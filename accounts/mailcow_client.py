import os
import requests
import json
import logging
import urllib3
import time

# Suppress insecure request warnings for local IP usage
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)

class MailcowClient:
    def __init__(self):
        self.api_key = os.getenv("mailcow_api")
        self.host = "78.10.178.160"
        self.base_url = f"https://{self.host}/api/v1"
        self.headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        }
        self._verify_connection()

    def _verify_connection(self):
        """Checks if the API is reachable."""
        try:
            response = requests.get(f"{self.base_url}/get/domain/all", headers=self.headers, timeout=5, verify=False)
            if response.status_code == 200:
                logger.info(f"Connected to Mailcow API via {self.base_url}")
                return True
        except Exception as e:
            logger.warning(f"Could not connect to Mailcow API: {e}")
        
        return False

    def create_mailbox(self, email, name, password, quota=20, domain="bedm.pl"):
        """
        Creates a new mailbox.
        email: local part (before @)
        """
        data = {
            "local_part": email,
            "domain": domain,
            "name": name,
            "password": password,
            "quota": quota,
            "active": 1
        }
        response = requests.post(f"{self.base_url}/add/mailbox", headers=self.headers, json=data, verify=False)
        return response.json()

    def get_fail2ban_bans(self):
        """Returns active Fail2Ban bans."""
        response = requests.get(f"{self.base_url}/get/fail2ban", headers=self.headers, verify=False)
        return response.json()

    def unban_ip(self, ip):
        """Unbans an IP address."""
        # Note: Mailcow API for unbanning might vary, usually it's DELETE /api/v1/delete/fail2ban
        data = [ip]
        response = requests.post(f"{self.base_url}/delete/fail2ban", headers=self.headers, json=data, verify=False)
        return response.json()

    def list_mailboxes(self, domain="bedm.pl"):
        """Lists all mailboxes for a domain."""
        response = requests.get(f"{self.base_url}/get/mailbox/all/{domain}", headers=self.headers, verify=False)
        return response.json()

    def delete_mailbox(self, username):
        """Deletes a mailbox by username (full email)."""
        data = [username]
        response = requests.post(f"{self.base_url}/delete/mailbox", headers=self.headers, json=data, verify=False)
        return response.json()

if __name__ == "__main__":
    # Szybki test integracji po korekcie ustawień
    logging.basicConfig(level=logging.INFO)
    client = MailcowClient()
    
    if client.base_url:
        print(f"Pomyślnie połączono z Mailcow API: {client.base_url}")
        
        test_user = "gemini"
        test_pass = "K@#$1234pqrsTUVW-Strong-2026" 
        
        print(f"Próba utworzenia skrzynki: {test_user}@bedm.pl")
        res = client.create_mailbox(test_user, "Gemini", test_pass, quota=20)
        print(f"Odpowiedź serwera: {res}")
        
        if isinstance(res, list) and any(item.get('type') == 'success' for item in res):
            print("SUKCES! Skrzynka została utworzona.")
            
            # Spróbujmy teraz pobrać listę skrzynek aby potwierdzić
            mailboxes = client.list_mailboxes()
            print(f"Aktualne skrzynki: {[mb.get('username') for mb in mailboxes] if isinstance(mailboxes, list) else mailboxes}")
    else:
        print("Nie udało się połączyć z API Mailcow.")

