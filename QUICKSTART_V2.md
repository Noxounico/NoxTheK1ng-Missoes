# 🚀 Impulsos.Fun Auto Bot — QUICKSTART V2

## ✨ Novo: Automação Completa de Missões

O bot agora **não apenas preenche o formulário** — **automatiza a missão inteira**:

### 5 STEPS no Ciclo Automático:

```
[STEP 1] 🌐 Abre impulsos.fun/quests
         → Chrome headless, anti-detection

[STEP 2] 📝 Preenche formulário
         → Token aleatório de tokens.json
         → Verifica se preenchido

[STEP 3] 🎯 Seleciona "1 Quest Aleatória (Grátis)"
         → Procura e clica botão

[STEP 4] 🤖 DETECTA E AUTOMATIZA QUEST
         ├─ 📹 VIDEO → Assiste automaticamente por 25s
         ├─ 🎮 GAME → Simula gameplay com clicks aleatórios por 40s
         ├─ ✅ SURVEY → Marca opções e clica submit
         ├─ 🔐 CAPTCHA → Aguarda manual (não suporta automation)
         └─ 🔹 OUTRO → Aguarda conclusão automática

[STEP 5] ⏳ Aguarda conclusão final
         → Procura sinais de sucesso (botão "Próximo", texto "Completo", etc)
         → Clica botão "Próximo" automaticamente se aparecer
         → Timeout: 15 min

[REPEAT] 🔄 Aguarda 30-90s aleatórios
         → Volta ao STEP 1
```

---

## 🎯 Tipos de Quest Automatizados

### 📹 VIDEO
```
✓ Detecta elemento <video> ou <iframe>
✓ Deixa vídeo reproduzir naturalmente
✓ Simula scroll humano
✓ Aguarda 25 segundos
✓ Pronto para continuar
```

### 🎮 GAME
```
✓ Procura botão "Play" / "Jogar" / "Iniciar Jogo"
✓ Clica para iniciar jogo
✓ Simula 40 segundos de gameplay:
  - Clicks aleatórios na tela
  - Coordenadas X/Y aleatórias
  - Logs a cada 5s
✓ Pronto para continuar
```

### ✅ SURVEY
```
✓ Detecta checkboxes e radio buttons
✓ Marca 2-3 opções aleatórias
✓ Procura botão "Enviar" / "Submit" / "Próximo"
✓ Clica botão automaticamente
✓ Pronto para continuar
```

### 🔐 CAPTCHA
```
⚠️ Não automatizado (requer manual solving)
✓ Bot detecta CAPTCHA e aguarda
✓ Deixa você resolver
✓ Continua automaticamente após conclusão
```

---

## 📊 Log de Automação

Cada ciclo agora mostra:

```
📋 [CICLO #42]
   ✓ Formulário preenchido
   ✓ Quest iniciada

[STEP 4] 🤖 Detectando e automatizando quest...
   → Tipo: 📹 VIDEO
   ✓ Vídeo encontrado
   ⏳ Assistindo vídeo por 25s...
      [0s] Assistindo...
      [5s] Assistindo...
      [10s] Assistindo...
      [15s] Assistindo...
      [20s] Assistindo...
   ✓ Vídeo concluído

[STEP 5] ⏳ Aguardando conclusão final...
   ✓ Quest detectada como concluída!

✅ QUEST COMPLETADA COM SUCESSO!
   Completadas: 42 | Tempo total: 2h 15m
```

---

## 🚀 Setup (2 passos)

### 1️⃣ Prepare tokens.json
```bash
cd /home/claude/impulsos-bot
```

**tokens.json:**
```json
["token1", "token2", "token3"]
```

Obter tokens:
1. Vá para impulsos.fun/quests
2. F12 → Console
3. `localStorage.getItem('auth_token')` ou `sessionStorage.getItem('token')`
4. Copie para `tokens.json`

### 2️⃣ Run Bot
```bash
python3 impulsos_auto_bot.py
```

**Output esperado:**
```
✅ Bot inicializado
🌐 Abrindo impulsos.fun/quests...
📝 [CICLO #1] Preenchendo formulário...
✓ Token: token1
✓ Quest iniciada
[STEP 4] 🤖 Detectando e automatizando quest...
   → Tipo: 📹 VIDEO
   ✓ Vídeo concluído
[STEP 5] ⏳ Aguardando conclusão final...
   ✓ Quest detectada como concluída!
✅ QUEST COMPLETADA COM SUCESSO!
```

---

## 🐳 Docker Deploy

```bash
cd /home/claude/impulsos-bot

# Build
docker build -t impulsos-bot .

# Run
docker run -d \
  -v $(pwd)/tokens.json:/app/tokens.json \
  -v $(pwd)/logs:/app/logs \
  impulsos-bot

# Logs
docker logs -f <container-id>
```

---

## ⚙️ Config

Edite `impulsos_auto_bot.py`:

```python
# Line ~420
DELAY_BETWEEN_CYCLES = random.randint(30, 90)  # segundos entre ciclos
VIDEO_WATCH_TIME = 25  # segundos para assistir vídeo
GAME_PLAY_TIME = 40    # segundos para simular gameplay
QUEST_TIMEOUT = 900    # 15 minutos max por quest
```

---

## 🔧 Troubleshooting

### ❌ "Vídeo não completou"
- Site pode ter anti-bot detection
- Tente aumento `VIDEO_WATCH_TIME` para 40s
- Verifique se localStorage token é válido

### ❌ "Jogo click não funcionou"
- Elemento pode estar em iframe
- Bot tenta detectar automaticamente
- Se não funcionar, adicione iframe handling:
  ```python
  self.driver.switch_to.frame(0)  # Muda para iframe
  # ... clicks
  self.driver.switch_to.default_content()  # Volta
  ```

### ❌ "Timeout após 15 minutos"
- Quest pode ser mais longa que esperado
- Aumente `QUEST_TIMEOUT` para 1800 (30 min)

### ⚠️ "Token inválido"
- Verifique se tokens em `tokens.json` ainda são válidos
- Tokens podem expirar após logout
- Obtenha novos tokens e atualize `tokens.json`

---

## 📈 Stats

Após cada ciclo completo:

```
📊 STATS ATUALIZADAS:
   Completadas: 42
   Tempo total: 2h 15m
   Tempo médio/quest: 3m 12s
   Taxa sucesso: 100%
```

Salvo em `bot_stats.json`:
```json
{
  "completed_count": 42,
  "total_time_seconds": 8100,
  "average_time_per_quest": 193,
  "start_time": "2026-10-28 22:30:45",
  "last_update": "2026-10-28 23:45:30"
}
```

---

## 🎯 Próximos Passos

- [x] Detectar tipo de quest
- [x] Automatizar vídeos
- [x] Automatizar games (clicks aleatórios)
- [x] Automatizar surveys
- [ ] CAPTCHA solving (requer API externa)
- [ ] Detecção de anti-bot (CloudFlare, etc)
- [ ] Proxy rotation (se necessário)

---

**Versão:** 2.0 (com automação de quests)
**Ultima atualização:** 2026-10-28
