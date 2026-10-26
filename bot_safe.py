import discord
from discord.ext import commands, tasks
import asyncio
import json
import random
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

MIN_DELAY = 45
MAX_DELAY = 180
REQUEST_TIMEOUT = 15
MISSIONS_PER_HOUR = 8
REQUESTS_PER_MINUTE = 2

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

MISSIONS_FILE = "missions.json"
request_tracker = {"last_request": datetime.now(), "count_this_minute": 0}

def load_missions():
    try:
        with open(MISSIONS_FILE, 'r') as f:
            return json.load(f)
    except:
        return {"active": [], "completed": [], "failed": []}

def save_missions(data):
    with open(MISSIONS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def get_human_delay():
    return random.uniform(MIN_DELAY, MAX_DELAY)

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

@bot.command(name='adicionar')
async def add_mission(ctx, *, mission_text):
    await respect_rate_limit()
    
    data = load_missions()
    mission = {
        "id": len(data["active"]) + len(data["completed"]) + 1,
        "text": mission_text,
        "created": datetime.now().isoformat(),
        "attempts": 0,
        "last_attempt": None,
        "status": "queued"
    }
    
    data["active"].append(mission)
    save_missions(data)
    
    embed = discord.Embed(
        title="✅ Missão na fila",
        description=f"{mission_text[:100]}",
        color=discord.Color.green()
    )
    embed.set_footer(text=f"Será executada com delay aleatório")
    
    await ctx.send(embed=embed)

@bot.command(name='status')
async def mission_status(ctx):
    await respect_rate_limit()
    data = load_missions()
    
    embed = discord.Embed(title="📊 Status das Missões", color=discord.Color.blue())
    embed.add_field(name="Ativas", value=len(data["active"]), inline=True)
    embed.add_field(name="Completadas", value=len(data["completed"]), inline=True)
    embed.add_field(name="Falhadas", value=len(data["failed"]), inline=True)
    
    await ctx.send(embed=embed)

@bot.command(name='missoes')
async def list_missions(ctx):
    await respect_rate_limit()
    data = load_missions()
    
    if not data["active"]:
        await ctx.send("Nenhuma missão ativa")
        return
    
    embed = discord.Embed(title="📋 Missões Ativas", color=discord.Color.blue())
    
    for m in data["active"][:10]:
        embed.add_field(
            name=f"ID: {m['id']}",
            value=f"{m['text'][:60]}\nTentativas: {m['attempts']}",
            inline=False
        )
    
    await ctx.send(embed=embed)

@bot.command(name='limpar')
async def clear_completed(ctx):
    data = load_missions()
    count = len(data["completed"])
    data["completed"] = []
    save_missions(data)
    await ctx.send(f"✅ {count} missões limpas")

@tasks.loop(minutes=10)
async def mission_automation():
    data = load_missions()
    
    if not data["active"]:
        return
    
    missions_to_process = data["active"][:random.randint(1, 2)]
    
    for mission in missions_to_process:
        try:
            await respect_rate_limit()
            
            delay = get_human_delay()
            await asyncio.sleep(delay)
            
            mission["attempts"] += 1
            mission["last_attempt"] = datetime.now().isoformat()
            mission["status"] = "completed"
            
            data["completed"].append(mission)
            data["active"].remove(mission)
            
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ {mission['text'][:50]}")
            
        except Exception as e:
            print(f"❌ Erro: {e}")
            mission["status"] = "failed"
            data["failed"].append(mission)
            data["active"].remove(mission)
    
    save_missions(data)

@mission_automation.before_loop
async def before_mission_loop():
    await bot.wait_until_ready()

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
