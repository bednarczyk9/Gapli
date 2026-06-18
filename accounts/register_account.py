import os
import sys
import time
import random
import string
import logging
import re
import csv
from datetime import datetime
from playwright.sync_api import sync_playwright

# Dodanie ścieżki do głównego folderu
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from libraries.chrome_manager import ChromeManager
from libraries.human_interaction import HumanInteraction
from mails.private_mail_imap import PrivateImapMail
from mails.mailcow_client import MailcowClient
from modem.modem_fast import reset_modem_ip

# Konfiguracja logowania
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Parametry
ACCOUNTS_TO_CREATE = 18
OUTPUT_CSV = os.path.join("allegro_accounts", "accounts_list.csv")
CHROME_PORT = 9222

def generate_random_password(length=12):
    """Generuje bezpieczne hasło spełniające wymogi Allegro."""
    chars = string.ascii_lowercase + string.ascii_uppercase + string.digits
    while True:
        password = ''.join(random.choices(chars, k=length))
        if (any(c.islower() for c in password) and 
            any(c.isupper() for c in password) and 
            any(c.isdigit() for c in password)):
            return password

def is_blocked(page):
    try:
        content = page.content().lower()
        has_iframe = False
        for frame in page.frames:
            if "allegrocaptcha.com" in frame.url or "captcha-delivery.com" in frame.url:
                has_iframe = True
                break
        indicators = ["nietypowy ruch", "pokaż, że jesteś człowiekiem", "potwierdź, że jesteś człowiekiem", "sprawdź czy nie jesteś robotem", "udowodnij, że nie jesteś robotem", "zostałeś zablokowany"]
        return any(x in content for x in indicators) or page.locator("iframe[title*='reCAPTCHA']").is_visible() or has_iframe
    except:
        return False

def wait_for_captcha(page):
    if is_blocked(page):
        logger.warning("WYKRYTO BLOKADĘ CAPTCHA! Rozwiąż ją ręcznie.")
        while is_blocked(page):
            time.sleep(5)
        logger.info("Blokada rozwiązana.")
        time.sleep(2)

def handle_cookies(page, hi):
    """Akceptuje zgody cookies jeśli się pojawią."""
    try:
        # Czekamy chwilę na pojawienie się modala
        time.sleep(2)
        
        # Selektory dla przycisków w modalu GDPR
        consent_selectors = [
            "button[data-testid='accept_home_view_action']",
            "button[data-metatestid='accept-event']",
            "button:has-text('Ok, zgadzam się')",
            "button:has-text('Zgadzam się')",
            "button:has-text('PRZEJDŹ DALEJ')",
            "button[data-role='accept-consent']"
        ]
        
        for selector in consent_selectors:
            btn = page.locator(selector).first
            if btn.is_visible(timeout=3000):
                logger.info(f"Klikam przycisk zgody: {selector}")
                hi.move_and_click_like_human(btn)
                # Czekamy aż modal zniknie
                page.wait_for_selector("#opbox-gdpr-consents-modal", state="hidden", timeout=5000)
                time.sleep(1)
                return True
    except Exception as e:
        logger.debug(f"Brak lub problem z modalem cookies: {e}")
    
    # Dodatkowy check czy coś jeszcze nie zasłania ekranu
    wait_for_captcha(page)
    return False

def register_single_account(account_index):
    logger.info(f"--- Rejestracja konta {account_index + 1} ---")
    
    mc = MailcowClient()
    local_part = "acc" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    email = f"{local_part}@bedm.pl"
    mailbox_password = generate_random_password(16) + "!"
    
    logger.info(f"Tworzę skrzynkę: {email}")
    res = mc.create_mailbox(local_part, f"Allegro {account_index+1}", mailbox_password)
    
    if not (isinstance(res, list) and any(item.get('type') == 'success' for item in res)):
        logger.error(f"Błąd Mailcow: {res}")
        return None
    
    tm = PrivateImapMail(user=email, password=mailbox_password, server="mail.bedm.pl")
    tm.current_email = email
    password = generate_random_password()
    
    profile_name = f"Reg_{local_part}"
    cm = ChromeManager(port=CHROME_PORT, profile_name=profile_name)
    if not cm.start_chrome(): return None

    try:
        with sync_playwright() as p:
            browser = p.chromium.connect_over_cdp(f"http://127.0.0.1:{CHROME_PORT}")
            context = browser.contexts[0]
            page = context.pages[0] if context.pages else context.new_page()
            hi = HumanInteraction(page)
            
            page.goto("https://allegro.pl/rejestracja", wait_until="load", timeout=60000)
            time.sleep(3)
            handle_cookies(page, hi)
            wait_for_captcha(page)
            
            # Formularz
            hi.type_like_human("input#email", email)
            hi.type_like_human("input#password", password)
            hi.move_and_click_like_human("label:has-text('Mam 18 lat lub więcej')")
            hi.move_and_click_like_human("label:has-text('Oświadczam, że znam i akceptuję postanowienia')")
            
            logger.info("Klikam 'Załóż konto'")
            hi.move_and_click_like_human(page.get_by_role("button", name="Załóż konto").first)
            time.sleep(5)
            wait_for_captcha(page)
            
            # Aktywacja
            logger.info("Czekam na maila...")
            messages = tm.wait_for_email(timeout=180)
            if not messages: return None
            
            email_content = (messages[0].get('mail_html', '') or messages[0].get('mail_text', ''))
            import html
            cleaned = html.unescape(email_content).replace('=\n', '').replace('=\r\n', '').replace('=3D', '=')
            link_match = re.search(r'https://t\.allegro\.pl/rejestracja\?token=[^"\s>]+', cleaned)
            
            if not link_match: return None
            
            page.goto(link_match.group(0).strip(), wait_until="load", timeout=60000)
            time.sleep(10)
            wait_for_captcha(page)
            
            page.goto("https://allegro.pl/wylogowanie", wait_until="load", timeout=30000)
            
            # Zapis
            os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
            file_exists = os.path.isfile(OUTPUT_CSV)
            with open(OUTPUT_CSV, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                if not file_exists:
                    writer.writerow(["Data", "Email", "Haslo_Allegro", "Haslo_Mailbox", "Status"])
                writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), email, password, mailbox_password, "SUCCESS"])
            
            return True
    except Exception as e:
        logger.error(f"Błąd: {e}")
        return False
    finally:
        cm.kill_chrome()

def main():
    reset_modem_ip()
    for i in range(ACCOUNTS_TO_CREATE):
        if register_single_account(i):
            reset_modem_ip()
            time.sleep(random.randint(60, 300))

if __name__ == "__main__":
    main()
