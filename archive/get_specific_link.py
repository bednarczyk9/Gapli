import sys
import os
import re
import html
import logging

# Dodanie ścieżki
sys.path.append(os.getcwd())
from mails.private_mail_imap import PrivateImapMail

logging.basicConfig(level=logging.ERROR)

def get_link(email, password):
    tm = PrivateImapMail(user=email, password=password, server="mail.bedm.pl")
    tm.current_email = email
    msgs = tm.get_inbox()
    if not msgs:
        return "Brak maili w skrzynce."
    
    content = msgs[0].get('mail_html') or msgs[0].get('mail_text', '')
    # Czyścimy znaki nowej linii QP i unescape HTML
    cleaned = html.unescape(content).replace('=\n', '').replace('=\r\n', '').replace('=3D', '=')
    
    match = re.search(r'https://t\.allegro\.pl/rejestracja\?token=[^"\s>]+', cleaned)
    if match:
        return match.group(0).strip()
    return "Nie znaleziono linku w treści maila."

if __name__ == "__main__":
    print(get_link("acctfjsn6mz@bedm.pl", "jOBdJTHvAlRJrPa7!"))
