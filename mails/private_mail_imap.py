import imaplib
import email
import re
import time
import os
import random
import string
import logging
from email.header import decode_header

# Konfiguracja z .env (należy dodać te zmienne)
# IMAP_SERVER = imap.twoj-hosting.pl
# IMAP_USER = catchall@bedm.pl
# IMAP_PASS = twoje-haslo
# MAIL_DOMAIN = bedm.pl

logger = logging.getLogger(__name__)

class PrivateImapMail:
    def __init__(self, server=None, user=None, password=None, domain=None):
        self.server = server or os.getenv("IMAP_SERVER")
        self.user = user or os.getenv("IMAP_USER")
        self.password = password or os.getenv("IMAP_PASS")
        self.domain = domain or os.getenv("MAIL_DOMAIN", "bedm.pl")
        self.current_email = None

    def generate_email(self, username=None):
        """Generuje losowy adres w Twojej domenie."""
        if not username:
            username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        
        self.current_email = f"{username}@{self.domain}"
        return self.current_email

    def _get_connection(self):
        try:
            mail = imaplib.IMAP4_SSL(self.server)
            mail.login(self.user, self.password)
            return mail
        except Exception as e:
            logger.error(f"Błąd połączenia IMAP: {e}")
            return None

    def get_inbox(self, email_address=None):
        """Przeszukuje skrzynkę pod kątem maili do konkretnego adresu."""
        target_email = email_address or self.current_email
        if not target_email:
            return []

        mail = self._get_connection()
        if not mail:
            return []

        messages = []
        try:
            mail.select("inbox")
            # Szukamy maili wysłanych DO naszego tymczasowego adresu
            # Uwaga: Niektóre serwery IMAP mogą wymagać innego zapytania jeśli to catch-all
            # 'TO "adres"' zazwyczaj działa.
            status, data = mail.search(None, f'(TO "{target_email}")')
            
            if status != "OK":
                return []

            mail_ids = data[0].split()
            # Pobieramy 3 najnowsze pasujące maile
            for m_id in mail_ids[-3:]:
                status, msg_data = mail.fetch(m_id, "(RFC822)")
                if status != "OK":
                    continue
                
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        
                        # Ekstrakcja treści
                        body = ""
                        if msg.is_multipart():
                            for part in msg.walk():
                                if part.get_content_type() == "text/plain":
                                    body = part.get_payload(decode=True).decode(errors='ignore')
                                elif part.get_content_type() == "text/html":
                                    # Jeśli nie ma plain text, bierzemy HTML
                                    if not body:
                                        body = part.get_payload(decode=True).decode(errors='ignore')
                        else:
                            body = msg.get_payload(decode=True).decode(errors='ignore')

                        subject, encoding = decode_header(msg["Subject"])[0]
                        if isinstance(subject, bytes):
                            subject = subject.decode(encoding or "utf-8")

                        messages.append({
                            "mail_from": msg["From"],
                            "mail_subject": subject,
                            "mail_text": body,
                            "mail_html": body if "html" in msg.get_content_type() else ""
                        })
            
            return messages[::-1] # Najnowsze pierwsze
        except Exception as e:
            logger.error(f"Błąd podczas pobierania maili IMAP: {e}")
            return []
        finally:
            try:
                mail.logout()
            except:
                pass

    def wait_for_email(self, timeout=180, interval=10):
        """Czeka na maila."""
        if not self.current_email:
            logger.error("Brak adresu e-mail.")
            return []

        logger.info(f"Oczekiwanie na wiadomość na adres: {self.current_email}...")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            messages = self.get_inbox()
            if messages:
                logger.info(f"Otrzymano wiadomość!")
                return messages
            
            time.sleep(interval)
        
        logger.warning("Przekroczono czas oczekiwania na IMAP.")
        return []

if __name__ == "__main__":
    # Szybki test (wymaga ustawienia .env lub zmiennych systemowych)
    logging.basicConfig(level=logging.INFO)
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        logger.info("python-dotenv nie jest zainstalowany, pomijam ładowanie z .env")
    
    pm = PrivateImapMail()
    # Testowo wygeneruj i sprawdź czy w ogóle łączy
    test_email = pm.generate_email("test")
    print(f"Testowy email: {test_email}")
    print("Próbuję połączyć z IMAP...")
    conn = pm._get_connection()
    if conn:
        print("Połączono pomyślnie!")
        conn.logout()
    else:
        print("Błąd połączenia. Sprawdź .env")
