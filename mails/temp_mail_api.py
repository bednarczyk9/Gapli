import os
import requests
import hashlib
import time
import random
import string

# Klucz RapidAPI - pobierz z https://rapidapi.com/privatix/api/temp-mail
# Możesz ustawić zmienną środowiskową RAPIDAPI_KEY lub wpisać klucz poniżej
RAPIDAPI_KEY = os.getenv("temp_mail_api")
HOST = "privatix-temp-mail-v1.p.rapidapi.com"

class TempMailAPI:
    def __init__(self, api_key=None):
        self.api_key = api_key or RAPIDAPI_KEY
        self.headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": HOST
        }
        self.current_email = None

    def get_domains(self):
        """Pobiera listę dostępnych domen dla e-maili tymczasowych."""
        url = f"https://{HOST}/request/domains/"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Błąd podczas pobierania domen: {e}")
            return []

    def generate_email(self, username=None):
        """Generuje nowy adres e-mail."""
        domains = self.get_domains()
        if not domains:
            return None
        
        if not username:
            # Generuj losowy login (8 znaków)
            username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        
        domain = domains[0] # Używamy pierwszej dostępnej domeny
        self.current_email = f"{username}{domain}"
        return self.current_email

    def get_inbox(self, email_address=None):
        """Sprawdza skrzynkę odbiorczą dla danego adresu."""
        email = email_address or self.current_email
        if not email:
            print("Brak adresu e-mail do sprawdzenia.")
            return []

        # API wymaga skrótu MD5 adresu e-mail
        email_hash = hashlib.md5(email.encode()).hexdigest()
        url = f"https://{HOST}/request/mail/id/{email_hash}/"
        
        try:
            response = requests.get(url, headers=self.headers)
            # API zwraca błąd 404 (lub dict z błędem) jeśli skrzynka jest pusta
            if response.status_code == 404:
                return []
            
            data = response.json()
            if isinstance(data, dict) and "error" in data:
                return []
            
            return data
        except Exception as e:
            print(f"Błąd podczas pobierania wiadomości: {e}")
            return []

    def wait_for_email(self, timeout=120, interval=5):
        """Czeka na pojawienie się e-maila w skrzynce."""
        if not self.current_email:
            print("Najpierw wygeneruj adres e-mail (generate_email()).")
            return None

        print(f"Oczekiwanie na wiadomość na adres: {self.current_email}...")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            messages = self.get_inbox()
            if messages and len(messages) > 0:
                print(f"Otrzymano {len(messages)} wiadomość(i)!")
                return messages
            
            time.sleep(interval)
        
        print("Przekroczono czas oczekiwania (timeout).")
        return []

if __name__ == "__main__":
    # Testowanie skryptu
    print("--- Test Temp-Mail API ---")
    
    # Sprawdzenie czy klucz jest ustawiony
    if RAPIDAPI_KEY == "TWOJ_KLUCZ_RAPIDAPI_TUTAJ":
        print("UWAGA: Nie ustawiono klucza RAPIDAPI_KEY. Skrypt może nie działać.")
        print("Zdobądź klucz na: https://rapidapi.com/privatix/api/temp-mail")
    
    tm = TempMailAPI()
    email = tm.generate_email()
    
    if email:
        print(f"Wygenerowany adres: {email}")
        print("Możesz teraz wysłać testowy e-mail na ten adres.")
        print("Czekam 60 sekund na wiadomość...")
        
        messages = tm.wait_for_email(timeout=60)
        
        for msg in messages:
            print("\n" + "="*50)
            print(f"Od: {msg.get('mail_from')}")
            print(f"Temat: {msg.get('mail_subject')}")
            print("-" * 20)
            # Wyświetlamy początek treści
            text = msg.get('mail_text', 'Brak treści tekstowej')
            print(f"Treść (fragment): {text[:200]}...")
            print("="*50)
    else:
        print("Nie udało się wygenerować adresu e-mail.")
