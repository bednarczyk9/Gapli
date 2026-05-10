import os
import subprocess
import time
import socket
import sys

def kill_chrome():
    print("Zamykam wszystkie instancje Chrome...")
    if sys.platform == "win32":
        subprocess.run(["taskkill", "/F", "/IM", "chrome.exe", "/T"], capture_output=True)
    else:
        subprocess.run(["pkill", "chrome"], capture_output=True)

def is_port_open(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

def get_chrome_path():
    if sys.platform != "win32":
        return "chrome"
    
    paths = [
        os.path.join(os.environ.get("ProgramFiles", "C:\\Program Files"), "Google\\Chrome\\Application\\chrome.exe"),
        os.path.join(os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)"), "Google\\Chrome\\Application\\chrome.exe"),
        os.path.join(os.environ.get("LocalAppData", ""), "Google\\Chrome\\Application\\chrome.exe")
    ]
    
    for path in paths:
        if os.path.exists(path):
            return path
            
    return "chrome.exe" # Fallback to PATH

def main():
    kill_chrome()

    chrome_path = get_chrome_path()
    chrome_profile = os.path.join(os.environ.get("TEMP", "."), "chrome-debug")
    print(f"Uruchamiam Chrome na porcie 9222 z izolowanym profilem: {chrome_profile}")

    chrome_args = [
        chrome_path,
        "--remote-debugging-port=9222",
        f"--user-data-dir={chrome_profile}",
        "--no-first-run",
        "--no-default-browser-check"
    ]

    try:
        subprocess.Popen(chrome_args)
    except FileNotFoundError:
        print("BŁĄD: Nie znaleziono chrome.exe. Upewnij się, że Chrome jest w PATH.")
        return

    print("Czekam na aktywację portu...")
    time.sleep(3)

    if is_port_open(9222):
        print("SUKCES: Chrome słucha na porcie 9222.")
        print("Teraz wejdź na https://gapli.com/login i zaloguj się.")
    else:
        print("BŁĄD: Nie udało się otworzyć portu 9222.")

if __name__ == "__main__":
    main()
