import requests
from ddgs import DDGS
from datetime import datetime
from colorama import init, Fore
import time
import os
from bs4 import BeautifulSoup
import random
from urllib.parse import quote_plus
import json

# Initialize colorama for colored terminal output
init(autoreset=True)

# Output and error log file paths
OUTPUT_FILE = "results.txt"
ERROR_FILE = "error.log"

# User agents for rotation
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0"
]

# Ensure required files exist
open(OUTPUT_FILE, "a").close()
open(ERROR_FILE, "a").close()

def get_random_headers():
    """Get random headers to avoid detection."""
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive"
    }

def yahoo_search(query, num_results=3):
    """Search Yahoo using requests and BeautifulSoup with improved parsing."""
    headers = get_random_headers()
    results = []
    encoded_query = quote_plus(query)
    url = f"https://search.yahoo.com/search?p={encoded_query}"
    
    try:
        session = requests.Session()
        session.headers.update(headers)
        
        resp = session.get(url, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        
        # Updated selectors for Yahoo search results
        selectors = [
            'div.dd.algo.algo-sr h3 a',
            'div.compTitle h3 a',
            'div.Sr h3 a',
            'h3.title a'
        ]
        
        for selector in selectors:
            links = soup.select(selector)
            for link in links:
                href = link.get('href', '')
                if href and href.startswith('http') and 'yahoo.com' not in href:
                    if href not in results:
                        results.append(href)
                    if len(results) >= num_results:
                        break
            if len(results) >= num_results:
                break
                
    except Exception as e:
        print(Fore.RED + f"[!] Yahoo search error: {e}")
        log_error(f"Yahoo search error for query '{query}': {e}")
    
    return results

def bing_search(query, num_results=3):
    """Search Bing using requests and BeautifulSoup with improved parsing."""
    headers = get_random_headers()
    results = []
    encoded_query = quote_plus(query)
    url = f"https://www.bing.com/search?q={encoded_query}&count={num_results}"
    
    try:
        session = requests.Session()
        session.headers.update(headers)
        
        resp = session.get(url, timeout=15)
        resp.raise_for_status()
        print(resp.text[:1000]) 
        soup = BeautifulSoup(resp.text, "html.parser")
        
        # Updated selectors for Bing search results
        selectors = [
            '#b_results > li > div.b_tpcn > a',
            'li.b_algo h2 a',
            'ol#b_results li h2 a',
            'li.b_algo .b_title a'
        ]
        
        for selector in selectors:
            links = soup.select(selector)
            for link in links:
                href = link.get('href', '')
                if href and href.startswith('http') and 'bing.com' not in href:
                    if href not in results:
                        results.append(href)
                    if len(results) >= num_results:
                        break
            if len(results) >= num_results:
                break
                
    except Exception as e:
        print(Fore.RED + f"[!] Bing search error: {e}")
        log_error(f"Bing search error for query '{query}': {e}")
    
    return results

def duckduckgo_search(query, num_results=3):
    """Search DuckDuckGo using ddgs library."""
    results = []
    try:
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=num_results):
                if 'href' in r:
                    results.append(r['href'])
                elif 'body' in r and 'title' in r:
                    # Some versions return different format
                    results.append(r.get('url', r.get('link', '')))
    except Exception as e:
        print(Fore.RED + f"[!] DuckDuckGo search error: {e}")
        log_error(f"DuckDuckGo search error for query '{query}': {e}")
    return results

