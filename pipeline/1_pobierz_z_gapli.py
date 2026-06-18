import requests
import pandas as pd
import logging
from datetime import datetime
import os
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

GAPLI_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"

def fetch_all():
    url = 'https://gapli.com/api/products-manager/products'
    headers = {'Authorization': GAPLI_TOKEN}
    all_products = []
    page = 1
    limit = 50
    retries = 0

    logger.info("Pobieranie produktów z Gapli...")
    while True:
        params = {'limit': limit, 'page': page}
        try:
            logger.info(f"Pobieranie strony {page}...")
            resp = requests.get(url, headers=headers, params=params, timeout=90) # Wydłużony timeout do 90 sekund
            if resp.status_code != 200:
                raise requests.exceptions.HTTPError(f"Błąd HTTP: {resp.status_code}")
                
            products = resp.json().get('products', [])
            if not products:
                logger.info("Brak kolejnych produktów na tej stronie. Kończę pobieranie.")
                break
            all_products.extend(products)
            logger.info(f"Pobrano {len(products)} produktów (łącznie: {len(all_products)})")
            page += 1
            retries = 0 # reset po udanym pobraniu
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError, requests.exceptions.HTTPError) as e:
            retries += 1
            if retries <= 5:
                logger.warning(f"Problem na stronie {page} ({e}). Próba ponownego pobrania ({retries}/5) za 10 sekund...")
                time.sleep(10)
                continue
            else:
                logger.error(f"Przekroczono limit prób dla strony {page}. Przerywam pobieranie i zapisuję to co się udało.")
                break
        except Exception as e:
            logger.error(f"Nieznany błąd pobierania: {e}")
            break

    if not all_products:
        return pd.DataFrame()

    df = pd.DataFrame(all_products)

    # Identyfikacja EAN
    col_ean = 'global_unique_id' if 'global_unique_id' in df.columns else None
    if not col_ean:
        for col in df.columns:
            if 'ean' in col.lower():
                col_ean = col
                break

    if not col_ean:
        logger.error("Nie znaleziono kolumny EAN w odpowiedzi z Gapli.")
        return pd.DataFrame()

    # Filtry
    df = df[df[col_ean].notna()]
    
    if 'allegro_blocked' in df.columns:
        df = df[df['allegro_blocked'] == False]
        
    if 'stock_quantity' in df.columns:
        df['stock_quantity'] = pd.to_numeric(df['stock_quantity'], errors='coerce').fillna(0)
        df = df[df['stock_quantity'] >= 5] # Przynajmniej 5 sztuk

    df = df.drop_duplicates(subset=[col_ean])

    # Cena i Zarobek
    price_col = 'sale_net_price' if 'sale_net_price' in df.columns else None
    if not price_col:
        for col in df.columns:
            if 'price' in col.lower() and 'net' in col.lower() and 'sale' in col.lower():
                price_col = col
                break
    
    wholesale_col = 'wholesale_net_price' if 'wholesale_net_price' in df.columns else None

    if price_col:
        df['sale_net_price'] = pd.to_numeric(df[price_col], errors='coerce').fillna(0)
        df['Cena Brutto'] = round(df['sale_net_price'] * 1.23, 2)
        
        # Obliczenie przybliżonego zysku (bez odjęcia prowizji Allegro)
        if wholesale_col:
            df['wholesale_net_price'] = pd.to_numeric(df[wholesale_col], errors='coerce').fillna(0)
            df['Cena Zakupu Brutto'] = round(df['wholesale_net_price'] * 1.23, 2)
            df['Zarobek Brutto (bez prowizji)'] = round(df['Cena Brutto'] - df['Cena Zakupu Brutto'], 2)
        else:
            df['Zarobek Brutto (bez prowizji)'] = 0.0

        # FILTR ZMIENIONY NA 70 ZŁ
        df = df[df['Cena Brutto'] >= 70] 
        df = df.sort_values(by='Cena Brutto', ascending=False)
        
        # Usuwamy mylące kolumny netto, żeby w Excelu były tylko przejrzyste kwoty Brutto
        df = df.drop(columns=[price_col, wholesale_col], errors='ignore')

    return df

def main():
    df = fetch_all()
    if df.empty:
        logger.warning("Brak produktów spełniających nowe kryteria (stan >= 5, cena brutto >= 70).")
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    filename = f"Analityka/baza_gapli_{timestamp}.xlsx"

    # Przygotowanie pustych kolumn dla drugiego skryptu
    df['Najtańszy Allegro'] = ""
    df['Różnica'] = ""
    df['Status'] = ""

    df.to_excel(filename, index=False)
    logger.info(f"Zapisano {len(df)} produktów po przefiltrowaniu (z pobranych). Plik: {filename}")
    logger.info("Możesz teraz uruchomić skrypt 2_analizuj_allegro.py")

if __name__ == "__main__":
    main()
