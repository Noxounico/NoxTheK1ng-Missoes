# 🔗 Integração Completa — Bot + Scraper + Backend

Guia da arquitetura full-stack com **Discord Bot** + **Web Scraper** sincronizados.

## 🏗️ Arquitetura

```
┌──────────────────────────────────────────────────┐
│              FRONTEND (React)                     │
│         http://localhost:3000                     │
│  - Painel de controle visual                      │
│  - Stats em tempo real                            │
│  - Botões Start/Stop                              │
└──────────────────┬───────────────────────────────┘
                   │ WebSocket + HTTP
┌──────────────────▼───────────────────────────────┐
│              BACKEND (Node.js)                    │
│         http://localhost:5000                     │
│  - API REST (/api/tokens, /api/quests, etc)      │
│  - Socket.io server                              │
│  - MongoDB connection                            │
│  - Orchestração de Bot + Scraper                 │
└────┬──────────────────────────────────┬──────────┘
     │ Socket.emit                      │ Socket.emit
┌────▼────────────────┐    ┌──────────▼──────────┐
│  DISCORD BOT        │    │  WEB SCRAPER        │
│  (Python)           │    │  (Node.js)          │
│  Port: Hidden       │    │  Port: Hidden       │
│                     │    │                     │
│ - Processa quests   │    │ - Browser control   │
│   automáticamente   │    │ - Impulsos.fun nav  │
│ - Via Discord API   │    │ - Video/Game/Survey │
│ - Socket listener   │    │ - Puppeteer         │
│ - Slash commands    │    │ - Socket listener   │
└─────────────────────┘    └─────────────────────┘
```

---

## 🔄 Fluxo de Funcionamento

### **Passo 1: Setup Inicial**

```bash
# Terminal 1: Backend
docker run -d mongo
cd backend && npm install && npm start

# Terminal 2: Bot Discord
cd bot && pip install -r requirements.txt && python quest_bot.py

# Terminal 3: Scraper
cd scraper && npm install && npm start

# Terminal 4: Frontend
cd frontend && npm install && npm start
```

### **Passo 2: Usuario adiciona Token Discord**

```
Frontend (React)
├─ User cola token no textarea
├─ Clica "Adicionar"
└─ POST /api/tokens
   │
   ├─ Backend valida via Discord API
   ├─ Salva em MongoDB
   ├─ Emite WebSocket "token_added" → Frontend
   └─ Frontend mostra token na lista
```

### **Passo 3: Usuario Escolhe Modo de Automação**

#### **Opção A: Bot Discord (Recomendado para Discord)**
```
Frontend
├─ Botão "Iniciar Bot Discord"
└─ POST /api/bot/start?token=xxx
   │
   ├─ Backend emite Socket event "start_quests"
   ├─ Bot Python ouve o evento
   ├─ Bot começa loop a cada 5 min
   ├─ Bot completa quests via Discord API
   ├─ Bot emite "quest_completed" → Backend
   └─ Backend salva em MongoDB + atualiza Frontend
```

#### **Opção B: Web Scraper (Para impulsos.fun direto)**
```
Frontend
├─ Botão "Iniciar Scraper Web"
└─ POST /api/scraper/start?token=xxx
   │
   ├─ Backend emite Socket event "start_scraper"
   ├─ Scraper Node.js ouve o evento
   ├─ Scraper abre browser Puppeteer
   ├─ Scraper navega impulsos.fun
   ├─ Scraper automatiza video/game/survey
   ├─ Scraper emite "quest_completed" → Backend
   └─ Backend salva em MongoDB + atualiza Frontend
```

#### **Opção C: AMBOS Simultaneamente**
```
Frontend
├─ Botão "Iniciar Automação Total"
└─ POST /api/automação/start?token=xxx
   │
   ├─ Backend emite "start_quests" (Bot)
   ├─ Backend emite "start_scraper" (Scraper)
   │
   ├─→ Bot começa automação Discord
   └─→ Scraper começa automação Web
   
   Ambos correm em paralelo!
   ├─ Bot → quest_completed (1 quest/5 min)
   ├─ Scraper → quest_completed (1 quest/30-90 seg)
   └─ Frontend mostra stats combinadas
```

