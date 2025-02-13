import os
import sys
import time
import subprocess
import requests
import shutil
import zipfile

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager

# GitHub repo details
GITHUB_RAW_VERSION_URL = "https://raw.githubusercontent.com/1inam1llion/pywin/main/version.txt"
GITHUB_RAW_SCRIPT_URL = "https://raw.githubusercontent.com/1inam1llion/pywin/main/win10_bootable.py"
LOCAL_VERSION_FILE = "version.txt"
SCRIPT_NAME = "win10_bootable.py"

# Define the virtual environment directory
VENV_DIR = "venv"
REQUIREMENTS = ["selenium", "webdriver-manager", "requests"]


def check_for_updates():
    """Check GitHub for script updates and restart if a new version is available."""
    try:
        print("[INFO] Checking for script updates...")
        
        # Fetch remote version
        response = requests.get(GITHUB_RAW_VERSION_URL, timeout=10)
        response.raise_for_status()
        remote_version = response.text.strip()

        # Read local version
        local_version = "0"
        if os.path.exists(LOCAL_VERSION_FILE):
            with open(LOCAL_VERSION_FILE, "r") as f:
                local_version = f.read().strip()

        print(f"[INFO] Local version: {local_version}, Remote version: {remote_version}")

        # Compare versions
        if remote_version > local_version:
            print("[INFO] New version available. Updating...")

            # Fetch latest script
            response = requests.get(GITHUB_RAW_SCRIPT_URL, timeout=10)
            response.raise_for_status()
            with open(SCRIPT_NAME, "w") as f:
                f.write(response.text)

            # Update version file
            with open(LOCAL_VERSION_FILE, "w") as f:
                f.write(remote_version)

            print("[INFO] Update complete. Restarting script...")
            os.execv(sys.executable, ["python3"] + sys.argv)  # Restart script

        else:
            print("[INFO] You are running the latest version.")

    except Exception as e:
        print(f"[WARNING] Could not check for updates: {e}")


def setup_venv():
    """Ensure the virtual environment is set up and dependencies are installed."""
    if not os.path.exists(VENV_DIR):
        print("[INFO] Setting up virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", VENV_DIR], check=True)

    pip_path = os.path.join(VENV_DIR, "bin", "pip") if os.name != "nt" else os.path.join(VENV_DIR, "Scripts", "pip.exe")

    # Ensure required packages are installed
    subprocess.run([pip_path, "install", "--upgrade"] + REQUIREMENTS, check=True)


def get_webdriver():
    """Automatically installs the correct WebDriver and returns a Selenium WebDriver instance."""
    print("[INFO] Checking and setting up WebDriver...")

    try:
        driver = None

        # Try Chrome
        try:
            service = ChromeService(ChromeDriverManager().install())
            options = webdriver.ChromeOptions()
            options.add_argument("--headless")  # Run in headless mode
            driver = webdriver.Chrome(service=service, options=options)
            print("[INFO] Using Chrome WebDriver.")
            return driver
        except Exception:
            pass  # If Chrome fails, try Firefox

        # Try Firefox
        try:
            service = FirefoxService(GeckoDriverManager().install())
            options = webdriver.FirefoxOptions()
            options.add_argument("--headless")
            driver = webdriver.Firefox(service=service, options=options)
            print("[INFO] Using Firefox WebDriver.")
            return driver
        except Exception as e:
            print(f"[ERROR] Could not set up any WebDriver: {e}")
            sys.exit(1)

    except Exception as e:
        print(f"[ERROR] WebDriver setup failed: {e}")
        sys.exit(1)


def fetch_windows_iso():
    """Fetch the latest Windows 10 ISO download link."""
    print("[INFO] Launching browser to fetch Windows 10 ISO links...")

    driver = get_webdriver()
    driver.get("https://www.microsoft.com/en-us/software-download/windows10ISO")

    try:
        # Wait for the edition selection box to appear
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "product-edition"))
        )

        # Select the edition
        print("[INFO] Available Windows 10 Editions:")
        editions = driver.find_elements(By.CSS_SELECTOR, "#product-edition option")
        for i, edition in enumerate(editions[1:], start=1):
            print(f"{i}. {edition.text}")

        choice = int(input("Select the edition number: ")) - 1
        edition_value = editions[choice + 1].get_attribute("value")

        # Submit edition
        driver.find_element(By.ID, "product-edition").send_keys(edition_value)
        driver.find_element(By.ID, "submit-edition").click()

        # Wait for language selection
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "product-language"))
        )

        # Select language
        print("[INFO] Available languages:")
        languages = driver.find_elements(By.CSS_SELECTOR, "#product-language option")
        for i, lang in enumerate(languages[1:], start=1):
            print(f"{i}. {lang.text}")

        lang_choice = int(input("Select the language number: ")) - 1
        lang_value = languages[lang_choice + 1].get_attribute("value")

        # Submit language
        driver.find_element(By.ID, "product-language").send_keys(lang_value)
        driver.find_element(By.ID, "submit-language").click()

        # Wait for download links
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "download-button"))
        )

        # Extract the actual download link
        download_links = driver.find_elements(By.CLASS_NAME, "download-button")
        for link in download_links:
            href = link.get_attribute("href")
            print(f"[INFO] Windows 10 ISO Download Link: {href}")

        driver.quit()

    except Exception as e:
        print(f"[ERROR] Failed to retrieve ISO link: {e}")
        driver.quit()
        sys.exit(1)


if __name__ == "__main__":
    print("\n[INFO] Windows 10 Bootable USB Creator - v1.0\n")

    check_for_updates()
    setup_venv()
    fetch_windows_iso()

