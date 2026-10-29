#!/usr/bin/env node
/**
 * 🌐 Impulsos.fun Web Scraper
 * Navega impulsos.fun, completa quests automaticamente
 * Conecta ao backend via REST API + WebSocket
 */

const puppeteer = require('puppeteer');
const axios = require('axios');
const io = require('socket.io-client');
const fs = require('fs').promises;
const path = require('path');
const log = console.log;

// Config
const IMPULSOS_URL = 'https://impulsos.fun';
const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:5000';
const LOG_DIR = './logs';

// Logger
const logger = {
  info: (msg) => log(`[INFO] ${new Date().toISOString()} - ${msg}`),
  error: (msg) => log(`[ERROR] ${new Date().toISOString()} - ${msg}`),
  quest: (token, type, status) => log(`[QUEST] ${token.slice(0,10)}*** - ${type.toUpperCase()} - ${status}`),
  debug: (msg) => process.env.DEBUG && log(`[DEBUG] ${msg}`)
};

// ===== SOCKET CLIENT =====
class BackendClient {
  constructor(backendUrl) {
    this.url = backendUrl;
    this.socket = null;
    this.connected = false;
  }

  async connect() {
    return new Promise((resolve) => {
      this.socket = io(this.url, {
        reconnection: true,
        reconnectionDelay: 1000,
        reconnectionDelayMax: 5000,
        reconnectionAttempts: Infinity
      });

      this.socket.on('connect', () => {
        this.connected = true;
        logger.info(`✅ Conectado ao backend em ${this.url}`);
        resolve(true);
      });

      this.socket.on('disconnect', () => {
        this.connected = false;
        logger.error('❌ Desconectado do backend');
      });

      this.socket.on('error', (err) => {
        logger.error(`Socket error: ${err}`);
      });
    });
  }

  async emit(event, data) {
    if (this.connected) {
      this.socket.emit(event, data);
    }
  }

  on(event, callback) {
    if (this.socket) {
      this.socket.on(event, callback);
    }
  }
}

// ===== WEB SCRAPER =====
class ImpulsossScraper {
  constructor(backendClient) {
    this.client = backendClient;
    this.browser = null;
    this.page = null;
    this.activeTokens = [];
  }

  async init() {
    try {
      this.browser = await puppeteer.launch({
        headless: 'new',
        args: [
          '--no-sandbox',
          '--disable-setuid-sandbox',
          '--disable-dev-shm-usage',
          '--disable-gpu',
          '--disable-web-resources',
          '--hide-scrollbars'
        ]
      });

      this.page = await this.browser.newPage();
      
      // Anti-detection
      await this.page.setUserAgent(
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
      );
      
      await this.page.evaluateOnNewDocument(() => {
        Object.defineProperty(navigator, 'webdriver', {
          get: () => false,
        });
      });

      logger.info('✅ Puppeteer inicializado');
      return true;
    } catch (err) {
      logger.error(`Erro inicializando Puppeteer: ${err}`);
      return false;
    }
  }

  async navigateToQuests(token) {
    try {
      logger.quest(token, 'nav', 'Abrindo impulsos.fun/quests');
      
      await this.page.goto(`${IMPULSOS_URL}/quests`, {
        waitUntil: 'networkidle2',
        timeout: 30000
      });

      // Aguarda carregamento de quests
      await this.page.waitForSelector('[data-quest-type]', { timeout: 10000 })
        .catch(() => logger.debug('Quest selector não encontrado imediatamente'));

      return true;
    } catch (err) {
      logger.error(`Erro navegando para quests: ${err}`);
      return false;
    }
  }

  async detectQuestType() {
    try {
      const questType = await this.page.evaluate(() => {
        // Detecta tipo de quest no DOM
        const videoElem = document.querySelector('video, iframe[src*="youtube"], [class*="video"]');
        if (videoElem) return 'video';

        const gameElem = document.querySelector('canvas, [class*="game"], [class*="play"]');
        if (gameElem) return 'game';

        const surveyElem = document.querySelector('input[type="checkbox"], input[type="radio"], select');
        if (surveyElem) return 'survey';

        return 'unknown';
      });

      logger.debug(`Quest detectada: ${questType}`);
      return questType;
    } catch (err) {
      logger.error(`Erro detectando quest: ${err}`);
      return 'unknown';
    }
  }

  async automateVideo() {
    try {
      logger.quest('', 'video', 'Iniciando automação de vídeo');

      // Aguarda video player
      await this.page.waitForSelector('video, iframe', { timeout: 10000 })
        .catch(() => null);

      // Simula assistência (25 segundos)
      for (let i = 0; i < 5; i++) {
        await this.page.waitForTimeout(5000);
        logger.debug(`Video: ${i * 5}s/25s`);
      }

      // Procura botão "Concluído" ou "Próximo"
      await this.page.click('[class*="complete"], [class*="next"], button:contains("Próximo")')
        .catch(() => logger.debug('Botão concluído não clicado automaticamente'));

      logger.quest('', 'video', '✅ Completo');
      return true;
    } catch (err) {
      logger.error(`Erro automando video: ${err}`);
      return false;
    }
  }