### **Passo 4: Monitorização em Tempo Real**

```
Backend (Socket.io)
├─ Recebe "quest_completed" do Bot
├─ Recebe "quest_completed" do Scraper
├─ Emite "stats_update" → Frontend
├─ Emite "log_entry" → Frontend
└─ Salva em MongoDB

Frontend (React)
├─ Atualiza counters em tempo real
├─ Mostra novo log
├─ Atualiza progress bar
└─ Mostra última quest completa
```

---

## 📡 API Endpoints

### **Bot Control**

```bash
# Iniciar Bot Discord
POST /api/bot/start
Body: { "token": "xxx" }
Response: { "success": true, "source": "discord_bot" }

# Parar Bot Discord
POST /api/bot/stop
Body: { "token": "xxx" }
Response: { "success": true }
```

### **Scraper Control**

```bash
# Iniciar Web Scraper
POST /api/scraper/start
Body: { "token": "xxx" }
Response: { "success": true, "source": "web_automation" }

# Parar Web Scraper
POST /api/scraper/stop
Body: { "token": "xxx" }
Response: { "success": true }
```

### **Automação Total**

```bash
# Iniciar AMBOS
POST /api/automacao/start
Body: { "token": "xxx" }
Response: { 
  "success": true, 
  "bot": "started",
  "scraper": "started"
}

# Status combinado
GET /api/automacao/status?token=xxx
Response: {
  "bot": { "active": true, "questsCompleted": 12 },
  "scraper": { "active": true, "questsCompleted": 34 }
}
```

---

## 🎮 Discord Slash Commands

### **Bot Commands**

```
/bot start <token>     → Inicia automação Discord Bot
/bot stop <token>      → Para automação Discord Bot
/bot status            → Mostra status do bot
```

### **Scraper Commands**

```
/scraper start <token>   → Inicia Web Scraper
/scraper stop <token>    → Para Web Scraper
/scraper logs            → Mostra logs do scraper
```

### **General**

```
/status                → Status do sistema
/stats                 → Stats combinadas (Bot + Scraper)
/automacao full <token> → Inicia AMBOS
```

---

## 🔀 Sincronização Backend

### **Schema Aprimorado**

```javascript
// Token Document
{
  _id: ObjectId,
  token: "discord_token",
  discordUser: "nome",
  createdAt: ISODate(),
  
  // Bot Stats
  bot: {
    active: false,
    questsCompleted: 42,
    questsFailed: 0,
    lastQuestTime: ISODate()
  },
  
  // Scraper Stats
  scraper: {
    active: false,
    questsCompleted: 128,
    questsFailed: 3,
    lastQuestTime: ISODate(),
    lastQuestType: "video"
  },
  
  // Combined
  totalQuestsCompleted: 170,
  totalQuestsFailed: 3,
  successRate: 0.9835
}
```

### **WebSocket Events**

```javascript
// Bot → Backend
socket.emit('quest_completed', {
  source: 'discord_bot',
  token: 'xxx',
  questType: 'video'
})

// Scraper → Backend
socket.emit('quest_completed', {
  source: 'web_scraper',
  token: 'xxx',
  questType: 'game'
})

// Backend → Frontend
io.emit('stats_update', {
  token: 'xxx',
  bot: { completed: 42, failed: 0 },
  scraper: { completed: 128, failed: 3 },
  total: 170
})
```

---

## 🔍 Diferenças Bot vs Scraper

| Aspecto | Bot Discord | Web Scraper |
|---------|-------------|-------------|
| **Tecnologia** | Python + discord.py | Node.js + Puppeteer |
| **Conexão** | Discord API | Browser HTTP |
| **Velocidade** | ~1 quest/5min | ~1 quest/30-90seg |
| **Fidelidade** | API oficial | Browser real (detecta como humano) |
| **Overhead** | Baixo | Alto (browser) |
| **Detecção** | Mais fácil detectar | Mais difícil (webdriver=false) |
| **Ideal Para** | Quests Discord diretas | Quests via impulsos.fun |
| **Falhas** | Rate limiting Discord | CAPTCHA, anti-bot |

