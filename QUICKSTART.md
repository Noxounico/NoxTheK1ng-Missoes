# 🤖 Impulsos.Fun Auto Bot — QUICKSTART

## O Que Faz

Bot preenche **automaticamente** o formulário de impulsos.fun/quests:

```
1️⃣ Abre impulsos.fun/quests
2️⃣ Preenche tokens
3️⃣ Seleciona "Grátis" (1 Quest Aleatória)
4️⃣ Clica "Iniciar"
5️⃣ Aguarda conclusão
6️⃣ Repete infinitamente (com delays aleatórios)
```

---

## Setup (2 passos)

### 1️⃣ Adicione tokens em `tokens.json`

```json
[
  "token_impulsos_1",
  "token_impulsos_2",
  "token_impulsos_3"
]
```

### 2️⃣ Deploy no Railway

```bash
git push origin main
```

---

## Logging em Tempo Real

```
2026-10-27 14:32:10 ✓ Carregou 3 tokens
2026-10-27 14:32:11 🤖 Bot iniciado em MODO AUTÔNOMO

2026-10-27 14:32:20 ======================================================================
2026-10-27 14:32:20 [14:32:20] 🎯 Novo ciclo iniciado
2026-10-27 14:32:20 ======================================================================

2026-10-27 14:32:20 📲 Abrindo impulsos.fun/quests...
2026-10-27 14:32:23 ✓ Página carregada

2026-10-27 14:32:23 [STEP 1] 📝 Procurando campo de tokens...
2026-10-27 14:32:24    ✓ Campo de tokens encontrado
2026-10-27 14:32:24    📌 Token selecionado: abc123...xyz789
2026-10-27 14:32:24    ⌨️ Digitando token (95 caracteres)...
2026-10-27 14:32:25    ✓ Token preenchido com sucesso

2026-10-27 14:32:25 [STEP 2] 🎯 Procurando modo 'Grátis'...
2026-10-27 14:32:26    → Encontrados 5 botões
2026-10-27 14:32:26    ✓ Botão encontrado: 'Modo Gratuito'
2026-10-27 14:32:26    🖱️ Clicando botão 'Grátis'...

2026-10-27 14:32:28 [STEP 3] 🚀 Procurando botão 'Iniciar'...
2026-10-27 14:32:29    ✓ Botão encontrado: 'Iniciar Automação'
2026-10-27 14:32:29    🖱️ Clicando 'Iniciar'...

2026-10-27 14:32:32 ✅ CICLO INICIADO COM SUCESSO
2026-10-27 14:32:32    → Quest em execução...

2026-10-27 14:32:33 ⏳ Aguardando conclusão da quest (max 900s)...
2026-10-27 14:34:15 ✅ Quest parece ter sido concluída!

2026-10-27 14:34:15 📊 STATS: ✅ 1 | ❌ 0

2026-10-27 14:34:15 ⏳ Aguardando 67s antes próximo ciclo...
2026-10-27 14:35:22 ======================================================================
2026-10-27 14:35:22 [14:35:22] 🎯 Novo ciclo iniciado
[continua...]
```

---

## Comportamento

```
Loop infinito:
├─ [5-10 min] Quest em execução
├─ [30-90 seg] Delay aleatório
├─ [Repeat] Preenche novamente e inicia
└─ Continua 24/7
```

---

## Stats

A cada ciclo:

```
✅ Completadas: 10
❌ Falhadas: 0
```

---

## Parar Bot

```
CTRL+C no terminal (Railway: pause/stop)
```

---

## Troubleshooting

| Problema | Solução |
|----------|---------|
| "Sem tokens" | Adicione em tokens.json |
| "Campo não encontrado" | Website pode ter mudado (contate dev) |
| "Botão não encontrado" | Website pode ter mudado (contate dev) |
| Timeout quest | Aguarda até 15 min, continua no próximo ciclo |

---

## 🚀 Ready!

Bot começa automaticamente quando deploy. Sem comandos necessários.
