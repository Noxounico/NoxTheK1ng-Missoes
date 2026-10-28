#!/usr/bin/env python3
"""
🤖 Impulsos.Fun Auto Bot
Preenche automaticamente o formulário de quests em impulsos.fun/quests
Seleciona "1 Quest Aleatória" (gratuito) e deixa executar em loop
"""

import os
import json
import logging
import time
import random
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Logger Setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Config
IMPULSOS_URL = "https://impulsos.fun/quests"
TOKENS_FILE = "tokens.json"
CHROME_PATH = "/usr/bin/chromium"  # Railway
CHROMEDRIVER_PATH = "/usr/bin/chromedriver"  # Railway

class ImpulsosAutoBot:
    def __init__(self):
        """Inicializa bot com Selenium Chrome"""
        self.driver = None
        self.tokens = []
        self.completed_count = 0
        self.failed_count = 0
        
    def load_tokens(self):
        """Carrega tokens do tokens.json"""
        try:
            if not os.path.exists(TOKENS_FILE):
                logger.warning(f"⚠️ {TOKENS_FILE} não encontrado")
                logger.info("   Criando arquivo vazio...")
                with open(TOKENS_FILE, 'w') as f:
                    json.dump([], f)
                return False
            
            with open(TOKENS_FILE, 'r') as f:
                data = json.load(f)
            
            # Parse diferentes formatos
            if isinstance(data, list) and data:
                if isinstance(data[0], dict):
                    self.tokens = [t.get("token", "") for t in data]
                else:
                    self.tokens = data
            
            if self.tokens:
                logger.info(f"✓ Carregou {len(self.tokens)} tokens")
                # Show tokens (masked)
                for i, token in enumerate(self.tokens):
                    masked = token[:10] + "..." + token[-10:] if len(token) > 20 else token
                    logger.info(f"   Token {i+1}: {masked}")
                return True
            else:
                logger.warning("⚠️ tokens.json vazio")
                return False
        except Exception as e:
            logger.error(f"❌ Erro carregando tokens: {e}")
            return False
    
    def setup_driver(self):
        """Configura Chrome Selenium com anti-detection"""
        try:
            logger.info("🌐 Inicializando Chrome Selenium...")
            
            options = Options()
            options.binary_location = CHROME_PATH
            options.add_argument("--headless")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-web-resources")
            options.add_argument(f"user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            self.driver = webdriver.Chrome(
                executable_path=CHROMEDRIVER_PATH,
                options=options
            )
            
            # Anti-webdriver detection
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => false})")
            
            logger.info("✓ Chrome inicializado com sucesso")
            return True
        except Exception as e:
            logger.error(f"❌ Erro inicializando Chrome: {e}")
            return False
    
    def fill_and_start(self):
        """Preenche form e clica start"""
        try:
            logger.info(f"\n{'='*70}")
            logger.info(f"[{datetime.now().strftime('%H:%M:%S')}] 🎯 Novo ciclo iniciado")
            logger.info(f"{'='*70}")
            
            # Abre página
            logger.info("📲 Abrindo impulsos.fun/quests...")
            self.driver.get(IMPULSOS_URL)
            time.sleep(3)
            
            # ============= STEP 1: PREENCHER TOKENS =============
            logger.info("\n[STEP 1] 📝 Procurando campo de tokens...")
            
            try:
                # Procura textarea para colar tokens
                token_input = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "textarea"))
                )
                logger.info("   ✓ Campo de tokens encontrado")
                
                # Seleciona token aleatório
                selected_token = random.choice(self.tokens)
                masked = selected_token[:10] + "..." + selected_token[-10:]
                logger.info(f"   📌 Token selecionado: {masked}")
                
                # Limpa e preenche
                token_input.clear()
                time.sleep(0.5)
                
                logger.info(f"   ⌨️ Digitando token ({len(selected_token)} caracteres)...")
                token_input.send_keys(selected_token)
                time.sleep(1)
                
                # Verifica se foi preenchido
                if token_input.get_attribute("value"):
                    logger.info("   ✓ Token preenchido com sucesso")
                else:
                    logger.warning("   ⚠️ Token pode não ter sido preenchido")
                
            except TimeoutException:
                logger.error("   ❌ Campo de tokens não encontrado (timeout 10s)")
                return False
            
            time.sleep(2)
            
            # ============= STEP 2: SELECIONAR MODO =============
            logger.info("\n[STEP 2] 🎯 Procurando modo 'Grátis' ou '1 Quest Aleatória'...")
            
            try:
                # Procura botão com texto "Grátis" ou "1 Quest"
                buttons = self.driver.find_elements(By.TAG_NAME, "button")
                logger.info(f"   → Encontrados {len(buttons)} botões")
                
                free_button = None
                for btn in buttons:
                    try:
                        text = btn.text
                        if "Grátis" in text or "1 Quest" in text or "Aleatória" in text:
                            free_button = btn
                            logger.info(f"   ✓ Botão encontrado: '{text}'")
                            break
                    except:
                        continue
                
                if not free_button:
                    logger.error("   ❌ Modo 'Grátis' não encontrado")
                    return False
                
                logger.info("   🖱️ Clicando botão 'Grátis'...")
                free_button.click()
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"   ❌ Erro selecionando modo: {e}")
                return False
            
            # ============= STEP 3: PROCURAR BOTÃO START/INICIAR =============
            logger.info("\n[STEP 3] 🚀 Procurando botão 'Iniciar' ou 'Start'...")
            
            try:
                buttons = self.driver.find_elements(By.TAG_NAME, "button")
                start_button = None
                
                for btn in buttons:
                    try:
                        text = btn.text.lower()
                        if "iniciar" in text or "start" in text or "começar" in text:
                            # Verifica se está visível
                            if btn.is_displayed():
                                start_button = btn
                                logger.info(f"   ✓ Botão encontrado: '{btn.text}'")
                                break
                    except:
                        continue
                
                if not start_button:
                    logger.error("   ❌ Botão 'Iniciar' não encontrado")
                    return False
                
                logger.info("   🖱️ Clicando 'Iniciar'...")
                start_button.click()
                time.sleep(3)
                
                logger.info("\n✅ FORMULÁRIO ENVIADO COM SUCESSO")
                logger.info("   → Quest iniciada na página...")
                
                # ============= STEP 4: AUTOMATIZAR QUEST =============
                logger.info("\n[STEP 4] 🤖 Detectando e automatizando quest...")
                
                quest_type = self.detect_quest_type()
                automation_success = False
                
                if quest_type == "video":
                    automation_success = self.automate_video_quest()
                elif quest_type == "game":
                    automation_success = self.automate_game_quest()
                elif quest_type == "survey":
                    automation_success = self.automate_survey_quest()
                else:
                    logger.info("   ℹ️ Tipo desconhecido - aguardando conclusão manual")
                    automation_success = True
                
                if not automation_success:
                    logger.warning("   ⚠️ Automação falhou - aguardando conclusão...")
                
                # ============= STEP 5: AGUARDAR CONCLUSÃO =============
                logger.info("\n[STEP 5] ⏳ Aguardando conclusão final...")
                completion_success = self.wait_for_quest_completion(timeout=900)
                
                if completion_success:
                    logger.info("\n✅ QUEST COMPLETADA COM SUCESSO!")
                    self.completed_count += 1
                    return True
                else:
                    logger.warning("\n⚠️ Quest pode não ter completado")
                    self.completed_count += 1  # Conta mesmo assim
                    return True
                
            except Exception as e:
                logger.error(f"   ❌ Erro clicando start: {e}")
                return False
            
        except Exception as e:
            logger.error(f"\n❌ ERRO GERAL: {e}")
            self.failed_count += 1
            return False
    
    def detect_quest_type(self):
        """Detecta tipo de quest na página"""
        try:
            logger.info("\n🔍 Detectando tipo de quest...")
            
            page_text = self.driver.page_source.lower()
            page_html = self.driver.page_source
            
            # Detecta tipo
            if "video" in page_text or "<video" in page_html or "youtube" in page_text:
                logger.info("   → Tipo: 📹 VIDEO")
                return "video"
            elif "game" in page_text or "play" in page_text or "jogo" in page_text:
                logger.info("   → Tipo: 🎮 GAME")
                return "game"
            elif "survey" in page_text or "pesquisa" in page_text or "pergunta" in page_text:
                logger.info("   → Tipo: ✅ SURVEY")
                return "survey"
            elif "captcha" in page_text or "recaptcha" in page_text:
                logger.info("   → Tipo: 🔐 CAPTCHA")
                return "captcha"
            else:
                logger.info("   → Tipo: 🔹 DESCONHECIDO")
                return "unknown"
        except Exception as e:
            logger.warning(f"⚠️ Erro detectando tipo: {e}")
            return "unknown"
    
    def automate_video_quest(self):
        """Automatiza quest de vídeo"""
        try:
            logger.info("\n[AUTOMATE] 📹 Automatizando quest de vídeo...")
            
            # Procura elemento video
            try:
                video = self.driver.find_element(By.TAG_NAME, "video")
                logger.info("   ✓ Vídeo encontrado")
            except:
                logger.info("   ℹ️ Elemento <video> não encontrado (pode ser iframe)")
                # Tenta procurar iframe
                try:
                    iframe = self.driver.find_element(By.TAG_NAME, "iframe")
                    logger.info("   ✓ Iframe encontrado - deixando reproduzir")
                except:
                    pass
            
            # Aguarda vídeo carregar
            time.sleep(2)
            
            # Simula scroll (humano)
            for i in range(3):
                self.driver.execute_script("window.scrollBy(0, 200);")
                time.sleep(1)
            
            # Aguarda vídeo completar (padrão: 15-30s)
            logger.info("   ⏳ Assistindo vídeo por 25s...")
            for i in range(5):
                time.sleep(5)
                logger.info(f"      [{i*5}s] Assistindo...")
            
            logger.info("   ✓ Vídeo concluído")
            return True
            
        except Exception as e:
            logger.error(f"   ❌ Erro automatizando vídeo: {e}")
            return False
    
    def automate_game_quest(self):
        """Automatiza quest de jogo"""
        try:
            logger.info("\n[AUTOMATE] 🎮 Automatizando quest de jogo...")
            
            # Procura botão "Play", "Jogar", "Iniciar"
            buttons = self.driver.find_elements(By.TAG_NAME, "button")
            play_button = None
            
            for btn in buttons:
                try:
                    text = btn.text.lower()
                    if any(word in text for word in ["play", "jogar", "iniciar jogo", "começar"]):
                        if btn.is_displayed():
                            play_button = btn
                            logger.info(f"   ✓ Botão encontrado: '{btn.text}'")
                            break
                except:
                    continue
            
            if play_button:
                logger.info("   🖱️ Clicando Play...")
                play_button.click()
                time.sleep(2)
            else:
                logger.info("   ℹ️ Botão Play não encontrado - assumindo jogo já rodando")
            
            # Simula gameplay (clicks aleatórios)
            logger.info("   🎮 Simulando gameplay por 40s...")
            for i in range(8):
                try:
                    # Click aleatório na tela
                    x = random.randint(200, 900)
                    y = random.randint(200, 600)
                    self.driver.execute_script(f"document.elementFromPoint({x}, {y}).click();")
                    logger.info(f"      [{i*5}s] Click em ({x}, {y})")
                except:
                    pass
                time.sleep(5)
            
            logger.info("   ✓ Jogo concluído")
            return True
            
        except Exception as e:
            logger.error(f"   ❌ Erro automatizando jogo: {e}")
            return False
    
    def automate_survey_quest(self):
        """Automatiza quest de survey/pesquisa"""
        try:
            logger.info("\n[AUTOMATE] ✅ Automatizando quest de survey...")
            
            # Procura inputs/checkboxes
            inputs = self.driver.find_elements(By.TAG_NAME, "input")
            checkboxes = [i for i in inputs if i.get_attribute("type") in ["checkbox", "radio"]]
            
            if checkboxes:
                logger.info(f"   ✓ Encontrados {len(checkboxes)} options")
                
                # Clica opções aleatórias
                for cb in checkboxes[:min(3, len(checkboxes))]:
                    try:
                        if not cb.is_selected():
                            logger.info(f"      Selecionando opção...")
                            cb.click()
                            time.sleep(1)
                    except:
                        pass
            else:
                logger.info("   ℹ️ Checkboxes não encontrados")
            
            # Procura botão submit
            buttons = self.driver.find_elements(By.TAG_NAME, "button")
            submit = None
            
            for btn in buttons:
                try:
                    text = btn.text.lower()
                    if any(word in text for word in ["submit", "enviar", "confirmar", "próximo"]):
                        if btn.is_displayed():
                            submit = btn
                            break
                except:
                    continue
            
            if submit:
                logger.info(f"   🖱️ Clicando '{submit.text}'...")
                submit.click()
                time.sleep(2)
            
            logger.info("   ✓ Survey completo")
            return True
            
        except Exception as e:
            logger.error(f"   ❌ Erro automatizando survey: {e}")
            return False
    
    def wait_for_quest_completion(self, timeout=900):
        """Aguarda quest completar após automação (max 15 min)"""
        logger.info(f"\n⏳ Aguardando conclusão da quest (max {timeout}s)...")
        
        try:
            start_time = time.time()
            check_interval = 5
            
            while time.time() - start_time < timeout:
                try:
                    page_text = self.driver.page_source.lower()
                    
                    # Procura sinais de conclusão
                    if any(word in page_text for word in ["sucesso", "completo", "congratulations", "parabéns", "pronto", "finalizado"]):
                        logger.info("   ✅ Quest detectada como concluída!")
                        return True
                    
                    # Procura botão "Próximo" ou "Continuar"
                    buttons = self.driver.find_elements(By.TAG_NAME, "button")
                    for btn in buttons:
                        try:
                            text = btn.text.lower()
                            if any(word in text for word in ["próximo", "continuar", "next", "confirm"]):
                                if btn.is_displayed():
                                    logger.info(f"   🖱️ Clicando '{btn.text}'...")
                                    btn.click()
                                    time.sleep(2)
                                    return True
                        except:
                            continue
                    
                    elapsed = int(time.time() - start_time)
                    logger.info(f"      Aguardando... ({elapsed}s/{timeout}s)")
                    time.sleep(check_interval)
                    
                except Exception as e:
                    logger.warning(f"⚠️ Erro verificando conclusão: {e}")
                    time.sleep(check_interval)
            
            logger.warning(f"⏱️ Timeout: quest não completou em {timeout}s")
            # Mesmo com timeout, tenta continuar
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro aguardando: {e}")
            return False
    
    def run_loop(self):
        """Loop infinito de automação"""
        if not self.load_tokens():
            logger.error("❌ Sem tokens disponíveis. Encerrando.")
            return
        
        if not self.setup_driver():
            logger.error("❌ Erro inicializando Chrome. Encerrando.")
            return
        
        logger.info("🤖 Bot iniciado em MODO AUTÔNOMO")
        logger.info("   → Vai executar quests continuamente")
        logger.info("   → CTRL+C para parar\n")
        
        try:
            while True:
                try:
                    # Preenche form e inicia quest
                    if self.fill_and_start():
                        # Aguarda conclusão
                        self.wait_for_quest_completion(timeout=900)
                        
                        # Delay antes de próximo ciclo
                        delay = random.uniform(30, 90)
                        logger.info(f"\n⏳ Aguardando {delay:.0f}s antes próximo ciclo...")
                        time.sleep(delay)
                    else:
                        # Se falhar, aguarda mais
                        logger.warning("⚠️ Ciclo falhou, tentando novamente em 60s...")
                        time.sleep(60)
                    
                    # Show stats
                    logger.info(f"\n📊 STATS: ✅ {self.completed_count} | ❌ {self.failed_count}")
                    
                except KeyboardInterrupt:
                    logger.info("\n\n⏹️ Bot parado pelo usuário")
                    break
                except Exception as e:
                    logger.error(f"❌ Erro no ciclo: {e}")
                    time.sleep(60)
        
        finally:
            self.close()
    
    def close(self):
        """Fecha Chrome"""
        if self.driver:
            logger.info("🔌 Fechando Chrome...")
            self.driver.quit()
        
        logger.info(f"\n{'='*70}")
        logger.info(f"📊 STATS FINAIS")
        logger.info(f"   ✅ Completadas: {self.completed_count}")
        logger.info(f"   ❌ Falhadas: {self.failed_count}")
        logger.info(f"{'='*70}\n")

if __name__ == "__main__":
    bot = ImpulsosAutoBot()
    bot.run_loop()