---

## 🚀 Deploy Sincronizado

### **Docker Compose (Tudo Junto)**

```bash
docker-compose up -d
# Inicia:
# - MongoDB
# - Backend (Node.js)
# - Bot (Python)
# - Scraper (Node.js)
# - Frontend (React)
```

### **Railway (Production)**

```
1. Backend service → Node.js
2. Bot service → Python
3. Scraper service → Node.js
4. Frontend service → React
5. MongoDB (provisioned)

Env vars:
- DISCORD_TOKEN
- BACKEND_URL
- MONGODB_URI
```

---

## 📊 Monitoring

### **Backend Logs**

```bash
# Ver eventos em tempo real
docker logs -f impulsos-backend

# Padrões:
[Bot] quest_completed: token_xxx video
[Scraper] quest_completed: token_xxx game
[Socket] emit stats_update to 42 clients
```

### **Bot Logs**

```bash
docker logs -f impulsos-bot

# Padrões:
[QUEST] token_xxx - VIDEO - ✅ Completo
[SOCKET] quest_completed emitido
```

### **Scraper Logs**

```bash
docker logs -f impulsos-scraper

# Padrões:
[QUEST] token_xxx - VIDEO - Iniciando automação
[VIDEO] Vídeo assistido 25s
[SOCKET] quest_completed emitido
```

---

## 🎯 Casos de Uso

### **Caso 1: Apenas Discord Bot**
```
1. User clica "Bot Discord"
2. Backend emite "start_quests"
3. Bot completa quests Discord
4. Frontend mostra: "Quests completadas via Bot: 12"
```

### **Caso 2: Apenas Web Scraper**
```
1. User clica "Web Scraper"
2. Backend emite "start_scraper"
3. Scraper abre browser, navega impulsos.fun
4. Frontend mostra: "Quests completadas via Scraper: 34"
```

### **Caso 3: Automação Total (Recomendado)**
```
1. User clica "Iniciar Automação Total"
2. Backend emite AMBOS "start_quests" + "start_scraper"
3. Bot + Scraper correm em paralelo
4. Frontend mostra:
   - "Bot: 12 quests | Scraper: 34 quests | Total: 46"
   - "Taxa de sucesso: 95.7%"
   - "Última quest: Scraper - Game (há 2 min)"
```

---

## 🛠️ Troubleshooting

### ❌ "Bot não completa quests"
```
1. Verifica DISCORD_TOKEN em .env
2. Verifica se bot está no servidor
3. Verifica permissões do bot
4. Vê logs: docker logs impulsos-bot
```

### ❌ "Scraper não abre browser"
```
1. Verifica se Chromium está instalado
2. Verifica BACKEND_URL correto
3. Vê logs: docker logs impulsos-scraper
```

### ❌ "Frontend não atualiza stats"
```
1. Verifica conexão WebSocket
2. Verifica browser console (F12)
3. Verifica backend está rodando
4. Testa: curl http://localhost:5000
```

---

## 📈 Performance

**Com AMBOS rodando:**
- Bot: 1 quest a cada 5 min = 288 quests/dia
- Scraper: 1 quest a cada 1 min (avg) = 1440 quests/dia
- **Total: ~1728 quests/dia**

**Consumo de recursos:**
- Backend: ~100MB RAM
- Bot: ~50MB RAM
- Scraper: ~200MB RAM (browser)
- MongoDB: ~100MB
- **Total: ~450MB**

---

**Status:** ✅ Full Integration Complete  
**Pronto para:** Production  
**Documentado:** Sim  
**Testado:** Em Docker Compose  

---

Tá tudo pronto. Sincronizado. Rodando. 🎯
