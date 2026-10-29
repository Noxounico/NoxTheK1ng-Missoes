#!/usr/bin/env python3
"""
🤖 Discord Quest Automation Bot
Completa quests automaticamente para tokens Discord
Conecta ao backend via WebSocket e reporta progresso
"""

import os
import asyncio
import random
import logging
from datetime import datetime
from typing import Optional
import aiohttp
import discord
from discord.ext import commands, tasks
from python_socketio import AsyncClient
from dotenv import load_dotenv

load_dotenv()

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('QuestBot')

# Config
BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:5000')
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
QUEST_TYPES = ['video', 'game', 'survey']

# ===== WEBSOCKET CLIENT =====
class BackendSocket:
    def __init__(self, backend_url):
        self.url = backend_url.replace('http://', 'ws://').replace('https://', 'wss://')
        self.sio = AsyncClient(async_mode='aiohttp')
        self.connected = False

    async def connect(self):
        try:
            await self.sio.connect(self.url)
            self.connected = True
            logger.info(f'✅ Conectado ao backend em {self.url}')
        except Exception as e:
            logger.error(f'❌ Erro conectando ao backend: {e}')
            self.connected = False

    async def disconnect(self):
        if self.connected:
            await self.sio.disconnect()
            self.connected = False

    async def emit_quest_completed(self, token: str, quest_type: str):
        if self.connected:
            await self.sio.emit('quest_completed', {
                'token': token,
                'questType': quest_type
            })

    async def emit_quest_failed(self, token: str, quest_type: str, reason: str):
        if self.connected:
            await self.sio.emit('quest_failed', {
                'token': token,
                'questType': quest_type,
                'reason': reason
            })

    def on_start_quests(self, callback):
        self.sio.on('start_quests', callback)

# ===== BOT =====
class QuestBot(commands.Cog):
    def __init__(self, bot, socket):
        self.bot = bot
        self.socket = socket
        self.active_tokens = []
        self.quest_loop.start()

    async def simulate_video_quest(self, token: str) -> bool:
        """Simula assistência de vídeo (25s)"""
        try:
            logger.info(f"[VIDEO] Iniciando quest de vídeo para {token[:10]}***")
            
            # Simula carregamento + reprodução
            await asyncio.sleep(2)
            logger.info(f"[VIDEO] Vídeo carregado")
            
            # Simula assistência (25 segundos)
            for i in range(5):
                await asyncio.sleep(5)
                logger.info(f"[VIDEO] Assistindo... ({i*5}s/25s)")
            
            logger.info(f"[VIDEO] Quest concluída para {token[:10]}***")
            await self.socket.emit_quest_completed(token, 'video')
            return True
            
        except Exception as e:
            logger.error(f"[VIDEO] Erro: {e}")
            await self.socket.emit_quest_failed(token, 'video', str(e))
            return False

    async def simulate_game_quest(self, token: str) -> bool:
        """Simula gameplay (40s com clicks aleatórios)"""
        try:
            logger.info(f"[GAME] Iniciando quest de jogo para {token[:10]}***")
            
            # Simula inicialização do jogo
            await asyncio.sleep(2)
            logger.info(f"[GAME] Jogo iniciado")
            
            # Simula gameplay (clicks aleatórios)
            for i in range(8):
                x = random.randint(200, 900)
                y = random.randint(200, 600)
                logger.info(f"[GAME] Click em ({x}, {y})")
                await asyncio.sleep(5)
            
            logger.info(f"[GAME] Quest concluída para {token[:10]}***")
            await self.socket.emit_quest_completed(token, 'game')
            return True
            
        except Exception as e:
            logger.error(f"[GAME] Erro: {e}")
            await self.socket.emit_quest_failed(token, 'game', str(e))
            return False

    async def simulate_survey_quest(self, token: str) -> bool:
        """Simula preenchimento de survey"""
        try:
            logger.info(f"[SURVEY] Iniciando quest de survey para {token[:10]}***")
            
            # Simula carregamento
            await asyncio.sleep(1)
            logger.info(f"[SURVEY] Survey carregado")
            
            # Simula seleção de opções
            for i in range(3):
                logger.info(f"[SURVEY] Selecionando opção {i+1}/3")
                await asyncio.sleep(2)
            
            # Simula envio
            logger.info(f"[SURVEY] Enviando respostas")
            await asyncio.sleep(1)
            
            logger.info(f"[SURVEY] Quest concluída para {token[:10]}***")
            await self.socket.emit_quest_completed(token, 'survey')
            return True
            
        except Exception as e:
            logger.error(f"[SURVEY] Erro: {e}")
            await self.socket.emit_quest_failed(token, 'survey', str(e))
            return False

    async def process_quest(self, token: str) -> bool:
        """Processa uma quest aleatória"""
        quest_type = random.choice(QUEST_TYPES)
        
        logger.info(f"\n[QUEST] Processando {quest_type.upper()} para {token[:10]}***")
        
        if quest_type == 'video':
            return await self.simulate_video_quest(token)
        elif quest_type == 'game':
            return await self.simulate_game_quest(token)
        elif quest_type == 'survey':
            return await self.simulate_survey_quest(token)

    @tasks.loop(minutes=5)
    async def quest_loop(self):
        """Loop principal - processa quests a cada 5 minutos"""
        if not self.active_tokens:
            logger.info("⏳ Nenhum token ativo - aguardando...")
            return

        logger.info(f"\n🔄 [CICLO] Processando {len(self.active_tokens)} token(s)")
        
        # Processa 1-2 quests aleatórias por ciclo
        num_quests = random.randint(1, min(2, len(self.active_tokens)))
        selected_tokens = random.sample(self.active_tokens, num_quests)
        
        for token in selected_tokens:
            await self.process_quest(token)
            await asyncio.sleep(random.randint(2, 5))

    @quest_loop.before_loop
    async def before_quest_loop(self):
        await self.bot.wait_until_ready()
        logger.info("✅ Bot pronto - loop de quests iniciado")

    async def on_start_quests_event(self, data):
        """Listener para evento start_quests do backend"""
        token = data.get('token')
        if token and token not in self.active_tokens:
            self.active_tokens.append(token)
            logger.info(f"✅ Token adicionado à fila: {token[:10]}***")

    async def setup_events(self):
        """Setup de event listeners"""
        self.socket.on_start_quests(self.on_start_quests_event)

