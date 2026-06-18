# Project Gapli - Automated Dropshipping & Market Analysis

Ten projekt to zaawansowany system automatyzujący procesy dropshippingowe przy użyciu platformy Gapli oraz API (i interfejsu) Allegro. Służy do analizy rynku, zarządzania cenami, automatycznego naprawiania błędów katalogowych przy użyciu AI oraz zautomatyzowanego publikowania ofert.

## Struktura Katalogów

Po niedawnej reorganizacji, projekt został podzielony na logiczne sekcje, aby ułatwić zarządzanie kodem i danymi:

```text
Gapli/
├── 📂 accounts/   # Skrypty do zarządzania kontami Allegro i mailami (np. IMAP catch-all)
├── 📂 archive/    # Archiwum: stare wersje skryptów, nieużywane już moduły i narzędzia
├── 📂 data/       # Wszystkie pliki z danymi wejściowymi i wyjściowymi
│   ├── backups/   # Kopie zapasowe (np. postępy analizy)
│   ├── exports/   # Wyeksportowane dane o produktach (np. dla klienta)
│   ├── raw/       # Surowe dane z hurtowni
│   └── reports/   # Raporty Excel (np. raport_OKAZJE, pełne raporty z Playwright)
├── 📂 debug/      # Katalog "brudnopisu": testy API, zrzuty ekranu błędów, skrypty sandboxowe
├── 📂 libs/       # Współdzielony kod, biblioteki i klienty (GapliClient, Allegro API)
├── 📂 pipeline/   # GŁÓWNY SILNIK: Skrypty uruchamiane na co dzień do przetwarzania danych
└── .env.example   # Szablon zmiennych środowiskowych (klucze API, hasła)
```

## Główny Silnik (`pipeline/`)

W folderze `pipeline` znajdują się kluczowe skrypty operacyjne:

*   **Faza analityczna:**
    *   `0_uruchom_wszystko.py` - Skrypt nadrzędny, orkiestrujący całe zadanie.
    *   `1_pobierz_z_gapli.py` - Łączy się z Gapli, pobiera całą bazę hurtowni i wstępnie filtruje (stan magazynowy, minimalna cena).
    *   `2_analizuj_allegro.py` - Wykorzystuje Playwright do sprawdzania cen konkurencji na Allegro dla odfiltrowanych produktów (omija boty m.in. rotując IP modemu i User-Agents).

*   **Faza naprawy i publikacji (Anty-Draft Limit 20k):**
    *   `proactive_repair.py` / `repair_sync_errors_v2.py` - Zapobiega blokadzie limitu 20 000 szkiców na Allegro. Zanim produkt zostanie wysłany, skrypt odpytuje API Allegro o wymogi kategorii, wysyła je do modelu AI (LLM), buduje perfekcyjny opis/parametry i aktualizuje dane w Gapli.
    *   `delete_aleja_drafts_ui.py` - Awaryjne narzędzie oparte na UI (Playwright) do masowego czyszczenia błędnych szkiców z konta, dla których Allegro wyłączyło API usuwania (wymaga manualnej interwencji lub tego skryptu).
    *   `clean_skarbiec_drafts.py` - Próba czyszczenia szkiców przez API (obecnie API Allegro zwraca `403` na starych endpointach).

## Konfiguracja i Uruchomienie

1.  **Zmienne środowiskowe:** Skopiuj plik `.env.example` i zmień jego nazwę na `.env`.
2.  Wypełnij wszystkie potrzebne klucze:
    *   `GAPLI_USER`, `GAPLI_PASS`, `Gapli_Apikey`
    *   Dane IMAP dla prywatnej domeny (do tworzenia kont)
    *   `skarbiec_client_id`, `skarbiec_client_secret` (do komunikacji z API Allegro)
3.  Zainstaluj wymagane pakiety Python: `playwright`, `pandas`, `openpyxl`, `requests`.

**Ważna uwaga (Czerwiec 2026):**
Allegro zablokowało metody API do usuwania szkiców. Masowe wysyłanie niesprawdzonych produktów przez Gapli szybko zapycha limit (20 000) nieaktywnych ofert. Używaj skryptów z rodziny `proactive_repair` przed wysyłką do Allegro!
