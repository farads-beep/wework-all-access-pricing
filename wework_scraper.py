import asyncio
import re
import requests
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

# Free API for currency conversion
CURRENCY_API = "https://api.frankfurter.app/latest"

# List of known WeWork locales / markets
MARKETS = {
    "US": {"url": "https://www.wework.com/solutions/wework-all-access", "currency": "USD"},
    "UK": {"url": "https://www.wework.com/en-GB/solutions/wework-all-access", "currency": "GBP"},
    "Germany": {"url": "https://www.wework.com/de-DE/solutions/wework-all-access", "currency": "EUR"},
    "France": {"url": "https://www.wework.com/fr-FR/solutions/wework-all-access", "currency": "EUR"},
    "Australia": {"url": "https://www.wework.com/en-AU/solutions/wework-all-access", "currency": "AUD"},
    "Spain": {"url": "https://www.wework.com/es-ES/solutions/wework-all-access", "currency": "EUR"},
    "Italy": {"url": "https://www.wework.com/it-IT/solutions/wework-all-access", "currency": "EUR"},
    "Japan": {"url": "https://www.wework.com/ja-JP/solutions/wework-all-access", "currency": "JPY"},
    "Mexico": {"url": "https://www.wework.com/es-LA/solutions/wework-all-access", "currency": "MXN"},
    "India": {"url": "https://www.wework.co.in/wework-all-access", "currency": "INR"}, 
    "Canada": {"url": "https://www.wework.com/en-CA/solutions/wework-all-access", "currency": "CAD"},
    "Poland": {"url": "https://www.wework.com/pl-PL/solutions/wework-all-access", "currency": "PLN"},
    "Singapore": {"url": "https://www.wework.com/en-SG/solutions/wework-all-access", "currency": "SGD"},
    "Ireland": {"url": "https://www.wework.com/en-IE/solutions/wework-all-access", "currency": "EUR"}
}

def get_exchange_rates():
    """Fetch current exchange rates relative to EUR"""
    print("Fetching live exchange rates...")
    response = requests.get(f"{CURRENCY_API}?from=EUR")
    response.raise_for_status()
    return response.json()['rates']

async def extract_price_from_page(page, url):
    """Navigates to the WeWork locale and tries to extract the monthly price."""
    try:
        await page.goto(url, timeout=60000)
        # Wait for potential pricing elements to load
        await page.wait_for_load_state("networkidle", timeout=15000)
        content = await page.content()
        soup = BeautifulSoup(content, 'html.parser')
        
        # Heuristic: Look for strings matching common price formats
        text_nodes = soup.stripped_strings
        price_pattern = re.compile(
            r'([\€\£\$\¥]|\b(?:USD|GBP|EUR|AUD|JPY|MXN|INR|CAD|PLN|SGD|HKD)\b)\s*([\d\,\.]+)\s*\/\s*(?:mo|month|més|monat)', 
            re.IGNORECASE
        )
        
        for text in text_nodes:
            match = price_pattern.search(text)
            if match:
                # Clean up commas (e.g. 39,000 -> 39000)
                price_str = match.group(2).replace(',', '')
                try:
                    price = float(price_str)
                    if price > 10:  # Skip unreasonably low digits caught by mistake
                        return price
                except ValueError:
                    continue
                    
        return None
    except Exception as e:
        print(f"  Error loading {url}: {e}")
        return None

async def main():
    print("=== WeWork All Access - Global Pricing Scraper ===")
    rates = get_exchange_rates()
    rates["EUR"] = 1.0 # Base currency
    
    results = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        for country, data in MARKETS.items():
            print(f"Scraping {country}...")
            page = await context.new_page()
            local_price = await extract_price_from_page(page, data['url'])
            await page.close()
            
            if local_price:
                currency = data['currency']
                if currency not in rates and currency != "EUR":
                    print(f"  [!] Missing exchange rate for {currency}")
                    continue
                
                # Convert to EUR
                eur_price = local_price if currency == "EUR" else local_price / rates[currency]
                
                results.append({
                    "Country": country,
                    "Local Price": f"{local_price:,.2f} {currency}",
                    "Price in EUR": eur_price
                })
                print(f"  -> Found: {local_price:,.2f} {currency} (~ {eur_price:.2f} EUR)")
            else:
                print(f"  -> Price not found (could be behind a redirect, login, or region block).")
                
        await browser.close()
        
    print("\n=== FINAL RANKING (Cheapest to Most Expensive) ===")
    results.sort(key=lambda x: x["Price in EUR"])
    
    for i, res in enumerate(results, 1):
        print(f"{i}. {res['Country']}: {res['Local Price']} -> €{res['Price in EUR']:.2f}")

if __name__ == "__main__":
    asyncio.run(main())