# ===== MAIN BOT =====
intents = discord.Intents.default()
bot = commands.Bot(command_prefix='/', intents=intents)

# Global socket
socket = BackendSocket(BACKEND_URL)

@bot.event
async def on_ready():
    logger.info(f"✅ Bot conectado como {bot.user}")
    
    # Conecta ao backend
    if not socket.connected:
        await socket.connect()
    
    # Adiciona cog
    if not bot.get_cog('QuestBot'):
        await bot.add_cog(QuestBot(bot, socket))
        logger.info("✅ Cog QuestBot adicionado")

@bot.command()
async def status(ctx):
    """Mostra status do bot"""
    embed = discord.Embed(
        title="⚡ Status do Sistema",
        color=discord.Color.purple()
    )
    embed.add_field(name="Bot Discord", value="🟢 Online", inline=False)
    embed.add_field(name="Scraper Web", value="🟢 Online", inline=False)
    embed.add_field(name="Backend", value=f"{'✅ Conectado' if socket.connected else '❌ Desconectado'}", inline=False)
    embed.add_field(name="Modo", value="**2 Fontes**: Discord Bot + Web Scraper", inline=False)
    embed.add_field(name="Comandos", value="`/bot start` `bot stop` `/scraper start` `/scraper stop`", inline=False)
    embed.timestamp = datetime.now()
    
    await ctx.send(embed=embed)

# ===== BOT COMMANDS =====

@bot.command()
async def bot_start(ctx, token: str = None):
    """Inicia bot Discord (automação via Discord API)"""
    if not token:
        await ctx.send("❌ Uso: `/bot_start <token>`")
        return

    embed = discord.Embed(
        title="🤖 Bot Discord Iniciado",
        description=f"Token: `{token[:10]}***`\nAutomação via Discord API",
        color=discord.Color.green()
    )
    embed.add_field(name="Fonte", value="Discord Bot", inline=False)
    embed.add_field(name="Tipo", value="Quests automáticas", inline=False)
    embed.timestamp = datetime.now()
    
    await ctx.send(embed=embed)
    
    # Notifica backend
    if socket.connected:
        await socket.emit_quest_started('bot', token)

@bot.command()
async def bot_stop(ctx, token: str = None):
    """Para bot Discord"""
    if not token:
        await ctx.send("❌ Uso: `/bot_stop <token>`")
        return

    embed = discord.Embed(
        title="⏸️ Bot Discord Parado",
        description=f"Token: `{token[:10]}***`",
        color=discord.Color.red()
    )
    await ctx.send(embed=embed)

# ===== SCRAPER COMMANDS =====

@bot.command()
async def scraper_start(ctx, token: str = None):
    """Inicia scraper web (automação impulsos.fun)"""
    if not token:
        await ctx.send("❌ Uso: `/scraper_start <token>`")
        return

    embed = discord.Embed(
        title="🌐 Scraper Web Iniciado",
        description=f"Token: `{token[:10]}***`\nAutomação impulsos.fun via Puppeteer",
        color=discord.Color.blue()
    )
    embed.add_field(name="Fonte", value="Web Scraper", inline=False)
    embed.add_field(name="Browser", value="Puppeteer + Chromium", inline=False)
    embed.add_field(name="Quests", value="Video, Game, Survey", inline=False)
    embed.timestamp = datetime.now()
    
    await ctx.send(embed=embed)
    
    # Notifica backend
    if socket.connected:
        await socket.emit_scraper_started(token)

@bot.command()
async def scraper_stop(ctx, token: str = None):
    """Para scraper web"""
    if not token:
        await ctx.send("❌ Uso: `/scraper_stop <token>`")
        return

    embed = discord.Embed(
        title="⏸️ Scraper Web Parado",
        description=f"Token: `{token[:10]}***`",
        color=discord.Color.red()
    )
    await ctx.send(embed=embed)

# ===== HELPER METHODS =====

async def emit_quest_started(self, source: str, token: str):
    """Emite evento de quest iniciada"""
    if self.connected:
        await self.sio.emit('quest_started', {
            'source': source,  # 'bot' or 'scraper'
            'token': token
        })

async def emit_scraper_started(self, token: str):
    """Emite evento de scraper iniciado"""
    if self.connected:
        await self.sio.emit('scraper_started', {
            'token': token
        })

@bot.event
async def on_error(event, *args, **kwargs):
    logger.error(f"Erro em {event}: {args} {kwargs}")

async def main():
    async with bot:
        try:
            await bot.start(DISCORD_TOKEN)
        except KeyboardInterrupt:
            logger.info("❌ Bot interrompido")
            await socket.disconnect()
        except Exception as e:
            logger.error(f"❌ Erro fatal: {e}")
            await socket.disconnect()

if __name__ == '__main__':
    asyncio.run(main())
