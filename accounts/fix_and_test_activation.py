import os
import sys
import csv
import logging
import re
import time
from playwright.sync_api import sync_playwright

# Dodanie ścieżki do głównego folderu
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mails.private_mail_imap import PrivateImapMail
from libraries.chrome_manager import ChromeManager

# Konfiguracja logowania
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

ACCOUNTS_CSV = os.path.join("allegro_accounts", "accounts_list.csv")
CHROME_PORT = 9222

def test_activation_flow():
    if not os.path.exists(ACCOUNTS_CSV):
        logger.error(f"Nie znaleziono pliku {ACCOUNTS_CSV}")
        return

    accounts = []
    with open(ACCOUNTS_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            accounts.append(row)

    if not accounts:
        logger.error("Brak kont w pliku CSV.")
        return

    # Filtrujemy tylko te konta, które mają Haslo_Mailbox (lub 4 kolumny)
    # Z logów widać, że format to: Data,Email,Haslo_Allegro,Haslo_Mailbox,Status
    # Ale DictReader może mieć problem z nagłówkiem jeśli był dopisywany.

    test_targets = []
    with open(ACCOUNTS_CSV, "r", encoding="utf-8") as f:
        lines = f.readlines()
        for line in lines[-2:]: # Ostatnie dwa
            parts = line.strip().split(',')
            if len(parts) >= 4:
                test_targets.append({
                    'Email': parts[1],
                    'Haslo_Allegro': parts[2],
                    'Haslo_Mailbox': parts[3]
                })

    if not test_targets:
        logger.error("Brak nowych kont z zapisanym hasłem do skrzynki w formacie 4+ kolumn.")
        return
    logger.info(f"Rozpoczynam test aktywacji dla {len(test_targets)} kont.")

    for acc in test_targets:
        email = acc['Email']
        mailbox_pass = acc['Haslo_Mailbox']
        allegro_pass = acc['Haslo_Allegro']

        logger.info(f"--- Testuję konto: {email} ---")

        # 1. Sprawdzamy pocztę
        tm = PrivateImapMail(user=email, password=mailbox_pass, server="mail.bedm.pl")
        tm.current_email = email

        logger.info("Łączę się z IMAP...")
        messages = tm.get_inbox()
        if not messages:
            logger.error("Brak wiadomości w skrzynce.")
            continue

        logger.info(f"Znaleziono {len(messages)} wiadomości.")

        # Szukamy linku
        activation_link = None
        for msg in messages:
            body = msg.get('mail_text', '') + msg.get('mail_html', '')
            link_match = re.search(r'https://t\.allegro\.pl/rejestracja\?token=[a-zA-Z0-9]+', body)
            if link_match:
                activation_link = link_match.group(0)
                break

        if not activation_link:
            logger.error("Nie znaleziono linku aktywacyjnego w odebranych mailach.")
            continue

        logger.info(f"Znaleziono link: {activation_link}")

        # 2. Próba logowania i aktywacji w przeglądarce
        cm = ChromeManager(port=CHROME_PORT, profile_name="test-activation")
        cm.start_chrome()

        try:
            with sync_playwright() as p:
                browser = p.chromium.connect_over_cdp(f"http://127.0.0.1:{CHROME_PORT}")
                context = browser.contexts[0]
                page = context.pages[0] if context.pages else context.new_page()

                # Przejdź do linku
                logger.info("Otwieram link aktywacyjny w przeglądarce...")
                page.goto(activation_link, wait_until="load", timeout=60000)
                time.sleep(5)

                # Spróbuj się zalogować jeśli trzeba
                if "zaloguj" in page.url.lower() or page.locator("input#login").is_visible():
                    logger.info("Wykryto potrzebę logowania. Loguję się...")
                    page.locator("input#login").fill(email)
                    page.locator("input#password").fill(allegro_pass)
                    page.get_by_role("button", name="Zaloguj się").first.click()
                    time.sleep(5)

                page.screenshot(path=f"debug_test_activation_{email}.png")
                logger.info(f"Zrobiono screenshot: debug_test_activation_{email}.png")

                # Sprawdź komunikat o aktywacji
                content = page.content().lower()
                if "konto jest aktywne" in content or "potwierdziliśmy Twój e-mail" in content or "został aktywowany" in content:
                    logger.info("SUKCES: Konto wydaje się być aktywne.")
                else:
                    logger.warning("Nie znaleziono potwierdzenia aktywacji na stronie.")

        except Exception as e:
            logger.error(f"Błąd podczas testu przeglądarki: {e}")
        finally:
            cm.kill_chrome()

    logger.info("Testy zakończone.")


if __name__ == "__main__":
    test_activation_flow()
