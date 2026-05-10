import os
import json
from playwright.sync_api import sync_playwright

def extract_info():
    with sync_playwright() as p:
        try:
            print("Próbuję podłączyć się do Chrome (127.0.0.1:9222)...")
            browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
            
            if not browser.contexts:
                print("BŁĄD: Brak aktywnych okien Chrome. Uruchom najpierw 'python start_chrome.py'.")
                return

            context = browser.contexts[0]
            page = context.pages[0] if context.pages else context.new_page()
            
            print(f"Sukces! Podłączono do: {page.url}")
            
            # 1. Zapisywanie HTML
            os.makedirs("Recorded", exist_ok=True)
            html_content = page.content()
            html_filename = "page_dump.html"
            html_path = os.path.join("Recorded", html_filename)
            
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            print(f"1. Zapisano HTML do: {html_path}")

            # 2. Generowanie selektorów JS
            print("Generowanie selektorów dla elementów interaktywnych...")
            
            selectors_script = """
            () => {
                const results = [];
                const seenSelectors = new Set();
                
                // Szukamy elementów, które zazwyczaj chcemy automatyzować
                const elements = document.querySelectorAll('button, input, a, select, textarea, [role="button"], [onclick]');
                
                function getBestSelector(el) {
                    // 1. ID jest najlepsze
                    if (el.id) return `#${el.id}`;
                    
                    // 2. Name dla inputów
                    if (el.getAttribute('name')) {
                        return `${el.tagName.toLowerCase()}[name="${el.getAttribute('name')}"]`;
                    }
                    
                    // 3. Tekst (standard Playwright)
                    const text = el.innerText ? el.innerText.trim() : "";
                    if (text && text.length > 0 && text.length < 50) {
                        return `text="${text.replace(/"/g, '\\\\"')}"`;
                    }
                    
                    // 4. Aria-label lub placeholder
                    if (el.getAttribute('aria-label')) return `[aria-label="${el.getAttribute('aria-label')}"]`;
                    if (el.getAttribute('placeholder')) return `[placeholder="${el.getAttribute('placeholder')}"]`;
                    
                    // 5. Klasy CSS (pierwsze dwie)
                    if (el.className && typeof el.className === 'string') {
                        const classes = el.className.split(/\\s+/).filter(c => c && !c.includes(':')).slice(0, 2).join('.');
                        if (classes) return `${el.tagName.toLowerCase()}.${classes}`;
                    }

                    return el.tagName.toLowerCase();
                }

                elements.forEach((el) => {
                    const rect = el.getBoundingClientRect();
                    // Tylko widoczne elementy
                    if (rect.width > 0 && rect.height > 0) {
                        const selector = getBestSelector(el);
                        
                        // Unikamy duplikatów selektorów dla czytelności
                        if (!seenSelectors.has(selector)) {
                            seenSelectors.add(selector);
                            results.push({
                                tag: el.tagName,
                                text: el.innerText ? el.innerText.trim().substring(0, 40) : "",
                                selector: selector,
                                type: el.type || el.getAttribute('role') || "link/other"
                            });
                        }
                    }
                });
                return results;
            }
            """
            
            elements_data = page.evaluate(selectors_script)
            
            # Zapis do pliku JSON dla łatwiejszego użycia w kodzie
            json_path = os.path.join("Recorded", "selectors.json")
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(elements_data, f, indent=4, ensure_ascii=False)
            
            # Zapis do pliku .js jako stałe (do wklejenia do skryptu)
            js_consts_path = os.path.join("Recorded", "selectors.js")
            with open(js_consts_path, "w", encoding="utf-8") as f:
                f.write("// Wygenerowane selektory dla strony: " + page.url + "\\n")
                f.write("const PAGE_ELEMENTS = {\\n")
                for item in elements_data:
                    # Tworzymy czytelną nazwę klucza
                    clean_name = item['text'] if item['text'] else f"{item['tag']}_{elements_data.index(item)}"
                    clean_name = "".join(filter(str.isalnum, clean_name)).lower()
                    if not clean_name: clean_name = f"element_{elements_data.index(item)}"
                    
                    f.write(f"    {clean_name}: '{item['selector']}', // {item['tag']} - {item['text']}\\n")
                f.write("};\\n")

            print(f"2. Zapisano dane selektorów do: {json_path}")
            print(f"3. Zapisano stałe JS do: {js_consts_path}")
            
            # 4. Screenshot (opcjonalnie, ale pomocne)
            screenshot_path = os.path.join("Recorded", "page_screenshot.png")
            page.screenshot(path=screenshot_path)
            print(f"4. Zapisano zrzut ekranu do: {screenshot_path}")

        except Exception as e:
            print(f"\\nBŁĄD: {e}")

if __name__ == "__main__":
    extract_info()
