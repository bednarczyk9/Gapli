import os
import subprocess
import socket
import sys
import time
import logging
import random

class ChromeManager:
    """Class for managing Chrome browser instance with remote debugging."""

    def __init__(self, port=9222, profile_name="chrome-debug", user_agent=None):
        self.port = port
        self.profile_path = os.path.join(os.environ.get("TEMP", "."), profile_name)
        self.user_agent = user_agent
        self.logger = logging.getLogger(__name__)

    def kill_chrome(self):
        """Closes all Chrome instances."""
        self.logger.info("Closing all Chrome instances...")
        if sys.platform == "win32":
            subprocess.run(["taskkill", "/F", "/IM", "chrome.exe", "/T"], capture_output=True)
        else:
            subprocess.run(["pkill", "chrome"], capture_output=True)

    def is_port_open(self):
        """Checks if the remote debugging port is open."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('127.0.0.1', self.port)) == 0

    def get_chrome_path(self):
        """Finds the executable path for Chrome."""
        if sys.platform != "win32":
            return "chrome"
        
        paths = [
            os.path.join(os.environ.get("ProgramFiles", "C:\\Program Files"), 
                         "Google\\Chrome\\Application\\chrome.exe"),
            os.path.join(os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)"), 
                         "Google\\Chrome\\Application\\chrome.exe"),
            os.path.join(os.environ.get("LocalAppData", ""), 
                         "Google\\Chrome\\Application\\chrome.exe")
        ]
        
        for path in paths:
            if os.path.exists(path):
                return path
                
        return "chrome.exe"

    def start_chrome(self):
        """Starts Chrome with remote debugging enabled."""
        self.kill_chrome()

        chrome_path = self.get_chrome_path()
        self.logger.info(f"Starting Chrome on port {self.port} with profile: {self.profile_path}")

        # Randomize resolution a bit
        widths = [1920, 1366, 1536, 1440, 1600]
        heights = [1080, 768, 864, 900, 900]
        idx = random.randint(0, len(widths) - 1)
        res = f"{widths[idx]},{heights[idx]}"

        chrome_args = [
            chrome_path,
            f"--remote-debugging-port={self.port}",
            f"--user-data-dir={self.profile_path}",
            "--no-first-run",
            "--no-default-browser-check",
            f"--window-size={res}",
            "--disable-notifications",
            "--disable-popup-blocking",
            "--disable-save-password-bubble",
            "--disable-infobars",
            "--lang=pl-PL",
            "--disable-features=WebRtcHideLocalIpsWithMdns",
            "--force-color-profile=srgb"
        ]

        if self.user_agent:
            chrome_args.append(f"--user-agent={self.user_agent}")

        try:
            subprocess.Popen(chrome_args)
        except FileNotFoundError:
            self.logger.error("ERROR: chrome.exe not found.")
            return False

        self.logger.info("Waiting for port activation...")
        time.sleep(3)

        if self.is_port_open():
            self.logger.info(f"SUCCESS: Chrome is listening on port {self.port}.")
            return True
        else:
            self.logger.error(f"ERROR: Failed to open port {self.port}.")
            return False
