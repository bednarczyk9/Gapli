import re
import os
from openpyxl import Workbook

def extract_wholesalers():
    html_file = 'Recorded/page_dump_main.html'
    if not os.path.exists(html_file):
        print(f"Błąd: Nie znaleziono pliku {html_file}")
        return

    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Szukamy wszystkich opcji w tagach <option>
    options = re.findall(r'<option[^>]*>(.*?)</option>', content)
    
    # Hurtownie zaczynają się po "Hurtownia" i kończą przed "Typ produktu"
    wholesalers = []
    found_start = False
    for opt in options:
        opt = opt.strip()
        if opt == "Hurtownia":
            found_start = True
            continue
        if opt == "Typ produktu":
            break
        if found_start and opt:
            # Przykładowy format: "Action (24142 na stanie) 🟡 57"
            # Wyciągamy nazwę, stan i status
            match = re.match(r'^(.*?)\s*\((\d+)\s*na stanie\)(.*)$', opt)
            if match:
                name = match.group(1).strip()
                stock = int(match.group(2))
                status = match.group(3).strip()
                wholesalers.append([name, stock, status])
            else:
                # Jeśli format jest inny, po prostu dodajemy nazwę
                wholesalers.append([opt, "", ""])

    if not wholesalers:
        print("Nie znaleziono hurtowni w pliku HTML.")
        return

    # Zapis do XLSX
    wb = Workbook()
    ws = wb.active
    ws.title = "Hurtownie Allegro"
    
    # Nagłówki
    ws.append(["Nazwa Hurtowni", "Stan magazynowy", "Status/Dodatkowe info"])
    
    for row in wholesalers:
        ws.append(row)

    output_path = 'Recorded/hurtownie_allegro.xlsx'
    wb.save(output_path)
    print(f"Sukces! Zapisano {len(wholesalers)} hurtowni do pliku: {output_path}")

if __name__ == "__main__":
    extract_wholesalers()
