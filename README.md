# Discord Orbs Automation Bot - Railway Deploy

Bot de automação de **Orbs/Quests** do Discord com proteção contra detecção.

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

## 🔒 Proteções Anti-Detecção

- ✅ Delays aleatórios 30-90s entre orbs
- ✅ Rate limiting: 2 requests/minuto
- ✅ Processamento de 1-2 orbs por ciclo (5 minutos)
- ✅ Headers humanos (User-Agent Mozilla)
- ✅ Logging discreto
- ✅ Staggered execution (não bombardeia API)

## 🎯 Exemplo de Uso

1. `/orbs status` → Mostra orbs completados até agora
2. `/orbs start` → Bot começa a completar orbs automaticamente
3. Bot processa 1-2 orbs a cada 5 minutos (silenciosamente)
4. `/orbs status` → Acompanha progresso real
5. `/clear` → Limpa histórico quando quiser

## 📁 Estrutura

```
.
├── bot_safe.py              (bot principal - orbs automation)
├── requirements.txt         (dependências)
├── Procfile                 (instrução para Railway)
├── Dockerfile               (container config)
├── railway.json             (config Railway)
├── .env.example             (template variáveis)
├── .gitignore               (segurança Git)
├── orbs_progress.json       (tracking de orbs - auto-created)
└── README.md                (este arquivo)
```

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

---

**Deployed and delivering.**
