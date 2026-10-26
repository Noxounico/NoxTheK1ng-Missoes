import discord
from discord.ext import commands, tasks
import asyncio
import json
import random
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import aiohttp
from browser_handler import BrowserHandler

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

MIN_DELAY = 30
MAX_DELAY = 90
ORBS_API = "https://discord.com/api/v10/users/@me/quests"

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='/')
tree = discord.app_commands.CommandTree(bot)

ORBS_FILE = "orbs_progress.json"
browser = None
request_tracker = {"last_request": datetime.now(), "count_this_minute": 0}

def load_orbs_data():
    try:
        with open(ORBS_FILE, 'r') as f:
            return json.load(f)
    except:
        return {"completed": [], "failed": [], "last_sync": None, "stats": {"videos": 0, "games": 0, "total": 0}}

def save_orbs_data(data):
    with open(ORBS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def get_human_delay():
    return random.uniform(MIN_DELAY, MAX_DELAY)

async def respect_rate_limit():
    global request_tracker
    
    now = datetime.now()
    if (now - request_tracker["last_request"]).seconds > 60:
        request_tracker["count_this_minute"] = 0
    
    if request_tracker["count_this_minute"] >= 2:
        wait_time = 60 - (now - request_tracker["last_request"]).seconds
        if wait_time > 0:
            await asyncio.sleep(wait_time)
            request_tracker["count_this_minute"] = 0
    
    request_tracker["count_this_minute"] += 1
    request_tracker["last_request"] = now

async def fetch_orbs_quests(session):
    """Busca quests disponíveis"""
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
        print(f"❌ Erro fetching quests: {e}")
        return None

async def complete_quest_api(session, quest_id):
    """Marca quest como completada na API"""
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
        print(f"❌ Erro completando quest: {e}")
        return False

async def process_quest(session, quest):
    """Processa um quest completo (automação + API marking)"""
    quest_id = quest.get("id", "")
    quest_name = quest.get("title", "Unknown")
    quest_type = quest.get("type", "unknown")  # video, game, etc
    
    print(f"\n🎯 Processando quest: {quest_name} ({quest_type})")
    
    quest_url = quest.get("quest_url", "")
    success = False
    quest_type_recorded = None
    
    try:
        # Automação baseada no tipo de quest
        if "video" in quest_type.lower():
            print(f"📹 Quest tipo: VIDEO")
            if browser and quest_url:
                success = await browser.watch_video_quest(quest_url, duration_seconds=15)
                quest_type_recorded = "video"
        
        elif "game" in quest_type.lower():
            print(f"🎮 Quest tipo: GAME")
            if browser and quest_url:
                success = await browser.play_game_quest(quest_url, play_time=30)
                quest_type_recorded = "game"
        
        else:
            # Fallback - assume que é completável direto
            print(f"🔹 Quest tipo: STANDARD")
            success = True
            quest_type_recorded = "standard"
        
        # Se automação foi bem-sucedida, marca na API
        if success:
            await respect_rate_limit()
            api_success = await complete_quest_api(session, quest_id)
            
            if api_success:
                print(f"✅ Quest completada: {quest_name}")
                return {
                    "id": quest_id,
                    "name": quest_name,
                    "type": quest_type_recorded,
                    "completed_at": datetime.now().isoformat(),
                    "status": "completed"
                }
    
    except Exception as e:
        print(f"❌ Erro processando quest: {e}")
    
    print(f"❌ Quest falhou: {quest_name}")
    return {
        "id": quest_id,
        "name": quest_name,
        "type": quest_type_recorded or quest_type,
        "failed_at": datetime.now().isoformat(),
        "status": "failed"
    }

@bot.event
async def on_ready():
    global browser
    print(f'✅ {bot.user} conectado')
    print(f'🔒 Anti-detection ativo: delays {MIN_DELAY}-{MAX_DELAY}s')
    print(f'👤 User ID: {bot.user.id}')
    
    # Inicializa browser
    if browser is None:
        try:
            browser = BrowserHandler()
            print("🌐 Browser inicializado (Selenium)")
        except Exception as e:
            print(f"⚠️ Erro inicializando browser: {e}")
    
    try:
        synced = await tree.sync()
        print(f'📋 {len(synced)} slash commands sincronizados')
    except Exception as e:
        print(f'❌ Erro sincronizando comandos: {e}')
    
    if not orbs_loop.is_running():
        orbs_loop.start()

@tree.command(name="orbs", description="Controla automação de orbs")
@discord.app_commands.describe(action="status, start ou stop")
async def orbs_command(interaction: discord.Interaction, action: str = "status"):
    """Controla automação de orbs e quests"""
    await interaction.response.defer()
    await respect_rate_limit()
    
    if action == "status":
        data = load_orbs_data()
        stats = data.get("stats", {})
        
        embed = discord.Embed(title="🔮 Orbs Quest Status", color=discord.Color.purple())
        embed.add_field(name="✅ Completadas", value=len(data["completed"]), inline=True)
        embed.add_field(name="❌ Falhadas", value=len(data["failed"]), inline=True)
        embed.add_field(name="📹 Videos", value=stats.get("videos", 0), inline=True)
        embed.add_field(name="🎮 Games", value=stats.get("games", 0), inline=True)
        embed.add_field(name="📊 Total", value=stats.get("total", 0), inline=True)
        embed.add_field(name="🕐 Última sync", value=data["last_sync"] or "Nunca", inline=False)
        
        await interaction.followup.send(embed=embed)
    
    elif action == "start":
        if orbs_loop.is_running():
            await interaction.followup.send("⚠️ Automação já está rodando")
        else:
            orbs_loop.start()
            await interaction.followup.send("✅ Automação iniciada (videos + games + API)")
    
    elif action == "stop":
        if orbs_loop.is_running():
            orbs_loop.stop()
            await interaction.followup.send("⏹️ Automação parada")
        else:
            await interaction.followup.send("⚠️ Automação não está rodando")
    
    else:
        await interaction.followup.send("Uso: `/orbs status` | `/orbs start` | `/orbs stop`")

@tree.command(name="clear", description="Limpa histórico de quests")
async def clear_orbs_data(interaction: discord.Interaction):
    """Limpa histórico"""
    await interaction.response.defer()
    data = load_orbs_data()
    count = len(data["completed"]) + len(data["failed"])
    data["completed"] = []
    data["failed"] = []
    data["stats"] = {"videos": 0, "games": 0, "total": 0}
    save_orbs_data(data)
    await interaction.followup.send(f"✅ {count} quests removidos do histórico")

@tasks.loop(minutes=5)
async def orbs_loop():
    """Automação completa de quests"""
    global browser
    
    data = load_orbs_data()
    
    if browser is None:
        print("⚠️ Browser não está inicializado")
        return
    
    async with aiohttp.ClientSession() as session:
        await respect_rate_limit()
        
        # Busca quests
        quests = await fetch_orbs_quests(session)
        
        if not quests:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ Nenhum quest disponível")
            return
        
        if not isinstance(quests, list):
            quests = quests.get("quests", []) if isinstance(quests, dict) else []
        
        # Processa 1-2 quests por ciclo
        quests_to_process = quests[:random.randint(1, 2)]
        
        for quest in quests_to_process:
            try:
                await respect_rate_limit()
                
                delay = get_human_delay()
                await asyncio.sleep(delay)
                
                result = await process_quest(session, quest)
                
                if result["status"] == "completed":
                    data["completed"].append(result)
                    # Atualiza stats
                    if result.get("type") == "video":
                        data["stats"]["videos"] = data["stats"].get("videos", 0) + 1
                    elif result.get("type") == "game":
                        data["stats"]["games"] = data["stats"].get("games", 0) + 1
                    data["stats"]["total"] = data["stats"].get("total", 0) + 1
                else:
                    data["failed"].append(result)
            
            except Exception as e:
                print(f"❌ Erro no loop: {e}")
        
        data["last_sync"] = datetime.now().isoformat()
        save_orbs_data(data)

@orbs_loop.before_loop
async def before_orbs_loop():
    await bot.wait_until_ready()

@bot.event
async def on_error(event, *args, **kwargs):
    print(f"❌ Erro em {event}: {Exception}")

if __name__ == "__main__":
    try:
        bot.run(DISCORD_TOKEN)
    except KeyboardInterrupt:
        print("\n🔌 Encerrando...")
        if browser:
            browser.close()
