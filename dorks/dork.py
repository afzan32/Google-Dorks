from googlesearch import search
from ddgs import DDGS
from datetime import datetime
from colorama import init, Fore
import time
import os
import requests
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from bs4 import BeautifulSoup

# Initialize colorama for colored terminal output
init(autoreset=True)

# Output and error log file paths
OUTPUT_FILE = "results.txt"
ERROR_FILE = "error.log"

# Ensure required files exist
open(OUTPUT_FILE, "a").close()
open(ERROR_FILE, "a").close()
def yahoo_search(query, num_results=3):
    """Search Yahoo using requests and BeautifulSoup."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    results = []
    url = f"https://search.yahoo.com/search?p={query}"
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        for div in soup.find_all('div', class_='dd algo algo-sr Sr'):
            a = div.find('a', href=True)
            if a and a['href'].startswith('http'):
                results.append(a['href'])
            if len(results) >= num_results:
                break
    except Exception as e:
        print(Fore.RED + f"[!] Yahoo search error: {e}")
    return results

def bing_search(query, num_results=3):
    """Search Bing using requests and BeautifulSoup (no Selenium)."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    results = []
    url = f"https://www.bing.com/search?q={query}&count={num_results}"
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        for li in soup.find_all('li', class_='b_algo'):
            a = li.find('a', href=True)
            if a and a['href'].startswith('http'):
                results.append(a['href'])
            if len(results) >= num_results:
                break
    except Exception as e:
        print(Fore.RED + f"[!] Bing search error: {e}")
    return results

def google_search(query, num_results=3):
    """Search Google using googlesearch library."""
    try:
        return list(search(query, num_results=num_results))
    except Exception as e:
        print(Fore.RED + f"[!] Google search error: {e}")
        return []

def duckduckgo_search(query, num_results=3):
    """Search DuckDuckGo using ddgs library."""
    results = []
    try:
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=num_results):
                if 'href' in r:
                    results.append(r['href'])
    except Exception as e:
        print(Fore.RED + f"[!] DuckDuckGo search error: {e}")
    return results

def run_dork_query(dork, num_results=3, delay=30):
    """Perform a dork query using Google, DuckDuckGo, and Bing, and log the results."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    engines = ["google", "duckduckgo", "bing", "yahoo"]

    for engine in engines:
        print(Fore.CYAN + f"\n[+] Searching with {engine.title()}: {dork} | Time: {timestamp}")
        try:
            with open(OUTPUT_FILE, "a") as f:
                f.write(f"\n[+] Dork: {dork} | Engine: {engine} | Time: {timestamp}\n")

                if engine == "google":
                    results = google_search(dork, num_results=num_results)
                elif engine == "duckduckgo":
                    results = duckduckgo_search(dork, num_results=num_results)
                elif engine == "bing":
                    results = bing_search_selenium(dork, num_results=num_results)
                elif engine == "yahoo":
                    results = yahoo_search(dork, num_results=num_results)
                else:
                    results = []

                for url in results:
                    print(Fore.GREEN + url)
                    f.write(url + "\n")

            time.sleep(delay)  # Delay between engine searches

        except Exception as e:
            print(Fore.RED + f"[!] Error during {engine} search: {e}")
            with open(ERROR_FILE, "a") as err:
                err.write(f"[{timestamp}] Error with dork '{dork}' using {engine}: {e}\n")

def main():
    print(Fore.YELLOW + "\n==== Automated Dork Executor (Google + DuckDuckGo + Bing) ====")
    print("1. Run Government Dorks")
    print("2. Run University Dorks")
    
    choice = input("Choose option (1 or 2): ").strip()
    if choice not in ["1", "2"]:
        print(Fore.RED + "[!] Invalid selection. Please enter 1 or 2.")
        return

    domain_input = input("Enter full domain : ").strip()
    if not domain_input:
        print(Fore.RED + "[!] Domain input required.")
        return

    dork_file = "gov_dorks.txt" if choice == "1" else "uni_dorks.txt"
    if not os.path.exists(dork_file):
        print(Fore.RED + f"[!] Dork file '{dork_file}' not found.")
        return

    print(Fore.YELLOW + f"\n[+] Running dorks from: {dork_file} | Target Domain: {domain_input}")
    with open(dork_file, "r") as file:
        for line in file:
            dork_suffix = line.strip()
            if dork_suffix:
                full_dork = f"site:{domain_input} {dork_suffix}"
                run_dork_query(full_dork)

    print(Fore.BLUE + "Output successfully saved to results.txt")

# Run the main function
if __name__ == "__main__":
    main()

# After all dorking is done, send results via email
# import mail_sender
# mail_sender.send_email()