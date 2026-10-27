# Discord Quests Complete Automation Bot - Railway Deploy

Bot de automação **COMPLETA** de Orbs/Quests Discord:
- 📹 **Videos** — Assiste automaticamente
- 🎮 **Games** — Joga automaticamente  
- ✅ **API Marking** — Marca como completo

Com proteção anti-detecção e browser headless Selenium.

## 🚀 Deploy no Railway

### 1. Preparação

```bash
# Clone ou crie repositório Git
git init
git add .
git commit -m "Initial commit"
```

### 2. Railway Setup

1. Acessa https://railway.app
2. Clica em "New Project"
3. Seleciona "Deploy from GitHub" ou "Deploy from Public Repo"
4. Conecta teu repositório GitHub

### 3. Variáveis de Ambiente (Railway Dashboard)

No Railway, vai em **Project → Variables** e adiciona:

```
DISCORD_TOKEN=seu_token_bot_aqui
```

**Pronto!** O bot extrai automaticamente o User ID do token.

### 4. Deploy

Railway detecta automaticamente Procfile e Dockerfile.
Clica "Deploy" e aguarda.

---

## 📋 Comandos do Bot (Slash Commands)

```
/orbs status    - Mostra status dos orbs (completados/falhados)
/orbs start     - Inicia automação de orbs
/orbs stop      - Para a automação
/clear          - Limpa histórico de orbs completados
```

## 🎯 Funcionalidades

**Automação de Quests:**
- 📹 **Video Watching** — Abre videos, simula visualização por X segundos
- 🎮 **Game Playing** — Abre games Discord, simula clicks/input aleatório
- ✅ **API Marking** — Completa quests após automação

**Proteções Anti-Detecção:**
- ✅ Delays aleatórios 30-90s entre ações
- ✅ Rate limiting: 2 requests/minuto
- ✅ Processamento de 1-2 quests por ciclo (5 minutos)
- ✅ Browser headless (não mostra janela)
- ✅ User-Agent humano (rotatório)
- ✅ Desativa detecção de automation (webdriver flag)
- ✅ Mouse/scroll aleatório (simulate humanlike behavior)
- ✅ Input aleatório em games (clicks, keys)

## 🎯 Exemplo de Uso

1. `/orbs start` → Inicia automação
2. Bot detecta tipo de quest (video/game/standard)
3. Para **videos**: abre, assiste por 15-30s (simula visualização)
4. Para **games**: abre, clica/interage por 30-50s (simula gameplay)
5. Marca como completo via Discord API
6. Aguarda 5 minutos, repete com próximos 1-2 quests
7. `/orbs status` → Mostra stats (videos, games, total)
8. `/clear` → Limpa histórico

## 📁 Estrutura

```
.
├── bot_complete.py          (bot principal - complete automation)
├── browser_handler.py       (Selenium browser controller)
├── requirements.txt         (dependências Python + Selenium)
├── Procfile                 (instrução para Railway)
├── Dockerfile               (container com Chrome + deps)
├── railway.json             (config Railway)
├── .env.example             (template variáveis)
├── .gitignore               (segurança Git)
├── orbs_progress.json       (tracking de quests - auto-created)
└── README.md                (este arquivo)
```

## 🔬 Como Funciona

### Video Quests
1. Bot abre URL do video em Chrome headless
2. Aguarda carregamento (anti-bot wait)
3. Simula comportamento humano:
   - Scroll aleatório
   - Espera aleatória (5-20s extra)
   - Detecção de player e timing real
4. Marca como completado na API Discord

### Game Quests
1. Bot abre URL do game em Chrome
2. Detecta iframes do game
3. Simula input humano:
   - Clicks aleatórios (x,y)
   - KeyPress eventos (arrows, space)
   - Intervalo aleatório entre inputs
4. Aguarda 30-50s de "gameplay"
5. Marca como completo

### API Marking
- Após automação bem-sucedida, marca quest em 100% completado
- Rate limiting para evitar blocks
- Retry automático em falhas temporárias

## 🔑 Obter Token Discord

1. https://discord.com/developers/applications
2. New Application → Name your app
3. Bot section → Add Bot
4. TOKEN → Copy (cole em Railway Variables)

**User ID é extraído automaticamente do token.**

---

## 🛡️ Segurança

- **Nunca** faz push de .env
- Bot roda em background (worker dyno)
- Dados persistem em missions.json
- Railway oferece 500 horas/mês free

## 📊 Monitoramento

Acessa Railway Dashboard para ver logs em tempo real.

## 📊 Monitoramento em Tempo Real

No Railway Dashboard → **Deployments** → **View logs**

Procura por:
```
✅ Bot conectado
📋 slash commands sincronizados
✅ Browser inicializado
🔄 Ciclo de automação iniciado
📋 Total de quests encontrados: X
🎯 Processando quest
✅ Quest completada
```

Se não aparecer "Ciclo de automação", `/orbs start` não funcionou.

## 🔧 Troubleshooting

**"Automação já está rodando" mas nada acontece** → Browser falhou silenciosamente
- Railway Dockerfile instala automaticamente
- Local: `pip install selenium webdriver-manager`

**"Video/Game não completa"** → URL inválida ou conteúdo bloqueado
- Verifica quest URL na resposta API
- Discord pode bloquear bots em certos games
- Logs mostram detalhes do erro

**"Rate limited"** → Muitas requisições rápido
- Aumenta MIN_DELAY/MAX_DELAY no código
- Diminui quests por ciclo (de 2 para 1)

**Bot crashes** → Check logs em Railway
- Console → View logs
- Procura "Error" ou "Exception"
- Token inválido é erro comum

---

**Deployed and delivering.**
