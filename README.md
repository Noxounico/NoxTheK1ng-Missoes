# Discord Mission Bot - Railway Deploy

Bot de automação de missões Discord com proteção contra detecção.

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

## 📋 Comandos do Bot

```
!adicionar <missão>     - Adiciona missão à fila
!status                 - Status das missões
!missoes                - Lista missões ativas
!limpar                 - Remove completadas
```

## 🔒 Proteções Anti-Detecção

- ✅ Delays aleatórios 45-180s entre actions
- ✅ Rate limiting: 2 requests/minuto
- ✅ Máximo 8 missões/hora
- ✅ Processamento de 1-2 missões por ciclo (10 minutos)
- ✅ Headers humanos
- ✅ Logging discreto

## 📁 Estrutura

```
.
├── bot_safe.py         (bot principal)
├── requirements.txt    (dependências)
├── Procfile           (instrução para Railway)
├── Dockerfile         (container config)
├── railway.json       (config Railway)
├── .env.example       (template variáveis)
├── .gitignore         (segurança Git)
└── README.md          (este arquivo)
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
