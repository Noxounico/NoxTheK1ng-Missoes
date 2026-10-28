# 🤖 Impulsos.Fun Auto Bot

## Resumo

Bot que **preenche automaticamente** o formulário de impulsos.fun/quests e deixa executando em loop infinito.

---

## Como Funciona

```
Cronograma:
00:00 → Deploy no Railway
00:05 → Bot inicia
00:10 → Preenche form, clica "Iniciar"
00:10-02:10 → Quest em execução (2min)
02:10-02:50 → Delay (30-90s aleatório)
02:50 → Novo ciclo [REPETE]
```

---

## Fluxo Automático

### STEP 1: Preencher Token

```
📲 Abre impulsos.fun/quests
🔍 Procura campo textarea para tokens
⌨️ Cola token aleatoriamente
✓ Verifica se foi preenchido
```

### STEP 2: Selecionar Modo Grátis

```
🎯 Procura botão "Grátis" ou "1 Quest Aleatória"
🖱️ Clica botão
```

### STEP 3: Iniciar Quest

```
🚀 Procura botão "Iniciar"
🖱️ Clica
✅ Quest em execução
```

### STEP 4: Aguardar Conclusão

```
⏳ Aguarda até 15 minutos
🔍 Verifica se "sucesso" ou "completo" na página
✅ Se completo: próximo ciclo
⚠️ Se timeout: pula mesmo assim
```

### STEP 5: Novo Ciclo

```
⏳ Aguarda 30-90 segundos (aleatório)
[VOLTA AO STEP 1]
```

---

## Ficheiros

```
impulsos_auto_bot.py     ← Bot principal (Selenium)
requirements.txt          ← Python deps (selenium)
Dockerfile               ← Railway config
tokens.json              ← Seus tokens (SECRET!)
QUICKSTART.md            ← Setup rápido
```

---

## Setup

### 1. Adicionar Tokens

```json
// tokens.json
[
  "token1",
  "token2",
  "token3"
]
```

### 2. Deploy

```bash
cd impulsos-bot
git add .
git commit -m "impulsos bot setup"
git push origin main
```

### 3. Railway

- New Project → Deploy from GitHub
- Selecionar repo
- Auto-detecta Dockerfile
- Clica Deploy

---

## Logging

```
✅ Carregou 3 tokens
🤖 Bot iniciado em MODO AUTÔNOMO
[14:32:20] 🎯 Novo ciclo iniciado
📲 Abrindo impulsos.fun/quests...
[STEP 1] 📝 Procurando campo de tokens...
   ✓ Campo de tokens encontrado
   📌 Token selecionado: abc123...
   ⌨️ Digitando token (95 caracteres)...
   ✓ Token preenchido com sucesso
[STEP 2] 🎯 Procurando modo 'Grátis'...
   ✓ Botão encontrado: 'Modo Gratuito'
[STEP 3] 🚀 Procurando botão 'Iniciar'...
   ✓ Botão encontrado: 'Iniciar Automação'
✅ CICLO INICIADO COM SUCESSO
⏳ Aguardando conclusão da quest (max 900s)...
✅ Quest parece ter sido concluída!
📊 STATS: ✅ 1 | ❌ 0
⏳ Aguardando 67s antes próximo ciclo...
```

---

## Diferença: Discord Bot vs Impulsos Bot

| Feature | Discord Bot | Impulsos Bot |
|---------|-------------|--------------|
| **Platform** | Discord API | Selenium Web Scraping |
| **What it does** | Completa quests Discord (videos/games) | Preenche form impulsos.fun |
| **Browser** | Sim (para videos/games) | Sim (Selenium) |
| **Tokens** | Discord tokens | Impulsos.fun tokens |
| **Loop** | `/orbs start` ou automático | Completamente automático |
| **Delay** | 5 minutos entre ciclos | 30-90s entre ciclos |
| **Quests** | Discord (Orbs) | Impulsos.fun (Grátis) |

---

## Comportamento Esperado

```
Hora 0:00 → Stats: 0 quests
Hora 0:30 → Stats: ~1-2 quests
Hora 1:00 → Stats: ~2-4 quests
Hora 2:00 → Stats: ~4-8 quests
Hora 4:00 → Stats: ~8-16 quests
Hora 8:00 → Stats: ~16-32 quests
Hora 24:00 → Stats: ~100-150 quests completados!
```

---

## Troubleshooting

### "Carregou 0 tokens"

```
✓ Verificar tokens.json
✓ Adicionar tokens válidos
✓ Fazer redeploy
```

### "Campo de tokens não encontrado"

```
✓ Página pode ter mudado
✓ Verificar impulsos.fun/quests manualmente
✓ Contatar dev para atualização
```

### "Botão 'Grátis' não encontrado"

```
✓ Layout pode ter mudado
✓ Pode estar "Modo Pago" em vez de "Modo Gratuito"
✓ Contatar dev para atualização
```

### Bot parou

```
✓ Railway → Logs: verificar erro
✓ CTRL+C pressionado
✓ Fazer redeploy
```

---

## Anti-Detection

Bot inclui:
- ✓ Headless Chrome (sem janela)
- ✓ User-Agent aleatório
- ✓ Delays aleatórios (30-90s)
- ✓ Selenium webdriver detection off
- ✓ Tokens selecionados aleatoriamente

---

## Railway Deploy

```bash
# Via GitHub (Recommended)
1. Git push
2. Railway auto-detecta Dockerfile
3. Deploy automático

# Via Railway CLI
1. railway login
2. railway up
```

---

## Ver Logs em Tempo Real

```bash
# Railway Dashboard
→ Logs tab

# Ou local
python3 impulsos_auto_bot.py
```

---

## Parar Bot

```
Railway: Pause / Stop deployment
Local: CTRL+C
```

---

## Reiniciar Bot

```
Railway: Re-deploy (git push)
Local: python3 impulsos_auto_bot.py
```

---

## ✨ Status

🚀 **PRONTO PARA DEPLOY**

- ✅ Bot Selenium completo
- ✅ Form filling automático
- ✅ Loop infinito
- ✅ Railway compatible
- ✅ Logging detalhado
- ✅ Anti-detection
- ✅ Error handling

**Próximos passos:**
1. Adicionar tokens em tokens.json
2. Deploy no Railway
3. Ver logs em tempo real
4. Stats vão crescendo a cada ciclo