def startpage_search(query, num_results=3):
    """Search Startpage as an additional search engine."""
    headers = get_random_headers()
    results = []
    encoded_query = quote_plus(query)
    url = f"https://www.startpage.com/sp/search?query={encoded_query}"
    
    try:
        session = requests.Session()
        session.headers.update(headers)
        
        resp = session.get(url, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        
        # Startpage result selectors
        links = soup.select('a.w-gl__result-title')
        for link in links:
            href = link.get('href', '')
            if href and href.startswith('http'):
                if href not in results:
                    results.append(href)
                if len(results) >= num_results:
                    break
                    
    except Exception as e:
        print(Fore.RED + f"[!] Startpage search error: {e}")
        log_error(f"Startpage search error for query '{query}': {e}")
    
    return results

def log_error(error_msg):
    """Log errors to error file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(ERROR_FILE, "a") as err:
        err.write(f"[{timestamp}] {error_msg}\n")

def run_dork_query(dork, num_results=3, delay=30):
    """Perform a dork query using multiple search engines and log the results."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    engines = {
        "duckduckgo": duckduckgo_search,
        "bing": bing_search,
        "yahoo": yahoo_search,
        "startpage": startpage_search
    }
    
    all_results = []
    
    for engine_name, search_func in engines.items():
        print(Fore.CYAN + f"\n[+] Searching with {engine_name.title()}: {dork} | Time: {timestamp}")
        
        try:
            results = search_func(dork, num_results=num_results)
            
            with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
                f.write(f"\n[+] Dork: {dork} | Engine: {engine_name} | Time: {timestamp}\n")
                f.write(f"Found {len(results)} results:\n")
                
                for url in results:
                    if url:  # Only process non-empty URLs
                        print(Fore.GREEN + url)
                        f.write(url + "\n")
                        all_results.append(url)
                
                f.write("-" * 80 + "\n")
            
            # Random delay between searches to avoid rate limiting
            sleep_time = random.randint(delay, delay + 10)
            print(Fore.YELLOW + f"[*] Waiting {sleep_time} seconds before next search...")
            time.sleep(sleep_time)
            
        except Exception as e:
            print(Fore.RED + f"[!] Error during {engine_name} search: {e}")
            log_error(f"Error with dork '{dork}' using {engine_name}: {e}")
    
    return all_results

def send_whatsapp_message(phone_number, message, file_path=None):
    """Send WhatsApp message using pywhatkit (requires installation)."""
    try:
        import pywhatkit as pwt
        
        # Send message immediately
        pwt.sendwhatmsg_instantly(phone_number, message)
        
        if file_path and os.path.exists(file_path):
            print(Fore.GREEN + f"[+] WhatsApp message sent. Please manually send the file: {file_path}")
        else:
            print(Fore.GREEN + "[+] WhatsApp message sent successfully!")
            
    except ImportError:
        print(Fore.RED + "[!] pywhatkit library not installed. Install with: pip install pywhatkit")
    except Exception as e:
        print(Fore.RED + f"[!] WhatsApp sending error: {e}")

def send_telegram_message(bot_token, chat_id, message, file_path=None):
    """Send Telegram message using bot API."""
    try:
        # Send text message
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }
        
        response = requests.post(url, json=data)
        
        if response.status_code == 200:
            print(Fore.GREEN + "[+] Telegram message sent successfully!")
            
            # Send file if provided
            if file_path and os.path.exists(file_path):
                send_file_url = f"https://api.telegram.org/bot{bot_token}/sendDocument"
                with open(file_path, 'rb') as file:
                    files = {'document': file}
                    file_data = {'chat_id': chat_id}
                    file_response = requests.post(send_file_url, data=file_data, files=files)
                    
                    if file_response.status_code == 200:
                        print(Fore.GREEN + "[+] File sent to Telegram successfully!")
                    else:
                        print(Fore.RED + f"[!] Failed to send file to Telegram: {file_response.text}")
        else:
            print(Fore.RED + f"[!] Failed to send Telegram message: {response.text}")
            
    except Exception as e:
        print(Fore.RED + f"[!] Telegram sending error: {e}")

def create_summary_report():
    """Create a summary report from the results."""
    if not os.path.exists(OUTPUT_FILE):
        return "No results file found."
    
    with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    
    lines = content.split('\n')
    dork_count = len([line for line in lines if line.startswith('[+] Dork:')])
    url_count = len([line for line in lines if line.startswith('http')])
    
    summary = f"""
🔍 **Dorking Operation Summary**

📊 **Statistics:**
• Total Dorks Executed: {dork_count}
• Total URLs Found: {url_count}
• Report Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

📁 **Files:**
• Results: {OUTPUT_FILE}
• Errors: {ERROR_FILE}

⚠️ **Disclaimer:** This tool is for educational and authorized security testing purposes only.
    """
    
    return summary

