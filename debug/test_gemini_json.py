import os
import requests
import json
import logging
import re

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

def test_gemini_rewrite():
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={GEMINI_API_KEY}"
    
    name = "Testowy Produkt"
    source_desc = "<p>Super produkt <i>bardzo</i> fajny.</p>"
    
    # Przykładowy kontekst parametrów
    param_context = "WAŻNE: Allegro WYMAGA poniższych parametrów. Wybierz dla nich najbardziej pasujące wartości ze słownika:\n"
    param_context += "- Liczba sztuk w ofercie (ID: 248489). Dozwolone wartości: 1, 2, 3\n"

    prompt = f"""
    Jesteś ekspertem Allegro. Przygotuj PEŁNY PAKIET danych produktu w formacie JSON.
    
    DANE WEJŚCIOWE:
    Nazwa: {name}
    Opis źródłowy: {source_desc}
    
    {param_context}
    
    ZASADY OPISU HTML:
    1. Dozwolone tagi: <h1>, <h2>, <p>, <ul>, <ol>, <li>, <b>, <strong>, <i>, <u>, <em>, <br>, <table>, <tr>, <td>, <th>, <img> (tylko https), <a> (tylko do allegro).
    2. Usuń atrybuty style, class, id.
    3. Opis musi być czytelny, estetyczny i zachęcać do zakupu.
    
    STRUKTURA JSON:
    {{
      "name": "Poprawiona nazwa produktu",
      "description": "Poprawiony kod HTML",
      "parameters": [
        {{ "id": "ID_PARAMETRU", "values": ["WARTOŚĆ"] }}
      ]
    }}
    
    Zwróć TYLKO czysty JSON, bez bloków kodu markdown.
    """
    
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        resp = requests.post(url, json=payload)
        logger.info(f"Status Code: {resp.status_code}")
        
        if resp.status_code == 200:
            data = resp.json()
            if 'candidates' in data and data['candidates']:
                text = data['candidates'][0]['content']['parts'][0]['text']
                logger.info(f"--- RAW RESPONSE ---\n{text}\n--------------------")
                
                # Cleanup and parse
                clean_text = text.strip()
                if clean_text.startswith("```json"):
                    clean_text = clean_text[7:]
                if clean_text.startswith("```"):
                    clean_text = clean_text[3:]
                if clean_text.endswith("```"):
                    clean_text = clean_text[:-3]
                
                clean_text = clean_text.strip()
                
                try:
                    parsed = json.loads(clean_text)
                    logger.info("JSON Parsed Successfully:")
                    logger.info(json.dumps(parsed, indent=2, ensure_ascii=False))
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse JSON: {e}")
                    logger.error(f"Cleaned Text was: {clean_text}")
            else:
                logger.error("No candidates in response")
        else:
            logger.error(f"API Error: {resp.text}")
    except Exception as e:
        logger.error(f"Exception: {e}")

if __name__ == "__main__":
    test_gemini_rewrite()