  async automateGame() {
    try {
      logger.quest('', 'game', 'Iniciando automação de game');

      // Aguarda canvas ou game container
      await this.page.waitForSelector('canvas, [class*="game"]', { timeout: 10000 })
        .catch(() => null);

      // Simula gameplay (40 segundos com clicks aleatórios)
      for (let i = 0; i < 8; i++) {
        const x = Math.floor(Math.random() * 800) + 100;
        const y = Math.floor(Math.random() * 600) + 100;

        await this.page.mouse.click(x, y);
        logger.debug(`Game click: (${x}, ${y})`);

        await this.page.waitForTimeout(5000);
      }

      logger.quest('', 'game', '✅ Completo');
      return true;
    } catch (err) {
      logger.error(`Erro automando game: ${err}`);
      return false;
    }
  }

  async automateSurvey() {
    try {
      logger.quest('', 'survey', 'Iniciando automação de survey');

      // Encontra todos checkboxes/radio buttons
      const inputs = await this.page.$$('input[type="checkbox"], input[type="radio"]');
      logger.debug(`Survey: encontradas ${inputs.length} opções`);

      // Marca 2-3 aleatórias
      const numToSelect = Math.min(3, Math.max(2, inputs.length));
      for (let i = 0; i < numToSelect; i++) {
        const randomIndex = Math.floor(Math.random() * inputs.length);
        await inputs[randomIndex].click();
        logger.debug(`Survey: selecionada opção ${i + 1}/${numToSelect}`);
        await this.page.waitForTimeout(1000);
      }

      // Procura botão submit
      const submitBtn = await this.page.$('button[type="submit"], [class*="submit"], [class*="enviar"]');
      if (submitBtn) {
        await submitBtn.click();
        logger.debug('Survey: formulário enviado');
      }

      await this.page.waitForTimeout(2000);
      logger.quest('', 'survey', '✅ Completo');
      return true;
    } catch (err) {
      logger.error(`Erro automando survey: ${err}`);
      return false;
    }
  }

  async processQuest() {
    try {
      const questType = await this.detectQuestType();

      let success = false;
      switch (questType) {
        case 'video':
          success = await this.automateVideo();
          break;
        case 'game':
          success = await this.automateGame();
          break;
        case 'survey':
          success = await this.automateSurvey();
          break;
        default:
          logger.error(`Quest type desconhecido: ${questType}`);
          return false;
      }

      // Notifica backend
      if (success) {
        await this.client.emit('quest_completed', {
          source: 'scraper',
          questType: questType,
          timestamp: new Date().toISOString()
        });
      }

      return success;
    } catch (err) {
      logger.error(`Erro processando quest: ${err}`);
      return false;
    }
  }

  async runCycle(token) {
    try {
      logger.info(`\n🔄 [CICLO] Processando token: ${token.slice(0, 10)}***`);

      // Navega para quests
      const navigated = await this.navigateToQuests(token);
      if (!navigated) {
        await this.client.emit('quest_failed', {
          source: 'scraper',
          token: token,
          reason: 'Falha ao navegar para quests'
        });
        return false;
      }

      // Aguarda carregamento de quest (random 2-5s)
      await this.page.waitForTimeout(Math.random() * 3000 + 2000);

      // Processa quest
      const success = await this.processQuest();

      // Delay antes da próxima (30-90s)
      const delay = Math.random() * 60000 + 30000;
      logger.info(`⏳ Aguardando ${Math.floor(delay / 1000)}s até próxima quest`);

      return success;
    } catch (err) {
      logger.error(`Erro no ciclo: ${err}`);
      return false;
    }
  }

  async startLoop(token) {
    if (!this.activeTokens.includes(token)) {
      this.activeTokens.push(token);
      logger.info(`✅ Token adicionado ao loop: ${token.slice(0, 10)}***`);
    }

    // Loop infinito
    let cycleCount = 0;
    while (this.activeTokens.includes(token)) {
      cycleCount++;
      logger.info(`\n[CICLO ${cycleCount}] Iniciando...`);

      await this.runCycle(token);

      // Espera antes de próximo ciclo (5 minutos)
      await this.page.waitForTimeout(300000);
    }
  }

  async stop() {
    if (this.browser) {
      await this.browser.close();
      logger.info('✅ Browser fechado');
    }
  }
}

// ===== MAIN =====
async function main() {
  // Cria diretório de logs
  try {
    await fs.mkdir(LOG_DIR, { recursive: true });
  } catch (err) {
    logger.debug(`Logs dir: ${err.message}`);
  }

  // Inicializa cliente
  const client = new BackendClient(BACKEND_URL);
  await client.connect();

  // Inicializa scraper
  const scraper = new ImpulsossScraper(client);
  const initialized = await scraper.init();

  if (!initialized) {
    logger.error('Falha ao inicializar scraper');
    process.exit(1);
  }

  // Listeners para eventos do backend
  client.on('start_scraper', async (data) => {
    const token = data.token;
    logger.info(`📢 Backend emitiu start_scraper para ${token.slice(0, 10)}***`);
    
    // Inicia em background
    scraper.startLoop(token).catch(err => {
      logger.error(`Erro no loop do scraper: ${err}`);
    });
  });

  client.on('stop_scraper', (data) => {
    const token = data.token;
    scraper.activeTokens = scraper.activeTokens.filter(t => t !== token);
    logger.info(`⏸️ Scraper parado para ${token.slice(0, 10)}***`);
  });

  logger.info('🎯 Scraper aguardando comandos do backend...');

  // Graceful shutdown
  process.on('SIGINT', async () => {
    logger.info('\n🛑 Encerrando scraper...');
    await scraper.stop();
    process.exit(0);
  });
}

main().catch(err => {
  logger.error(`Erro fatal: ${err}`);
  process.exit(1);
});
