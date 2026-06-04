import os
import sys
import re
import time
import logging
import quopri
import html
from playwright.sync_api import sync_playwright

# Dodanie ścieżki do głównego folderu
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from libraries.chrome_manager import ChromeManager
from libraries.human_interaction import HumanInteraction
from mails.private_mail_imap import PrivateImapMail

# Konfiguracja logowania
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Dane konta do testu
EMAIL = "accjwcs0zoi@bedm.pl"
MAILBOX_PASS = "IxMygMkyPad8DkkI!"
ALLEGRO_PASS = "0yfa1DJAhIAa"
CHROME_PORT = 9222

def run_activation_test():
    logger.info(f"--- Próba aktywacji z pełnym flow UI dla: {EMAIL} ---")
    
    # 1. Pobranie linku z maila
    tm = PrivateImapMail(user=EMAIL, password=MAILBOX_PASS, server="mail.bedm.pl")
    tm.current_email = EMAIL
    
    logger.info("Łączę się z IMAP po link...")
    messages = tm.get_inbox()
    if not messages:
        logger.error("Brak wiadomości w skrzynce.")
        return

    activation_link = None
    for msg in messages:
        content = (msg.get('mail_html') or msg.get('mail_text') or "")
        cleaned = html.unescape(content).replace('=\n', '').replace('=\r\n', '').replace('=3D', '=')
        link_match = re.search(r'https://t\.allegro\.pl/rejestracja\?token=[^"\s>]+', cleaned)
        if link_match:
            activation_link = link_match.group(0).strip()
            break
            
    if not activation_link:
        logger.error("Nie znaleziono linku aktywacyjnego.")
        return
        
    logger.info(f"Link pobrany: {activation_link}")
    
    # 2. Proces w przeglądarce
    cm = ChromeManager(port=CHROME_PORT, profile_name=f"act-flow-{int(time.time())}")
    cm.start_chrome()
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.connect_over_cdp(f"http://127.0.0.1:{CHROME_PORT}")
            context = browser.contexts[0]
            page = context.pages[0] if context.pages else context.new_page()
            hi = HumanInteraction(page)
            
            # KROK 1: Otwarcie linku i Cookies
            logger.info("Otwieram link aktywacyjny...")
            page.goto(activation_link, wait_until="load", timeout=60000)
            time.sleep(5)
            
            logger.info("Krok 1: Obsługa Cookies ('Zgadzam się')...")
            try:
                cookie_btn = page.locator("button:has-text('Zgadzam się'), button[data-testid='accept_home_view_action']").first
                if cookie_btn.is_visible(timeout=5000):
                    cookie_btn.click()
                    logger.info("Kliknięto 'Zgadzam się'")
                    time.sleep(3)
            except:
                logger.info("Modal cookies nie pojawił się.")

            # Logowanie jeśli potrzebne (Allegro często o to prosi)
            logger.info("Sprawdzam czy wymagane logowanie...")
            login_sel = "input#login, input#email, input[name='login']"
            if page.locator(login_sel).first.is_visible(timeout=5000):
                logger.info("Wymagane logowanie przed aktywacją...")
                # Wybieramy konkretny widoczny selektor
                if page.locator("input#login").is_visible():
                    active_login_sel = "input#login"
                elif page.locator("input#email").is_visible():
                    active_login_sel = "input#email"
                else:
                    active_login_sel = "input[name='login']"

                hi.type_like_human(active_login_sel, EMAIL)
                hi.type_like_human("input#password", ALLEGRO_PASS)
                page.get_by_role("button", name="Zaloguj się").first.click()
                logger.info("Kliknięto 'Zaloguj się', czekam na przeładowanie...")
                time.sleep(10)
                wait_for_captcha(page)

            # KROK 2: WYJDŹ (może pojawić się po aktywacji/logowaniu)
            logger.info("Krok 2: Czekam na przycisk 'WYJDŹ' (do 15s)...")
            try:
                exit_btn = page.locator("button:has-text('WYJDŹ'), [data-role='modal'] >> text='WYJDŹ'").first
                exit_btn.wait_for(state="visible", timeout=15000)
                exit_btn.click()
                logger.info("Kliknięto 'WYJDŹ'")
                time.sleep(3)
            except:
                logger.warning("Nie znaleziono przycisku 'WYJDŹ' w przewidzianym czasie.")

            # KROK 3: WYCHODZĘ
            logger.info("Krok 3: Czekam na przycisk 'WYCHODZĘ' (do 10s)...")
            try:
                leaving_btn = page.locator("button:has-text('WYCHODZĘ'), text='WYCHODZĘ'").first
                leaving_btn.wait_for(state="visible", timeout=10000)
                leaving_btn.click()
                logger.info("Kliknięto 'WYCHODZĘ'")
                time.sleep(3)
            except:
                logger.warning("Nie znaleziono przycisku 'WYCHODZĘ'")

            # KROK 4 & 5: Wylogowanie
            logger.info("Krok 4 & 5: Wylogowanie...")
            page.screenshot(path="debug_before_logout.png")
            
            # Bezpieczniejszy sposób na wylogowanie - bezpośredni URL
            logger.info("Nawiguję bezpośrednio do /wylogowanie...")
            page.goto("https://allegro.pl/wylogowanie", wait_until="load")
            time.sleep(5)

            page.screenshot(path="debug_manual_flow_final.png")
            logger.info("Zrobiono końcowy screenshot: debug_manual_flow_final.png")
            logger.info("Flow zakończony.")
            
    except Exception as e:
        logger.error(f"Błąd główny: {e}")
    finally:
        cm.kill_chrome()

if __name__ == "__main__":
    run_activation_test()
