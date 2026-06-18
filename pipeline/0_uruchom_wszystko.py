import subprocess
import logging
import sys
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    script1 = os.path.join(base_dir, "1_pobierz_z_gapli.py")
    script2 = os.path.join(base_dir, "2_analizuj_allegro.py")
    
    logger.info("=== ETAP 1: Uruchamianie pobierania bazy z Gapli ===")
    try:
        # check=True sprawia, że jeśli skrypt wyrzuci błąd, proces zostanie przerwany
        subprocess.run([sys.executable, script1], check=True)
        logger.info("=== ETAP 1 ZAKOŃCZONY SUKCESEM ===")
    except subprocess.CalledProcessError as e:
        logger.error(f"ETAP 1 zakończył się błędem: {e}. Przerywam pracę.")
        return
        
    logger.info("\n=== ETAP 2: Uruchamianie analizy cen na Allegro ===")
    try:
        subprocess.run([sys.executable, script2], check=True)
        logger.info("=== ETAP 2 ZAKOŃCZONY SUKCESEM ===")
    except subprocess.CalledProcessError as e:
        logger.error(f"ETAP 2 zakończył się błędem: {e}.")
        return
        
    logger.info("\n>>> CAŁKOWITY PROCES ZAKOŃCZONY. Raporty są gotowe w folderze Analityka. <<<")

if __name__ == "__main__":
    main()