def main():
    print(Fore.YELLOW + "\n" + "="*60)
    print(Fore.YELLOW + "    ENHANCED AUTOMATED DORKING TOOL")
    print(Fore.YELLOW + "    For Educational & Authorized Testing Only")
    print(Fore.YELLOW + "="*60)
    
    print("\nSelect dorking category:")
    print("1. Run Government Dorks")
    print("2. Run University Dorks")
    print("3. Run Custom Dorks")
    
    choice = input("\nChoose option (1, 2, or 3): ").strip()
    if choice not in ["1", "2", "3"]:
        print(Fore.RED + "[!] Invalid selection. Please enter 1, 2, or 3.")
        return

    domain_input = input("Enter target domain (e.g., example.com): ").strip()
    if not domain_input:
        print(Fore.RED + "[!] Domain input required.")
        return

    # Get number of results per search engine
    try:
        num_results = int(input("Number of results per search engine (default 5): ").strip() or "5")
    except ValueError:
        num_results = 5

    # Get delay between searches
    try:
        delay = int(input("Delay between searches in seconds (default 30): ").strip() or "30")
    except ValueError:
        delay = 30

    if choice == "3":
        print("\nEnter custom dorks (one per line, press Enter twice to finish):")
        custom_dorks = []
        while True:
            dork = input().strip()
            if not dork:
                break
            custom_dorks.append(dork)
        
        if not custom_dorks:
            print(Fore.RED + "[!] No custom dorks provided.")
            return
            
        dorks = custom_dorks
        dork_type = "custom"
    else:
        dork_file = "gov_dorks.txt" if choice == "1" else "uni_dorks.txt"
        if not os.path.exists(dork_file):
            print(Fore.RED + f"[!] Dork file '{dork_file}' not found.")
            return
        
        with open(dork_file, "r") as file:
            dorks = [line.strip() for line in file if line.strip()]
        
        dork_type = "government" if choice == "1" else "university"

    print(Fore.YELLOW + f"\n[+] Starting {dork_type} dorks | Target Domain: {domain_input}")
    print(Fore.YELLOW + f"[+] Total dorks to process: {len(dorks)}")
    print(Fore.YELLOW + f"[+] Results per engine: {num_results}")
    print(Fore.YELLOW + f"[+] Delay between searches: {delay} seconds")
    
    # Clear previous results
    with open(OUTPUT_FILE, "w") as f:
        f.write(f"Dorking Results - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Target Domain: {domain_input}\n")
        f.write(f"Dork Type: {dork_type}\n")
        f.write("="*80 + "\n")

    total_results = 0
    for i, dork_suffix in enumerate(dorks, 1):
        if dork_suffix:
            full_dork = f"site:{domain_input} {dork_suffix}"
            print(Fore.BLUE + f"\n[{i}/{len(dorks)}] Processing: {dork_suffix}")
            results = run_dork_query(full_dork, num_results=num_results, delay=delay)
            total_results += len(results)

    print(Fore.GREEN + f"\n[+] Dorking completed!")
    print(Fore.GREEN + f"[+] Total results found: {total_results}")
    print(Fore.GREEN + f"[+] Results saved to: {OUTPUT_FILE}")

    # Ask about sending results
    send_option = input("\nSend results via (w)hatsapp, (t)elegram, or (n)o: ").strip().lower()
    
    summary = create_summary_report()
    
    if send_option == 'w':
        phone = input("Enter WhatsApp phone number (with country code, e.g., +1234567890): ").strip()
        if phone:
            send_whatsapp_message(phone, summary, OUTPUT_FILE)
    
    elif send_option == 't':
        bot_token = input("Enter Telegram bot token: ").strip()
        chat_id = input("Enter Telegram chat ID: ").strip()
        if bot_token and chat_id:
            send_telegram_message(bot_token, chat_id, summary, OUTPUT_FILE)
    
    print(Fore.BLUE + f"\n[+] Operation completed successfully!")
    print(Fore.YELLOW + "\n⚠️  Remember: Use this tool only for authorized security testing!")

if __name__ == "__main__":
    main()