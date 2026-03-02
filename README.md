# WeWork All Access Global Pricing Scraper

This script automatically queries WeWork domains across different global markets to extract the "All Access" subscription price. It then uses live currency exchange rates to convert all prices to EUR (Euros) to find the cheapest market to buy a subscription.

## Features
- Scrapes multi-region WeWork pages using Playwright to handle dynamically loaded content.
- Normalizes prices using live exchange rates via the free Frankfurter API.
- Ranks the markets from cheapest to most expensive in EUR.

## Requirements
- Python 3.9+
- `playwright`
- `beautifulsoup4`
- `requests`

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/farads-beep/wework-all-access-pricing.git
   cd wework-all-access-pricing
   ```

2. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Install Playwright browsers:
   ```bash
   playwright install chromium
   ```

4. Run the script:
   ```bash
   python wework_scraper.py
   ```