import React, { useState, useEffect } from 'react';
import io from 'socket.io-client';
import './App.css';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

function App() {
  const [tokens, setTokens] = useState([]);
  const [newToken, setNewToken] = useState('');
  const [stats, setStats] = useState(null);
  const [logs, setLogs] = useState([]);
  const [isRunning, setIsRunning] = useState(false);
  const [socket, setSocket] = useState(null);

  // WebSocket
  useEffect(() => {
    const newSocket = io(API_URL);
    setSocket(newSocket);

    newSocket.on('quest_update', (data) => {
      fetchStats();
      fetchLogs();
      
      if (data.type === 'completed') {
        showNotification(`✅ ${data.questType} completo!`, 'success');
      } else {
        showNotification(`❌ ${data.questType} falhou: ${data.reason}`, 'error');
      }
    });

    newSocket.on('token_added', (data) => {
      showNotification(`✅ Token adicionado: ${data.user}`, 'success');
      fetchTokens();
    });

    return () => newSocket.close();
  }, []);

  // Fetch functions
  const fetchTokens = async () => {
    try {
      const res = await fetch(`${API_URL}/api/tokens`);
      const data = await res.json();
      setTokens(data.tokens);
    } catch (err) {
      console.error('Erro fetching tokens:', err);
    }
  };

  const fetchStats = async () => {
    try {
      const res = await fetch(`${API_URL}/api/stats`);
      const data = await res.json();
      setStats(data);
    } catch (err) {
      console.error('Erro fetching stats:', err);
    }
  };

  const fetchLogs = async () => {
    try {
      const res = await fetch(`${API_URL}/api/logs`);
      const data = await res.json();
      setLogs(data.logs);
    } catch (err) {
      console.error('Erro fetching logs:', err);
    }
  };

  useEffect(() => {
    fetchTokens();
    fetchStats();
    fetchLogs();
    const interval = setInterval(() => {
      fetchStats();
      fetchLogs();
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  // Add token
  const handleAddToken = async (e) => {
    e.preventDefault();
    if (!newToken.trim()) return;

    try {
      const res = await fetch(`${API_URL}/api/tokens`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token: newToken })
      });

      if (res.ok) {
        setNewToken('');
        fetchTokens();
      } else {
        const err = await res.json();
        showNotification(`❌ ${err.error}`, 'error');
      }
    } catch (err) {
      showNotification(`❌ Erro: ${err.message}`, 'error');
    }
  };

  // Start quests
  const handleStartQuests = async () => {
    if (tokens.length === 0) {
      showNotification('❌ Nenhum token disponível', 'error');
      return;
    }

    setIsRunning(true);

    // Inicia automação para cada token
    for (const token of tokens) {
      try {
        await fetch(`${API_URL}/api/quests/start`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ token: token.token })
        });
      } catch (err) {
        console.error('Erro iniciando quests:', err);
      }
    }

    showNotification('🚀 Automação iniciada para todos os tokens!', 'success');
  };

  // Clear logs
  const handleClearLogs = async () => {
    try {
      await fetch(`${API_URL}/api/logs/clear`, { method: 'DELETE' });
      setLogs([]);
      showNotification('✅ Logs limpos', 'success');
    } catch (err) {
      showNotification(`❌ Erro: ${err.message}`, 'error');
    }
  };

  const showNotification = (msg, type) => {
    const div = document.createElement('div');
    div.className = `notification ${type}`;
    div.textContent = msg;
    document.body.appendChild(div);
    setTimeout(() => div.remove(), 3000);
  };

  return (
    <div className="container">
      {/* Header */}
      <header className="header">
        <div className="logo">
          <span className="icon">⚡</span>
          <h1>API Impulsos</h1>
          <p>Auto Quest - Clone</p>
        </div>
        <nav>
          <a href="#inicio">Início</a>
          <a href="#automacoes">Automações</a>
          <a href="#paineis">Painéis</a>
          <a href="#documentacao">Documentação</a>
        </nav>
      </header>

      {/* Main Content */}
      <main className="main">
        {/* Left Column - Tokens */}
        <div className="left-column">
          <div className="card">
            <h2>Modalidade de Uso</h2>
            <div className="mode-buttons">
              <button className="mode-btn active">Modo Gratuito</button>
              <button className="mode-btn">Modo Pago</button>
            </div>
          </div>

          <div className="card">
            <h2>Tokens</h2>
            <div className="token-input">
              <form onSubmit={handleAddToken}>
                <input
                  type="text"
                  placeholder="Cole o token aqui (1 por linha)"
                  value={newToken}
                  onChange={(e) => setNewToken(e.target.value)}
                />
                <button type="submit">Adicionar</button>
              </form>
            </div>

            <div className="token-stats">
              <span>{tokens.length} / ∞</span>
              <button className="clear-btn">Limpar</button>
            </div>

            <div className="token-list">
              {tokens.map((t, i) => (
                <div key={i} className="token-item">
                  <span className="token-user">{t.discordUser}</span>
                  <span className="token-status">{t.status}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="card">
            <h2>Modo de Conclusão</h2>
            <button className="quest-mode active">
              <span>🎯</span>
              <span>1 Quest Aleatória</span>
              <span className="badge">Grátis</span>
            </button>
            <button className="quest-mode">
              <span>⚡</span>
              <span>Todas as Quests</span>
              <span className="badge">Pago</span>
            </button>
          </div>
        </div>

        {/* Right Column - Stats */}
        <div className="right-column">
          <div className="card start-card">
            <div className="start-content">
              <span className="icon">🚀</span>
              <h3>Pronto para iniciar</h3>
              <p>Selecione o modo, cole os tokens e inicie a execução.</p>
              <span className={`status ${isRunning ? 'active' : 'inactive'}`}>
                {isRunning ? 'Em execução...' : 'Inativo'}
              </span>
            </div>

            <div className="progress-bar">
              <div className="progress" style={{ width: `${stats ? (stats.questsCompleted / (stats.questsCompleted + stats.questsFailed + 1) * 100) : 0}%` }}></div>
            </div>
            <span className="progress-text">0%</span>

            <div className="stats-grid">
              <div className="stat">
                <span className="stat-value">{stats?.tokens || 0}</span>
                <span className="stat-label">Tokens Prontos</span>
              </div>
              <div className="stat">
                <span className="stat-value">{stats?.questsCompleted || 0}</span>
                <span className="stat-label">Quests 100%</span>
              </div>
              <div className="stat">
                <span className="stat-value">{stats?.questsFailed || 0}</span>
                <span className="stat-label">Falhas</span>
              </div>
            </div>

            <button 
              className="start-btn"
              onClick={handleStartQuests}
              disabled={isRunning || tokens.length === 0}
            >
              {isRunning ? 'Executando...' : 'INICIAR QUESTS'}
            </button>
          </div>

          {/* Logs */}
          <div className="card logs-card">
            <div className="logs-header">
              <h3>📋 Log de Execução</h3>
              <button className="clear-logs-btn" onClick={handleClearLogs}>Limpar</button>
            </div>

            <div className="logs-container">
              {logs.length === 0 ? (
                <p className="no-logs">Aguardando início do Auto Quest...</p>
              ) : (
                logs.map((log, i) => (
                  <div key={i} className={`log-item ${log.status}`}>
                    <span className="log-time">
                      {new Date(log.timestamp).toLocaleTimeString('pt-PT')}
                    </span>
                    <span className="log-type">{log.questType}</span>
                    <span className="log-status">{log.status}</span>
                    <span className="log-details">{log.details}</span>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="footer">
        <div className="footer-content">
          <p>Impulsos Clone © 2026 | Todos os direitos reservados</p>
        </div>
      </footer>
    </div>
  );
}

export default App;
