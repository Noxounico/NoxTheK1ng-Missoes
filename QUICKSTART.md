# 🚀 Discord Orbs Bot — Quickstart 5 Minutos

## 1️⃣ Obter Token Discord Bot

1. https://discord.com/developers/applications
2. **New Application** → nome do bot
3. **Bot** → **Add Bot**
4. **TOKEN** → **Copy**
5. **Guarda em lugar seguro**

## 2️⃣ Configurar Railway

1. https://railway.app
2. **New Project** → **Deploy from GitHub**
3. Conecta repositório (orbs-bot)
4. Railway auto-detecta Dockerfile
5. **Variables** → `DISCORD_TOKEN=teu_token`
6. **Deploy**

## 3️⃣ Configurar Tokens de Contas (Para Games)

Se quer que bot **preencha automaticamente** o modal "Configurar Missões (Orbs)":

```bash
# Edita tokens.json
cat > tokens.json << EOF
[
  "token_da_conta_1",
  "token_da_conta_2",
  "token_da_conta_3"
]
EOF

# Faz commit e push
git add tokens.json
git commit -m "Add account tokens"
git push
```

Railway redeploys automaticamente.

## 4️⃣ Usar Bot em Discord

```
/orbs status    → mostra stats
/orbs start     → inicia automação
/orbs stop      → para
/clear          → limpa histórico
```

## 🎮 Como Funciona com Games

**Cenário:**
1. Bot detecta quest tipo "GAME"
2. Abre game em Chrome headless
3. **Detecta modal "Configurar Missões (Orbs)"**
4. **Preenche automaticamente com token de tokens.json**
5. **Clica "Enviar"**
6. Aguarda resposta do servidor
7. Simula gameplay (clicks + inputs aleatórios por 30-50s)
8. Marca quest como 100% completo na API

## ⚠️ Cuidados

- **Nunca** faz push de .env com DISCORD_TOKEN real
- Railway Variables é seguro (usa .env internamente)
- Tokens em `tokens.json` são para contas secundárias (não é segredo)
- Se token é comprometido, remove de Railway redeploys

## 🔧 Troubleshooting

| Problema | Solução |
|----------|---------|
| Bot não responde a comandos | Verifica Railway logs (View logs) |
| Browser não inicia | Token inválido? Restart deployment |
| Game modal não preenche | Verifica se tokens.json existe e tem tokens válidos |
| Rate limited | Normal, bot aguarda 2req/min |

## 📊 Monitoramento

```bash
# Railway logs (real-time)
Railway Dashboard → Deployments → View logs

# Procura por:
✅ bot conectado
🎮 Quest tipo: GAME
🔧 Modal preenchido
✅ Quest completada
```

---

**Deployed and running. Check status in 5 minutes.**
