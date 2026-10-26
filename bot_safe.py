import discord
from discord.ext import commands, tasks
import asyncio
import json
import random
import base64
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import aiohttp

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

MIN_DELAY = 30
MAX_DELAY = 90
ORBS_API = "https://discord.com/api/v10/users/@me/quests"

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

ORBS_FILE = "orbs_progress.json"
request_tracker = {"last_request": datetime.now(), "count_this_minute": 0}

def load_orbs_data():
    try:
        with open(ORBS_FILE, 'r') as f:
            return json.load(f)
    except:
        return {"completed": [], "failed": [], "last_sync": None}

def save_orbs_data(data):
    with open(ORBS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def get_human_delay():
    return random.uniform(MIN_DELAY, MAX_DELAY)

def get_auth_token():
    """Extrai token de DISCORD_TOKEN (format: bot-token)"""
    return DISCORD_TOKEN.split('.')[-1] if '.' in DISCORD_TOKEN else DISCORD_TOKEN

async def fetch_orbs_quests(session):
    """Busca quests/orbs disponiveis"""
    headers = {
        "Authorization": DISCORD_TOKEN,
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
    }
    
    try:
        async with session.get(ORBS_API, headers=headers, timeout=15) as resp:
            if resp.status == 200:
                return await resp.json()
            return None
    except Exception as e:
        print(f"❌ Erro fetching orbs: {e}")
        return None

async def complete_orb_quest(session, quest_id):
    """Marca quest como completada"""
    headers = {
        "Authorization": DISCORD_TOKEN,
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
    }
    
    url = f"{ORBS_API}/{quest_id}/progress"
    
    try:
        async with session.post(url, headers=headers, json={"progress": 100}, timeout=15) as resp:
            return resp.status in [200, 201]
    except Exception as e:
        print(f"❌ Erro completing quest {quest_id}: {e}")
        return False

async def respect_rate_limit():
    global request_tracker
    
    now = datetime.now()
    if (now - request_tracker["last_request"]).seconds > 60:
        request_tracker["count_this_minute"] = 0
    
    if request_tracker["count_this_minute"] >= REQUESTS_PER_MINUTE:
        wait_time = 60 - (now - request_tracker["last_request"]).seconds
        if wait_time > 0:
            await asyncio.sleep(wait_time)
            request_tracker["count_this_minute"] = 0
    
    request_tracker["count_this_minute"] += 1
    request_tracker["last_request"] = now

@bot.event
async def on_ready():
    print(f'✅ {bot.user} conectado')
    print(f'🔒 Anti-detection ativo: delays {MIN_DELAY}-{MAX_DELAY}s')
    print(f'👤 User ID: {bot.user.id}')
    if not mission_automation.is_running():
        mission_automation.start()

@bot.command(name='orbs')
async def orbs_command(ctx, action="status"):
    """Controla automação de orbs: !orbs status, !orbs start, !orbs stop"""
    await respect_rate_limit()
    
    if action == "status":
        data = load_orbs_data()
        embed = discord.Embed(title="🔮 Orbs Status", color=discord.Color.purple())
        embed.add_field(name="Completadas", value=len(data["completed"]), inline=True)
        embed.add_field(name="Falhadas", value=len(data["failed"]), inline=True)
        embed.add_field(name="Última sync", value=data["last_sync"] or "Nunca", inline=False)
        await ctx.send(embed=embed)
    
    elif action == "start":
        if orbs_loop.is_running():
            await ctx.send("⚠️ Automação já está rodando")
        else:
            orbs_loop.start()
            await ctx.send("✅ Automação de orbs iniciada")
    
    elif action == "stop":
        if orbs_loop.is_running():
            orbs_loop.stop()
            await ctx.send("⏹️ Automação parada")
        else:
            await ctx.send("⚠️ Automação não está rodando")
    
    else:
        await ctx.send("Uso: `!orbs status` | `!orbs start` | `!orbs stop`")

@bot.command(name='clear')
async def clear_orbs_data(ctx):
    """Limpa histórico de orbs completados"""
    data = load_orbs_data()
    count = len(data["completed"])
    data["completed"] = []
    data["failed"] = []
    save_orbs_data(data)
    await ctx.send(f"✅ {count} orbs removidos do histórico")

@tasks.loop(minutes=5)
async def orbs_loop():
    """Automação de orbs - fetch e completa quests"""
    data = load_orbs_data()
    
    async with aiohttp.ClientSession() as session:
        await respect_rate_limit()
        
        # Busca orbs disponiveis
        quests = await fetch_orbs_quests(session)
        
        if not quests:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ Nenhum quest disponível")
            return
        
        # Processa 1-2 quests por ciclo (anti-detection)
        quests_to_complete = quests[:random.randint(1, 2)] if isinstance(quests, list) else []
        
        for quest in quests_to_complete:
            try:
                quest_id = quest.get("id", "")
                quest_name = quest.get("title", "Unknown")
                
                await respect_rate_limit()
                delay = get_human_delay()
                await asyncio.sleep(delay)
                
                # Completa o quest
                success = await complete_orb_quest(session, quest_id)
                
                if success:
                    data["completed"].append({
                        "id": quest_id,
                        "name": quest_name,
                        "completed_at": datetime.now().isoformat()
                    })
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Orb: {quest_name}")
                else:
                    data["failed"].append({
                        "id": quest_id,
                        "name": quest_name,
                        "failed_at": datetime.now().isoformat()
                    })
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Falha: {quest_name}")
            
            except Exception as e:
                print(f"❌ Erro processando quest: {e}")
        
        data["last_sync"] = datetime.now().isoformat()
        save_orbs_data(data)

@orbs_loop.before_loop
async def before_orbs_loop():
    await bot.wait_until_ready()

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
