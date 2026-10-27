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
import logging

load_dotenv()

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("OrbsBot")

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
if not DISCORD_TOKEN:
    raise ValueError("❌ DISCORD_TOKEN not found in .env or environment variables")

MIN_DELAY = 30
MAX_DELAY = 90
ORBS_API = "https://discord.com/api/v10/users/@me/quests"

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents)
tree = discord.app_commands.CommandTree(bot)

ORBS_FILE = "orbs_progress.json"
TOKENS_FILE = "tokens.json"
browser = None
request_tracker = {"last_request": datetime.now(), "count_this_minute": 0}
orbs_loop_running = False
account_tokens = []  # Para games que precisam de token

def load_orbs_data():
    """Carrega dados persistentes de orbs"""
    try:
        with open(ORBS_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "completed": [],
            "failed": [],
            "last_sync": None,
            "stats": {"videos": 0, "games": 0, "total": 0}
        }

def load_account_tokens():
    """Carrega tokens de contas para preenchimento de modais (games)"""
    global account_tokens
    try:
        with open(TOKENS_FILE, 'r') as f:
            data = json.load(f)
            if isinstance(data, list):
                account_tokens = [t if isinstance(t, str) else t.get("token", "") for t in data]
            elif isinstance(data, dict) and "tokens" in data:
                account_tokens = data["tokens"]
            else:
                account_tokens = []
        
        if account_tokens:
            logger.info(f"✓ Carregou {len(account_tokens)} tokens de contas")
        return account_tokens
    except FileNotFoundError:
        logger.warning(f"⚠️ Ficheiro {TOKENS_FILE} não encontrado — games podem falhar modal")
        return []
    except Exception as e:
        logger.error(f"❌ Erro carregando tokens: {e}")
        return []

