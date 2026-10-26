import asyncio
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import random
import time

class BrowserHandler:
    def __init__(self):
        self.driver = None
        self.setup_driver()
    
    def setup_driver(self):
        """Configura Chrome headless com anti-detection"""
        chrome_options = Options()
        
        # Headless + sem GUI
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        # Anti-detection
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("start-maximized")
        chrome_options.add_argument("--disable-gpu")
        
        # User agent humano
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ]
        chrome_options.add_argument(f"user-agent={random.choice(user_agents)}")
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Inject stealth JS
        self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': '''
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => false,
                });
            '''
        })
    
    async def watch_video_quest(self, video_url, duration_seconds=15):
        """Simula assistir video por X segundos"""
        try:
            print(f"🎬 Iniciando video: {video_url[:50]}...")
            self.driver.get(video_url)
            
            # Espera video carregar
            wait = WebDriverWait(self.driver, 10)
            
            # Procura video player
            video_element = None
            try:
                video_element = wait.until(
                    EC.presence_of_element_located((By.TAG_NAME, "video"))
                )
            except:
                print("⚠️ Video element não encontrado, usando fallback")
            
            # Aguarda duração especificada
            watch_time = duration_seconds + random.randint(5, 15)
            
            # Simula movimentos de mouse aleatórios
            for i in range(int(watch_time / 3)):
                # Scroll aleatório
                scroll = random.randint(0, 3)
                self.driver.execute_script(f"window.scrollBy(0, {scroll});")
                
                # Aguarda antes do próximo movimento
                await asyncio.sleep(random.uniform(2, 5))
            
            print(f"✅ Video assistido: {watch_time}s")
            return True
            
        except Exception as e:
            print(f"❌ Erro assistindo video: {e}")
            return False
    
    async def play_game_quest(self, game_url, play_time=30):
        """Simula jogar um game Discord por X segundos"""
        try:
            print(f"🎮 Iniciando game: {game_url[:50]}...")
            self.driver.get(game_url)
            
            # Aguarda carregamento
            time.sleep(random.uniform(3, 8))
            
            # Procura iframe do game
            iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
            
            if iframes:
                self.driver.switch_to.frame(iframes[0])
            
            # Simula input aleatório no game (clicks, keys)
            play_duration = play_time + random.randint(5, 20)
            
            for i in range(int(play_duration / 2)):
                # Random clicks
                try:
                    x = random.randint(100, 800)
                    y = random.randint(100, 600)
                    self.driver.execute_script(
                        f"document.elementFromPoint({x}, {y})?.click();"
                    )
                except:
                    pass
                
                # Random keys
                keys = ['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight', ' ']
                try:
                    self.driver.execute_script(
                        f"document.dispatchEvent(new KeyboardEvent('keydown', {{'key': '{random.choice(keys)}'}}));"
                    )
                except:
                    pass
                
                await asyncio.sleep(random.uniform(1, 4))
            
            print(f"✅ Game jogado: {play_duration}s")
            return True
            
        except Exception as e:
            print(f"❌ Erro jogando game: {e}")
            return False
    
    def close(self):
        """Fecha o browser"""
        if self.driver:
            self.driver.quit()
            print("🔌 Browser fechado")
