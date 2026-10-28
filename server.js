const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const dotenv = require('dotenv');
const axios = require('axios');
const { Server } = require('socket.io');
const http = require('http');

dotenv.config();

const app = express();
const server = http.createServer(app);
const io = new Server(server, {
  cors: { origin: "*" }
});

// Middleware
app.use(express.json());
app.use(cors());

// MongoDB Connection
mongoose.connect(process.env.MONGODB_URI || 'mongodb://localhost:27017/impulsos-clone')
  .then(() => console.log('✅ MongoDB conectado'))
  .catch(err => console.error('❌ MongoDB erro:', err));

// ===== SCHEMAS =====
const tokenSchema = new mongoose.Schema({
  token: { type: String, required: true, unique: true },
  discordId: String,
  discordUser: String,
  createdAt: { type: Date, default: Date.now },
  questsCompleted: { type: Number, default: 0 },
  questsFailed: { type: Number, default: 0 },
  status: { type: String, default: 'active' }
});

const questLogSchema = new mongoose.Schema({
  token: String,
  questType: String, // video, game, survey
  status: String, // completed, failed
  timestamp: { type: Date, default: Date.now },
  details: String
});

const Token = mongoose.model('Token', tokenSchema);
const QuestLog = mongoose.model('QuestLog', questLogSchema);

// ===== API ENDPOINTS =====

// GET: Home
app.get('/', (req, res) => {
  res.json({ 
    name: 'Impulsos Clone API',
    version: '1.0.0',
    status: 'online'
  });
});

// POST: Add Token
app.post('/api/tokens', async (req, res) => {
  try {
    const { token } = req.body;
    
    if (!token) {
      return res.status(400).json({ error: 'Token é obrigatório' });
    }

    // Valida token Discord
    try {
      const response = await axios.get('https://discord.com/api/v10/users/@me', {
        headers: { 'Authorization': `Bot ${token}` }
      });
      
      const existingToken = await Token.findOne({ token });
      if (existingToken) {
        return res.status(400).json({ error: 'Token já existe' });
      }

      const newToken = new Token({
        token,
        discordId: response.data.id,
        discordUser: response.data.username
      });

      await newToken.save();

      io.emit('token_added', { 
        token: token.substring(0, 10) + '***',
        user: response.data.username
      });

      res.json({ 
        success: true, 
        message: 'Token adicionado',
        data: { discordUser: response.data.username }
      });
    } catch (discordErr) {
      return res.status(401).json({ error: 'Token Discord inválido' });
    }

  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// GET: All Tokens
app.get('/api/tokens', async (req, res) => {
  try {
    const tokens = await Token.find();
    res.json({ tokens });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// POST: Start Quests for Token
app.post('/api/quests/start', async (req, res) => {
  try {
    const { token } = req.body;

    if (!token) {
      return res.status(400).json({ error: 'Token é obrigatório' });
    }

    const existingToken = await Token.findOne({ token });
    if (!existingToken) {
      return res.status(404).json({ error: 'Token não encontrado' });
    }

    // Emite evento para bot completar quests
    io.emit('start_quests', { token });

    res.json({ 
      success: true, 
      message: 'Automação iniciada',
      data: { token: token.substring(0, 10) + '***' }
    });

  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// GET: Stats
app.get('/api/stats', async (req, res) => {
  try {
    const tokens = await Token.find();
    const logs = await QuestLog.find();

    const totalTokens = tokens.length;
    const totalQuestsCompleted = tokens.reduce((sum, t) => sum + t.questsCompleted, 0);
    const totalQuestsFailed = tokens.reduce((sum, t) => sum + t.questsFailed, 0);

    res.json({
      tokens: totalTokens,
      questsCompleted: totalQuestsCompleted,
      questsFailed: totalQuestsFailed,
      successRate: totalTokens > 0 ? ((totalQuestsCompleted / (totalQuestsCompleted + totalQuestsFailed)) * 100).toFixed(2) + '%' : '0%',
      tokensList: tokens.map(t => ({
        discordUser: t.discordUser,
        questsCompleted: t.questsCompleted,
        questsFailed: t.questsFailed,
        status: t.status
      }))
    });

  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// GET: Logs
app.get('/api/logs', async (req, res) => {
  try {
    const logs = await QuestLog.find().sort({ timestamp: -1 }).limit(100);
    res.json({ logs });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// DELETE: Clear Logs
app.delete('/api/logs/clear', async (req, res) => {
  try {
    await QuestLog.deleteMany({});
    io.emit('logs_cleared');
    res.json({ success: true, message: 'Logs limpos' });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// ===== WEBSOCKET =====
io.on('connection', (socket) => {
  console.log(`✅ Cliente conectado: ${socket.id}`);

  // Bot emite progresso
  socket.on('quest_completed', async (data) => {
    const { token, questType } = data;
    
    const tokenDoc = await Token.findOne({ token });
    if (tokenDoc) {
      tokenDoc.questsCompleted += 1;
      await tokenDoc.save();
    }

    const log = new QuestLog({
      token: token.substring(0, 10) + '***',
      questType,
      status: 'completed',
      details: `${questType} quest concluída`
    });
    await log.save();

    io.emit('quest_update', { 
      type: 'completed',
      questType,
      timestamp: new Date()
    });
  });

  socket.on('quest_failed', async (data) => {
    const { token, questType, reason } = data;
    
    const tokenDoc = await Token.findOne({ token });
    if (tokenDoc) {
      tokenDoc.questsFailed += 1;
      await tokenDoc.save();
    }

    const log = new QuestLog({
      token: token.substring(0, 10) + '***',
      questType,
      status: 'failed',
      details: reason || 'Falha desconhecida'
    });
    await log.save();

    io.emit('quest_update', { 
      type: 'failed',
      questType,
      reason,
      timestamp: new Date()
    });
  });

  socket.on('disconnect', () => {
    console.log(`❌ Cliente desconectado: ${socket.id}`);
  });
});

// ===== START SERVER =====
const PORT = process.env.PORT || 5000;
server.listen(PORT, () => {
  console.log(`🚀 Backend rodando em porta ${PORT}`);
});

module.exports = { app, io, Token, QuestLog };
