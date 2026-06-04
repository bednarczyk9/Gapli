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
ACCOUNTS_TO_CREATE = 20
OUTPUT_CSV = os.path.join("allegro_accounts", "accounts_list.csv")
CHROME_PORT = 9222

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 OPR/110.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 OPR/109.0.0.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 17_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; SM-S901B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:124.0) Gecko/20100101 Firefox/124.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 OPR/108.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 OPR/107.0.0.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 14; SM-S911B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 OPR/106.0.0.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 12; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36"
]

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
        indicators = ["nietypowy ruch", "pokaż, że jesteś człowiekiem", "potwierdź, że jesteś człowiekiem", "sprawdź czy nie jesteś robotem", "udowodnij, że nie jesteś robotem"]
        return any(x in content for x in indicators) or page.locator("iframe[title*='reCAPTCHA']").is_visible() or has_iframe
    except:
        return False

def wait_for_captcha(page):
    if is_blocked(page):
        logger.warning("WYKRYTO BLOKADĘ CAPTCHA! Rozwiąż ją ręcznie w oknie przeglądarki.")
        while is_blocked(page):
            time.sleep(5)
        logger.info("Blokada Captcha rozwiązana. Kontynuuję...")
        time.sleep(2)

def register_single_account(account_index):
    logger.info(f"--- Rozpoczynam rejestrację konta nr {account_index + 1} ---")
    
    # 1. Inicjalizacja danych i tworzenie skrzynki Mailcow
    mc = MailcowClient()
    local_part = "acc" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    email = f"{local_part}@bedm.pl"
    mailbox_password = generate_random_password(16) + "!"
    
    logger.info(f"Tworzę skrzynkę w Mailcow: {email}")
    res = mc.create_mailbox(local_part, f"Allegro Account {account_index+1}", mailbox_password)
    
    # Sprawdzenie czy sukces (Mailcow zwraca listę słowników)
    if not (isinstance(res, list) and any(item.get('type') == 'success' for item in res)):
        logger.error(f"Błąd tworzenia skrzynki w Mailcow: {res}")
        return None
    
    logger.info("Skrzynka utworzona pomyślnie.")
    
    # Konfiguracja IMAP dla nowej skrzynki
    tm = PrivateImapMail(user=email, password=mailbox_password, server="mail.bedm.pl")
    tm.current_email = email
    
    password = generate_random_password()
    logger.info(f"Dane konta Allegro: Email: {email}, Hasło: {password}")
    
    # 2. Uruchomienie Chrome
    profile_name = f"chrome-reg-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    user_agent = random.choice(USER_AGENTS)
    logger.info(f"Używam User-Agent: {user_agent}")
    
    cm = ChromeManager(port=CHROME_PORT, profile_name=profile_name, user_agent=user_agent)
    if not cm.start_chrome():
        logger.error("Błąd: Nie udało się uruchomić Chrome.")
        return None

    try:
        with sync_playwright() as p:
            # Połączenie do uruchomionego Chrome
            browser = p.chromium.connect_over_cdp(f"http://127.0.0.1:{CHROME_PORT}")
            context = browser.contexts[0]
            page = context.pages[0] if context.pages else context.new_page()
            
            hi = HumanInteraction(page)
            
            # 3. Nawigacja do rejestracji
            logger.info("Nawiguję do allegro.pl/rejestracja")
            page.goto("https://allegro.pl/rejestracja", wait_until="load", timeout=60000)
            time.sleep(3)
            wait_for_captcha(page)
            
            # Akceptacja cookies jeśli się pojawi
            logger.info("Sprawdzam zgody GDPR/Cookies...")
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
                        btn.click()
                        # Czekamy aż modal zniknie
                        page.wait_for_selector("#opbox-gdpr-consents-modal", state="hidden", timeout=5000)
                        time.sleep(2)
                        break
            except Exception as e:
                logger.debug(f"Brak lub problem z modalem cookies: {e}")

            # Dodatkowy check czy coś jeszcze nie zasłania ekranu
            wait_for_captcha(page)

            # 4. Wypełnianie formularza
            logger.info("Wypełniam formularz rejestracji...")
            
            # Czekamy aż formularz będzie interaktywny
            page.wait_for_selector("label[for='switchToSignup']", timeout=10000)
            time.sleep(0.5)

            # E-mail
            hi.type_like_human("input#email", email)
            
            # Hasło
            hi.type_like_human("input#password", password)
            
            # Mam 18 lat
            page.locator("label:has-text('Mam 18 lat lub więcej')").click()
            time.sleep(random.uniform(0.5, 1.2))
            
            # Regulamin
            page.locator("label:has-text('Oświadczam, że znam i akceptuję postanowienia')").click()
            time.sleep(random.uniform(0.5, 1.0))
            
            # Submit
            logger.info("Klikam 'Załóż konto'")
            page.get_by_role("button", name="Załóż konto").first.click()
            
            time.sleep(5)
            page.screenshot(path="debug_after_register_click.png")
            
            # Sprawdź czy nie ma błędów walidacji
            errors = page.locator("div[data-role='error-message'], .error-text, [role='alert']").all_text_contents()
            if errors:
                logger.error(f"Wykryto błędy na stronie po kliknięciu: {errors}")
            
            wait_for_captcha(page)
            
            # 5. Potwierdzenie e-maila (Browser pozostaje otwarty)
            logger.info("Oczekuję na e-mail z linkiem aktywacyjnym (przeglądarka pozostaje otwarta)...")
            messages = tm.wait_for_email(timeout=180)
            
            if not messages:
                logger.error("Błąd: Nie otrzymano e-maila aktywacyjnego.")
                return None
            
            # Wyciąganie linku - Allegro używa specyficznego formatu
            # Pobieramy całą treść maila (HTML zazwyczaj zawiera lepsze linki)
            email_content = (messages[0].get('mail_html', '') or messages[0].get('mail_text', ''))
            
            # Dekodujemy encje HTML (&amp; -> &) i czyścimy znaki nowej linii QP oraz specyficzne kodowania
            import html
            cleaned_content = html.unescape(email_content).replace('=\n', '').replace('=\r\n', '').replace('=3D', '=')
            
            # Szukamy linku z tokenem i wszystkimi parametrami
            link_match = re.search(r'https://t\.allegro\.pl/rejestracja\?token=[^"\s>]+', cleaned_content)
            
            if not link_match:
                logger.error("Błąd: Nie znaleziono linku aktywacyjnego w e-mailu.")
                # DEBUG: Zapisz treść maila do analizy
                with open(f"debug_email_{local_part}.html", "w", encoding="utf-8") as f:
                    f.write(email_content)
                return None
            
            activation_link = link_match.group(0).strip()
            logger.info(f"Oczyszczony link aktywacyjny: {activation_link}")
            
            logger.info("Otwieram link aktywacyjny w TEJ SAMEJ SESJI...")
            page.goto(activation_link, wait_until="load", timeout=60000)
            time.sleep(10)
            wait_for_captcha(page)
            
            # KROK 1: Obsługa Cookies po otwarciu linku
            
            wait_for_captcha(page)
            
            # Akceptacja cookies jeśli się pojawi
            logger.info("Sprawdzam zgody GDPR/Cookies...")
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
                        btn.click()
                        # Czekamy aż modal zniknie
                        page.wait_for_selector("#opbox-gdpr-consents-modal", state="hidden", timeout=5000)
                        time.sleep(2)
                        break
            except Exception as e:
                logger.debug(f"Brak lub problem z modalem cookies: {e}")

            # Dodatkowy check czy coś jeszcze nie zasłania ekranu
            wait_for_captcha(page)
            page.screenshot(path=f"debug_before_modals_{local_part}.png")

            # KROK 2: WYJDŹ
            logger.info("Krok 2: Czekam na przycisk 'WYJDŹ' (do 15s)...")
            try:
                # Szukamy we wszystkich ramkach
                found = False
                for _ in range(30): # 15 sekund (co 0.5s)
                    for frame in page.frames:
                        try:
                            # Próbujemy znaleźć przycisk z tekstem "WYJD" (case-insensitive)
                            btn = frame.get_by_text(re.compile("WYJD", re.I)).first
                            if btn.is_visible(timeout=500):
                                logger.info(f"Znaleziono 'WYJDŹ' w ramce: {frame.url or 'main'}")
                                btn.click()
                                found = True
                                break
                        except:
                            continue
                    if found: break
                    time.sleep(0.5)
                
                if found:
                    logger.info("Kliknięto 'WYJDŹ'")
                    time.sleep(3)
                else:
                    logger.warning("Nie znaleziono przycisku 'WYJDŹ' w przewidzianym czasie.")
                    page.screenshot(path=f"debug_fail_wyjdz_{local_part}.png")
            except Exception as e:
                logger.error(f"Błąd podczas szukania 'WYJDŹ': {e}")

            # KROK 3: WYCHODZĘ
            logger.info("Krok 3: Czekam na przycisk 'WYCHODZĘ' (do 10s)...")
            try:
                found = False
                for _ in range(20):
                    for frame in page.frames:
                        try:
                            btn = frame.get_by_text(re.compile("WYCHODZ", re.I)).first
                            if btn.is_visible(timeout=500):
                                logger.info(f"Znaleziono 'WYCHODZĘ' w ramce: {frame.url or 'main'}")
                                btn.click()
                                found = True
                                break
                        except:
                            continue
                    if found: break
                    time.sleep(0.5)

                if found:
                    logger.info("Kliknięto 'WYCHODZĘ'")
                    time.sleep(3)
                else:
                    logger.warning("Nie znaleziono przycisku 'WYCHODZĘ'")
                    page.screenshot(path=f"debug_fail_wychodze_{local_part}.png")
            except Exception as e:
                logger.error(f"Błąd podczas szukania 'WYCHODZĘ': {e}")


            # 6. Finalizacja i wylogowanie
            logger.info("Próbuję się wylogować...")
            page.goto("https://allegro.pl/wylogowanie", wait_until="load", timeout=30000)
            time.sleep(3)
            
            # Zapis do CSV
            os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
            file_exists = os.path.isfile(OUTPUT_CSV)
            with open(OUTPUT_CSV, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                if not file_exists:
                    writer.writerow(["Data", "Email", "Haslo_Allegro", "Haslo_Mailbox", "Status"])
                writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), email, password, mailbox_password, "SUCCESS"])
            
            logger.info(f"Sukces! Dane konta zapisane do {OUTPUT_CSV}")
            return True
    
    except Exception as e:
        logger.error(f"Wystąpił nieoczekiwany błąd: {e}")
        return False
    finally:
        cm.kill_chrome()

def main():
    logger.info(f"Rozpoczynam proces tworzenia {ACCOUNTS_TO_CREATE} kont Allegro.")
    
    for i in range(ACCOUNTS_TO_CREATE):
        success = register_single_account(i)
        
        if success:
            logger.info(f"Konto {i+1} utworzone pomyślnie.")
            # Zmiana IP po każdym koncie (lub co N kont)
            logger.info("Resetuję adres IP modemu...")
            reset_modem_ip()
            
            if i < ACCOUNTS_TO_CREATE - 1:
                # Czekaj chwilę przed kolejnym kontem
                delay = random.randint(60, 300)
                logger.info(f"Czekam {delay} sekund przed kolejną rejestracją...")
                time.sleep(delay)
        else:
            logger.error(f"Nie udało się utworzyć konta {i+1}.")
            # Można tu zdecydować czy kontynuować, czy przerwać
            continue

    logger.info("Proces zakończony.")

if __name__ == "__main__":
    main()
