import imaplib
import email
import os
import logging
from email.header import decode_header

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def debug_inbox():
    server = os.getenv("IMAP_SERVER")
    user = os.getenv("IMAP_USER")
    password = os.getenv("IMAP_PASS")

    print(f"Łączenie z {server} jako {user}...")
    try:
        mail = imaplib.IMAP4_SSL(server)
        mail.login(user, password)
        mail.select("inbox")

        # Pobierz 10 ostatnich maili bez filtrowania po TO
        status, data = mail.search(None, "ALL")
        if status != "OK":
            print("Błąd search")
            return

        mail_ids = data[0].split()
        print(f"Znaleziono łącznie {len(mail_ids)} wiadomości.")

        for m_id in mail_ids[-10:]:
            status, msg_data = mail.fetch(m_id, "(RFC822)")
            if status != "OK":
                continue
            
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding or "utf-8")
                    
                    to_header = msg.get("To")
                    date_header = msg.get("Date")
                    print(f"ID: {m_id.decode()} | Data: {date_header} | Do: {to_header} | Temat: {subject}")

        mail.logout()
    except Exception as e:
        print(f"Błąd: {e}")

if __name__ == "__main__":
    debug_inbox()
