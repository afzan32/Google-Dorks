import os
import time
import random
import requests
from ddgs import DDGS
from googleapiclient.discovery import build
from datetime import datetime
from colorama import init, Fore
from bs4 import BeautifulSoup
from serpapi import GoogleSearch

init(autoreset=True)
OUTPUT_FILE = "results.txt"
ERROR_FILE = "error.log"

# CONFIGURATION SECTION
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")            # Set your key as environment variable
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")              # Set your Programmable Search Engine ID
BING_API_KEY = os.getenv("BING_API_KEY")                # Set your Bing API key

def bing_search_serpapi(query, num_results=3):
    """Bing Search using SerpAPI."""
    params = {
        "engine": "bing",
        "q": query,
        "api_key": "198734385f04c3718691787ead0b29d059e270dc0f08b1da2041935e0bd23217",
        "count": num_results
    }
    results = []
    try:
        search = GoogleSearch(params)
        data = search.get_dict()
        for result in data.get("organic_results", []):
            link = result.get("link")
            if link:
                results.append(link)
            if len(results) >= num_results:
                break
    except Exception as e:
        print(Fore.RED + f"[!] SerpAPI Bing search error: {e}")
    return results


def google_search(query, num_results=3):
    """Google Custom Search API"""
    try:
        service = build("customsearch", "v1", developerKey="AIzaSyAhjDPsQz65YuwYYwlWsTexTU9ocfoYGag")
        results = []
        res = service.cse().list(q=query, cx="e59ba6f655c8d4a5c", num=num_results).execute()
        for item in res.get('items', []):
            results.append(item['link'])
        return results
    except Exception as e:
        print(Fore.RED + f"[!] Google search error: {e}")
        return []

# def bing_search(query, num_results=3):
#     """Bing Web Search API"""
#     try:
#         url = "https://api.bing.microsoft.com/v7.0/search"
#         headers = {"Ocp-Apim-Subscription-Key": BING_API_KEY}
#         params = {"q": query, "count": num_results}
#         response = requests.get(url, headers=headers, params=params, timeout=10)
#         response.raise_for_status()
#         data = response.json()
#         results = [entry['url'] for entry in data.get('webPages', {}).get('value', [])]
#         return results
#     except Exception as e:
#         print(Fore.RED + f"[!] Bing search error: {e}")
#         return []

def duckduckgo_search(query, num_results=3):
    results = []
    try:
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=num_results):
                if 'href' in r:
                    results.append(r['href'])
        return results
    except Exception as e:
        print(Fore.RED + f"[!] DuckDuckGo search error: {e}")
        return []

def yahoo_search(query, num_results=3):
    """Yahoo Search with anti-blocking tricks."""
    results = []
    headers_list = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15"
    ]
    proxies = [
        "http://149.97.239.166:8080",        
        # Proxy strings like "http://user:pass@host:port" or "socks5://ip:port"
        # Add your proxies here for scaling, or leave empty for direct connection
    ]
    url = f"https://search.yahoo.com/search?p={query}"
    try:
        headers = {"User-Agent": random.choice(headers_list)}
        proxy = {"http": random.choice(proxies)} if proxies else None
        resp = requests.get(url, headers=headers, proxies=proxy, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        for div in soup.find_all('div', class_='dd algo algo-sr Sr'):
            a = div.find('a', href=True)
            if a and a['href'].startswith('http'):
                results.append(a['href'])
            if len(results) >= num_results:
                break
        # Sleep a randomized short time to avoid rate-limiting
        time.sleep(random.uniform(2, 5))
        return results
    except Exception as e:
        print(Fore.RED + f"[!] Yahoo search error: {e}")
        return []

def run_dork_query(dork, num_results=3, delay=10):
    """Run all search engines for a dork."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    engines = [("google", google_search), ("duckduckgo", duckduckgo_search),
               ("bing", bing_search_serpapi), ("yahoo", yahoo_search)]
    for name, func in engines:
        print(Fore.CYAN + f"\n[+] Searching with {name.title()}: {dork} | Time: {timestamp}")
        try:
            with open(OUTPUT_FILE, "a") as f:
                f.write(f"\n[+] Dork: {dork} | Engine: {name} | Time: {timestamp}\n")
                results = func(dork, num_results)
                for url in results:
                    print(Fore.GREEN + url)
                    f.write(url + "\n")
            time.sleep(delay)
        except Exception as e:
            print(Fore.RED + f"[!] Error during {name} search: {e}")
            with open(ERROR_FILE, "a") as err:
                err.write(f"[{timestamp}] Error with dork '{dork}' using {name}: {e}\n")

def main():
    print(Fore.YELLOW + "\n==== Automated Dork Executor (Google + DuckDuckGo + Bing + Yahoo) ====")
    print("1. Run Government Dorks")
    print("2. Run University Dorks")
    choice = input("Choose option (1 or 2): ").strip()
    if choice not in ["1", "2"]:
        print(Fore.RED + "[!] Invalid selection. Please enter 1 or 2.")
        return
    domain_input = input("Enter full domain: ").strip()
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
    print(Fore.BLUE + f"Output successfully saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
