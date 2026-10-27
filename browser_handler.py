import asyncio
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import random
import time
import logging
import os

logger = logging.getLogger("BrowserHandler")

class BrowserHandler:
    """Selenium Chrome handler com anti-detection para Railway"""
    
    def __init__(self):
        self.driver = None
        self.setup_driver()
    
    def setup_driver(self):
        """Configura Chrome headless com anti-detection"""
        chrome_options = Options()
        
        # Headless + Railway compatible
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--single-process")
        chrome_options.add_argument("--disable-setuid-sandbox")
        
        # Anti-detection flags
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--disable-web-resources")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # User agents rotatórios
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ]
        chrome_options.add_argument(f"user-agent={random.choice(user_agents)}")
        
        try:
            # Try Railway system Chrome
            if os.path.exists("/usr/bin/chromedriver"):
                service = Service("/usr/bin/chromedriver")
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
                logger.info("✓ Using Railway system chromedriver")
            elif os.path.exists("/usr/bin/chromium"):
                # Use chromium directly if chromedriver not found
                chrome_options.binary_location = "/usr/bin/chromium"
                self.driver = webdriver.Chrome(options=chrome_options)
                logger.info("✓ Using Railway chromium")
            else:
                # Last resort: try to find in PATH
                self.driver = webdriver.Chrome(options=chrome_options)
                logger.info("✓ Using Chrome from PATH")
        
        except Exception as e:
            logger.error(f"❌ Failed to initialize Chrome: {e}")
            logger.error("Make sure Dockerfile installs chromium/chromedriver")
            raise
        
        # Inject stealth JavaScript
        try:
            self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => false,
                    });
                    window.chrome = {
                        runtime: {}
                    };
                '''
            })
        except Exception as e:
            logger.warning(f"⚠️ Could not inject stealth JS: {e}")
    
    async def watch_video_quest(self, video_url, duration_seconds=15):
        """Simula assistir um video por X segundos"""
        try:
            logger.info(f"🎬 Abrindo video: {video_url[:50]}...")
            
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: self.driver.get(video_url)
            )
            
            # Aguarda video carregar (max 10s)
            wait = WebDriverWait(self.driver, 10)
            
            try:
                # Procura video element
                video_element = wait.until(
                    EC.presence_of_element_located((By.TAG_NAME, "video")),
                    message="Video element not found"
                )
                logger.info("✓ Video element encontrado")
            except:
                logger.warning("⚠️ Video element não encontrado, continuando...")
            
            # Simula assistência com comportamento humano
            watch_time = duration_seconds + random.randint(5, 15)
            logger.info(f"👁️ Assistindo por {watch_time}s...")
            
            # Scroll aleatório enquanto assiste
            for i in range(int(watch_time / 3)):
                scroll = random.randint(0, 3)
                await loop.run_in_executor(
                    None,
                    lambda s=scroll: self.driver.execute_script(f"window.scrollBy(0, {s});")
                )
                await asyncio.sleep(random.uniform(2, 5))
            
            logger.info(f"✅ Video assistido com sucesso ({watch_time}s)")
            return True
        
        except asyncio.CancelledError:
            raise
        except Exception as e:
            logger.error(f"❌ Erro assistindo video: {e}")
            return False
    
    async def play_game_quest(self, game_url, play_time=30, account_token=None):
        """Simula jogar um game Discord por X segundos"""
        try:
            logger.info(f"🎮 Abrindo game: {game_url[:50]}...")
            
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: self.driver.get(game_url)
            )
            
            # Aguarda game carregar
            await asyncio.sleep(random.uniform(3, 8))
            
            # Verifica se existe modal "Configurar Missões (Orbs)"
            if account_token:
                logger.info("🔍 Procurando modal de Orbs...")
                try:
                    modal_found = await self.detect_orbs_modal()
                    if modal_found:
                        logger.info("🔐 Modal detectado — iniciando preenchimento automático...")
                        success = await self.handle_orbs_modal(account_token)
                        if success:
                            logger.info("✅ Modal preenchido com sucesso!")
                        else:
                            logger.warning("⚠️ Falha ao preencher modal")
                    else:
                        logger.info("ℹ️ Modal não encontrado nesta página")
                except Exception as e:
                    logger.error(f"❌ Erro processando modal: {e}")
            
            # Procura iframe do game
            try:
                iframes = await loop.run_in_executor(
                    None,
                    lambda: self.driver.find_elements(By.TAG_NAME, "iframe")
                )
                
                if iframes:
                    await loop.run_in_executor(
                        None,
                        lambda: self.driver.switch_to.frame(iframes[0])
                    )
                    logger.info("✓ Game iframe encontrado")
            except:
                logger.warning("⚠️ Game iframe não encontrado")
            
            # Simula input aleatório
            play_duration = play_time + random.randint(5, 20)
            logger.info(f"🕹️ Jogando por {play_duration}s...")
            
            for i in range(int(play_duration / 2)):
                # Random clicks
                try:
                    x = random.randint(100, 800)
                    y = random.randint(100, 600)
                    await loop.run_in_executor(
                        None,
                        lambda: self.driver.execute_script(
                            f"document.elementFromPoint({x}, {y})?.click();"
                        )
                    )
                except:
                    pass
                
                # Random keyboard input
                keys = ['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight', ' ', 'Enter']
                try:
                    key = random.choice(keys)
                    await loop.run_in_executor(
                        None,
                        lambda k=key: self.driver.execute_script(
                            f"document.dispatchEvent(new KeyboardEvent('keydown', {{'key': '{k}'}}));"
                        )
                    )
                except:
                    pass
                
                await asyncio.sleep(random.uniform(1, 4))
            
            logger.info(f"✅ Game jogado com sucesso ({play_duration}s)")
            return True
        
        except asyncio.CancelledError:
            raise
        except Exception as e:
            logger.error(f"❌ Erro jogando game: {e}")
            return False
    
    async def detect_orbs_modal(self):
        """Detecta se modal 'Configurar Missões (Orbs)' está presente"""
        try:
            loop = asyncio.get_event_loop()
            
            # Procura pelo título do modal
            modal_selectors = [
                "div:has(> h1:contains('Configurar Missões'))",
                "h1:contains('Configurar Missões')",
                "div[role='dialog']",
                "[aria-labelledby*='Missoes'], [aria-labelledby*='Orbs']",
            ]
            
            # Fallback: procura por qualquer heading com "Configurar"
            try:
                headings = await loop.run_in_executor(
                    None,
                    lambda: self.driver.find_elements(By.TAG_NAME, "h1")
                )
                
                for heading in headings:
                    try:
                        text = await loop.run_in_executor(
                            None,
                            lambda h=heading: h.text
                        )
                        if "Configurar" in text or "Missões" in text or "Orbs" in text:
                            logger.info(f"✓ DETECTOU MODAL: '{text}'")
                            return True
                    except:
                        continue
            except:
                pass
            
            logger.warning("⚠️ Modal 'Configurar Missões' NÃO detectado")
            return False
        
        except Exception as e:
            logger.error(f"❌ Erro detectando modal: {e}")
            return False
    
    async def handle_orbs_modal(self, account_token):
        """Preenche modal 'Configurar Missões (Orbs)' automaticamente"""
        try:
            loop = asyncio.get_event_loop()
            
            # PRIMEIRO: verifica se modal existe
            modal_exists = await self.detect_orbs_modal()
            if not modal_exists:
                logger.warning("⚠️ Modal não existe — pulando preenchimento")
                return False
            
            logger.info("🔧 Preenchendo modal 'Configurar Missões (Orbs)'...")
            await asyncio.sleep(1)  # Aguarda modal renderizar
            
            # Procura textarea/input com placeholder ou contenteditable
            input_selectors = [
                "textarea[placeholder*='cole']",
                "textarea[placeholder*='Token']",
                "textarea[placeholder*='token']",
                "input[placeholder*='cole']",
                "input[placeholder*='Token']",
                "textarea[aria-label*='Token']",
                "input[aria-label*='Token']",
                "div[contenteditable='true']",
                "textarea:not([readonly])",
                "textarea",
            ]
            
            input_element = None
            for selector in input_selectors:
                try:
                    elements = await loop.run_in_executor(
                        None,
                        lambda s=selector: self.driver.find_elements(By.CSS_SELECTOR, s)
                    )
                    if elements:
                        # Verifica se elemento é visível
                        element = elements[0]
                        is_visible = await loop.run_in_executor(
                            None,
                            lambda e=element: self.driver.execute_script(
                                "return arguments[0].offsetParent !== null;", e
                            )
                        )
                        if is_visible:
                            input_element = element
                            logger.info(f"✓ Input encontrado: {selector}")
                            break
                except:
                    continue
            
            if not input_element:
                logger.error("❌ Input field não encontrado — modal pode ter conteúdo diferente")
                return False
            
            logger.info("✓ Input field visível e pronto para preenchimento")
            
            # Limpa field
            try:
                await loop.run_in_executor(
                    None,
                    lambda: input_element.clear()
                )
                logger.info("✓ Input field limpo")
            except Exception as e:
                logger.warning(f"⚠️ Erro limpando field: {e}")
            
            await asyncio.sleep(0.5)
            
            # Type token character by character (simula typing humano)
            logger.info(f"⌨️ Digitando token ({len(account_token)} caracteres)...")
            chars_typed = 0
            for char in account_token:
                try:
                    await loop.run_in_executor(
                        None,
                        lambda c=char: input_element.send_keys(c)
                    )
                    chars_typed += 1
                    if chars_typed % 10 == 0:
                        logger.info(f"  → {chars_typed}/{len(account_token)} caracteres")
                except Exception as e:
                    logger.error(f"❌ Erro digitando char: {e}")
                    return False
                await asyncio.sleep(random.uniform(0.05, 0.15))
            
            logger.info(f"✅ Token totalmente preenchido ({chars_typed} caracteres)")
            await asyncio.sleep(0.5)
            
            # Verifica se token foi realmente inserido
            field_value = await loop.run_in_executor(
                None,
                lambda: input_element.get_attribute("value") or input_element.text
            )
            if len(field_value) < len(account_token) * 0.8:  # Pelo menos 80% do token
                logger.warning(f"⚠️ Token pode não ter sido inserido corretamente ({len(field_value)}/{len(account_token)} chars)")
            else:
                logger.info(f"✓ Token verificado no field ({len(field_value)} caracteres)")
            
            # Procura botão "Enviar"
            logger.info("🔍 Procurando botão 'Enviar'...")
            
            try:
                buttons = await loop.run_in_executor(
                    None,
                    lambda: self.driver.find_elements(By.TAG_NAME, "button")
                )
                
                logger.info(f"   → Encontrados {len(buttons)} botões na página")
                
                submit_button = None
                for i, btn in enumerate(buttons):
                    try:
                        text = await loop.run_in_executor(
                            None,
                            lambda b=btn: b.text
                        )
                        is_visible = await loop.run_in_executor(
                            None,
                            lambda b=btn: self.driver.execute_script(
                                "return arguments[0].offsetParent !== null;", b
                            )
                        )
                        
                        if is_visible:
                            logger.info(f"   → Botão {i}: '{text}' (visível)")
                            if "Enviar" in text or "Submit" in text or "Confirmar" in text:
                                submit_button = btn
                                logger.info(f"✓ Botão 'Enviar' ENCONTRADO!")
                                break
                        else:
                            logger.info(f"   → Botão {i}: '{text}' (oculto)")
                    except Exception as e:
                        logger.info(f"   → Botão {i}: erro ao ler ({e})")
                        continue
                
                if not submit_button:
                    logger.error("❌ Botão 'Enviar' NÃO encontrado em nenhum botão")
                    return False
                
                logger.info("🖱️ Clicando botão 'Enviar'...")
                try:
                    await loop.run_in_executor(
                        None,
                        lambda: submit_button.click()
                    )
                    logger.info("✓ Click enviado ao servidor")
                except Exception as e:
                    logger.error(f"❌ Erro ao clicar: {e}")
                    return False
                
                # Aguarda resposta do servidor
                logger.info("⏳ Aguardando resposta do servidor (2s)...")
                await asyncio.sleep(2)
                
                logger.info("✅ Modal enviado com sucesso")
                return True
            
            except Exception as e:
                logger.error(f"❌ Erro processando botão: {e}")
                return False
        
        except asyncio.CancelledError:
            raise
        except Exception as e:
            logger.error(f"❌ Erro preenchendo modal: {e}")
            return False
    
    def close(self):
        """Fecha o browser"""
        try:
            if self.driver:
                self.driver.quit()
                logger.info("🔌 Browser fechado")
        except Exception as e:
            logger.error(f"❌ Erro fechando browser: {e}")