def save_orbs_data(data):
    """Salva dados persistentes"""
    try:
        with open(ORBS_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        logger.error(f"❌ Erro salvando dados: {e}")

def get_human_delay():
    """Retorna delay aleatório (anti-detection)"""
    return random.uniform(MIN_DELAY, MAX_DELAY)

async def respect_rate_limit():
    """Rate limit: máximo 2 requests/minuto"""
    global request_tracker
    
    now = datetime.now()
    elapsed = (now - request_tracker["last_request"]).total_seconds()
    
    if elapsed > 60:
        request_tracker["count_this_minute"] = 0
        request_tracker["last_request"] = now
    
    if request_tracker["count_this_minute"] >= 2:
        wait_time = 60 - elapsed
        if wait_time > 0:
            logger.warning(f"⏱️ Rate limit: aguardando {wait_time:.1f}s")
            await asyncio.sleep(wait_time)
            request_tracker["count_this_minute"] = 0
            request_tracker["last_request"] = datetime.now()
    
    request_tracker["count_this_minute"] += 1

async def fetch_orbs_quests(session):
    """Busca quests disponíveis da API Discord"""
    headers = {
        "Authorization": DISCORD_TOKEN,
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        async with session.get(ORBS_API, headers=headers, timeout=15) as resp:
            if resp.status == 200:
                data = await resp.json()
                logger.info(f"📋 API retornou: {type(data).__name__}")
                return data
            else:
                logger.error(f"❌ API error {resp.status}")
                return None
    except Exception as e:
        logger.error(f"❌ Erro fetching quests: {e}")
        return None

async def complete_quest_api(session, quest_id):
    """Marca quest como 100% completada na API Discord"""
    headers = {
        "Authorization": DISCORD_TOKEN,
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
    }
    
    url = f"{ORBS_API}/{quest_id}/progress"
    
    try:
        async with session.post(
            url,
            headers=headers,
            json={"progress": 100},
            timeout=15
        ) as resp:
            success = resp.status in [200, 201, 204]
            if success:
                logger.info(f"✅ API marked quest {quest_id} as completed")
            return success
    except Exception as e:
        logger.error(f"❌ Erro completando quest via API: {e}")
        return False

async def process_quest(session, quest, account_token=None):
    """Processa um quest completo: automação browser + API marking"""
    quest_id = quest.get("id", "unknown")
    quest_name = quest.get("title", "Unknown Quest")
    quest_type = quest.get("type", "unknown").lower()
    quest_url = quest.get("quest_url", "")
    
    logger.info(f"\n🎯 Processando: {quest_name} | Tipo: {quest_type}")
    
    success = False
    quest_type_recorded = None
    
    try:
        # Automação baseada no tipo
        if "video" in quest_type:
            logger.info("📹 Quest tipo: VIDEO — assistindo...")
            if browser and quest_url:
                success = await asyncio.wait_for(
                    browser.watch_video_quest(quest_url, duration_seconds=15),
                    timeout=60.0
                )
                quest_type_recorded = "video"
            else:
                logger.warning("⚠️ Browser não disponível ou URL vazia")
        
        elif "game" in quest_type:
            logger.info("🎮 Quest tipo: GAME — jogando...")
            if browser and quest_url:
                success = await asyncio.wait_for(
                    browser.play_game_quest(
                        quest_url, 
                        play_time=30,
                        account_token=account_token
                    ),
                    timeout=120.0
                )
                quest_type_recorded = "game"
            else:
                logger.warning("⚠️ Browser não disponível ou URL vazia")
        
        else:
            logger.info(f"🔹 Quest tipo: {quest_type} — marcando direto")
            success = True
            quest_type_recorded = quest_type
        
        # Se automação bem-sucedida, marca na API
        if success:
            await respect_rate_limit()
            api_success = await complete_quest_api(session, quest_id)
            
            if api_success:
                logger.info(f"✅ COMPLETO: {quest_name}")
                return {
                    "id": quest_id,
                    "name": quest_name,
                    "type": quest_type_recorded,
                    "completed_at": datetime.now().isoformat(),
                    "status": "completed"
                }
    
    except asyncio.TimeoutError:
        logger.error(f"⏱️ Timeout processando quest {quest_name}")
    except Exception as e:
        logger.error(f"❌ Erro processando quest: {e}")
    
    logger.warning(f"❌ FALHOU: {quest_name}")
    return {
        "id": quest_id,
        "name": quest_name,
        "type": quest_type_recorded or quest_type,
        "failed_at": datetime.now().isoformat(),
        "status": "failed"
    }

@bot.event
async def on_ready():
    """Bot conectado — inicializa browser e sincroniza comandos"""
    global browser
    
    logger.info(f'✅ {bot.user} conectado com sucesso')
    logger.info(f'👤 User ID: {bot.user.id}')
    logger.info(f'🔒 Anti-detection: delays {MIN_DELAY}-{MAX_DELAY}s, rate limit 2req/min')
    
    # Inicializa browser Selenium
    if browser is None:
        try:
            browser = BrowserHandler()
            logger.info("🌐 Browser Selenium inicializado com sucesso")
        except Exception as e:
            logger.error(f"⚠️ Erro inicializando browser: {e}")
            logger.info("⚠️ Bot vai funcionar sem automação de videos/games")
    
    # Sincroniza slash commands
    try:
        synced = await tree.sync()
        logger.info(f'📋 {len(synced)} slash commands sincronizados: {[c.name for c in synced]}')
    except Exception as e:
        logger.error(f'❌ Erro sincronizando comandos: {e}')

@tree.command(name="orbs", description="Controla automação de Discord Orbs/Quests")
@discord.app_commands.describe(
    action="status, start ou stop"
)
async def orbs_command(interaction: discord.Interaction, action: str = "status"):
    """
    Controla automação de orbs e quests.
    - /orbs status → mostra stats
    - /orbs start → inicia automação
    - /orbs stop → para automação
    """
    await interaction.response.defer()
    
    if action == "status":
        try:
            await respect_rate_limit()
            data = load_orbs_data()
            stats = data.get("stats", {})
            
            embed = discord.Embed(
                title="🔮 Discord Orbs Quest Status",
                color=discord.Color.purple()
            )
            embed.add_field(
                name="✅ Quests Completadas",
                value=str(len(data["completed"])),
                inline=True
            )
            embed.add_field(
                name="❌ Quests Falhadas",
                value=str(len(data["failed"])),
                inline=True
            )
            embed.add_field(name="📹 Videos", value=str(stats.get("videos", 0)), inline=True)
            embed.add_field(name="🎮 Games", value=str(stats.get("games", 0)), inline=True)
            embed.add_field(name="📊 Total", value=str(stats.get("total", 0)), inline=True)
            embed.add_field(
                name="🕐 Última execução",
                value=data.get("last_sync") or "Nunca",
                inline=False
            )
            
            await interaction.followup.send(embed=embed)
        except Exception as e:
            await interaction.followup.send(f"❌ Erro: {e}")
    
    elif action == "start":
        global orbs_loop_running
        try:
            if orbs_loop_running or orbs_automation_loop.is_running():
                await interaction.followup.send("⚠️ Automação já está rodando")
            else:
                orbs_loop_running = True
                orbs_automation_loop.start()
                await interaction.followup.send("✅ Automação iniciada (videos + games + API)\n🔄 Próxima execução em 5 minutos")
        except Exception as e:
            await interaction.followup.send(f"❌ Erro: {e}")
    
    elif action == "stop":
        global orbs_loop_running
        try:
            if orbs_loop_running and orbs_automation_loop.is_running():
                orbs_automation_loop.stop()
                orbs_loop_running = False
                await interaction.followup.send("⏹️ Automação parada")
            else:
                await interaction.followup.send("⚠️ Automação não está rodando")
        except Exception as e:
            await interaction.followup.send(f"❌ Erro: {e}")
    
    else:
        await interaction.followup.send("❌ Ação inválida. Use: `status`, `start` ou `stop`")

@tree.command(name="clear", description="Limpa histórico de quests completados/falhados")
async def clear_orbs_data(interaction: discord.Interaction):
    """Limpa histórico de quests"""
    try:
        await interaction.response.defer()
        await respect_rate_limit()
        
        data = load_orbs_data()
        count = len(data["completed"]) + len(data["failed"])
        
        data["completed"] = []
        data["failed"] = []
        data["stats"] = {"videos": 0, "games": 0, "total": 0}
        save_orbs_data(data)
        
        await interaction.followup.send(f"✅ {count} quests removidos do histórico")
    except Exception as e:
        await interaction.followup.send(f"❌ Erro: {e}")

@tasks.loop(minutes=5)
async def orbs_automation_loop():
    """Loop automático: busca quests e processa (videos + games + API)"""
    logger.info(f"\n{'='*60}")
    logger.info(f"[{datetime.now().strftime('%H:%M:%S')}] 🔄 Ciclo de automação de quests iniciado")
    logger.info(f"{'='*60}")
    
    data = load_orbs_data()
    
    if browser is None:
        logger.warning("⚠️ Browser não está inicializado — pulando ciclo")
        return
    
    # Carrega tokens para games (preenchimento de modais)
    if not account_tokens:
        load_account_tokens()
    
    try:
        async with aiohttp.ClientSession() as session:
            await respect_rate_limit()
            
            # Busca quests
            quests = await fetch_orbs_quests(session)
            
            if not quests:
                logger.warning("⚠️ Nenhum quest disponível")
                return
            
            # Trata resposta (pode ser lista ou dict com "quests")
            if isinstance(quests, dict):
                quest_list = quests.get("quests", [])
            elif isinstance(quests, list):
                quest_list = quests
            else:
                logger.error(f"❌ Formato de resposta inválido: {type(quests)}")
                return
            
            logger.info(f"📋 Total de quests encontrados: {len(quest_list)}")
            
            if not quest_list:
                logger.warning("⚠️ Lista de quests vazia")
                return
            
            # Processa 1-2 quests aleatórios
            num_to_process = min(random.randint(1, 2), len(quest_list))
            selected = random.sample(quest_list, num_to_process)
            
            for quest in selected:
                try:
                    await respect_rate_limit()
                    
                    delay = get_human_delay()
                    logger.info(f"⏱️ Delay anti-detection: {delay:.1f}s")
                    await asyncio.sleep(delay)
                    
                    # Se é game, passa token para preencher modal
                    quest_token = None
                    if "game" in quest.get("type", "").lower() and account_tokens:
                        quest_token = random.choice(account_tokens)
                    
                    result = await process_quest(session, quest, account_token=quest_token)
                    
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
                
                except asyncio.CancelledError:
                    raise
                except Exception as e:
                    logger.error(f"❌ Erro processando quest individual: {e}")
        
        data["last_sync"] = datetime.now().isoformat()
        save_orbs_data(data)
        
        logger.info(f"✅ Ciclo completo — Próximo em 5 minutos")
        logger.info(f"{'='*60}\n")
    
    except asyncio.CancelledError:
        logger.info("🛑 Loop cancelado")
        raise
    except Exception as e:
        logger.error(f"❌ Erro no ciclo: {e}")

@orbs_automation_loop.before_loop
async def before_automation_loop():
    """Aguarda bot estar pronto antes de iniciar loop"""
    await bot.wait_until_ready()

@bot.event
async def on_error(event, *args, **kwargs):
    """Error handler"""
    logger.error(f"❌ Erro em evento '{event}': {Exception}")

def main():
    """Entry point"""
    try:
        logger.info("🚀 Iniciando Discord Orbs Automation Bot")
        logger.info(f"Token carregado: {DISCORD_TOKEN[:20]}...")
        bot.run(DISCORD_TOKEN)
    except KeyboardInterrupt:
        logger.info("\n🔌 Encerrando bot...")
        if browser:
            browser.close()
    except Exception as e:
        logger.error(f"❌ Erro fatal: {e}")
        if browser:
            browser.close()
        raise

if __name__ == "__main__":
    main()
