#!/usr/bin/env python3
"""
Mac mini Price Monitor
Fetches prices from Apple Store and Amazon; logs history and alerts on drops.
Run via GitHub Actions (see .github/workflows/mac-mini-monitor.yml).
"""

import json
import logging
import os
import re
import sys
from datetime import datetime, date
from pathlib import Path

import cloudscraper
from bs4 import BeautifulSoup

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).parent
HISTORY_FILE = SCRIPT_DIR / "price_history.json"
LOG_FILE = SCRIPT_DIR / "price_monitor.log"
END_DATE = date(2026, 6, 30)

NOTIFY_EMAIL = os.environ.get("NOTIFY_EMAIL", "vyas0189@gmail.com")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
GITHUB_REPO = os.environ.get("GITHUB_REPOSITORY", "vyas0189/test")

# Mac mini M4 products — SKUs verified against Apple Store (Nov 2024 lineup)
APPLE_PRODUCTS = [
    {
        "name": "Mac mini M4 8GB/256GB",
        "sku": "MYLT3LL/A",
        "expected_price": 599.00,
    },
    {
        "name": "Mac mini M4 16GB/256GB",
        "sku": "MYLY3LL/A",
        "expected_price": 799.00,
    },
    {
        "name": "Mac mini M4 Pro 24GB/512GB",
        "sku": "MYM13LL/A",
        "expected_price": 1299.00,
    },
]

# Amazon ASINs for Mac mini M4 (US listings, Nov 2024)
AMAZON_PRODUCTS = [
    {
        "name": "Mac mini M4 8GB/256GB (Amazon)",
        "asin": "B0DLGXMS71",
        "expected_price": 599.00,
    },
    {
        "name": "Mac mini M4 Pro 24GB/512GB (Amazon)",
        "asin": "B0DLGYQ8ZC",
        "expected_price": 1299.00,
    },
]

# ---------------------------------------------------------------------------
# Logging — append to file and stream to stdout
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# HTTP session (cloudscraper handles TLS fingerprinting + JS challenges)
# ---------------------------------------------------------------------------

def make_scraper():
    scraper = cloudscraper.create_scraper(
        browser={"browser": "chrome", "platform": "darwin", "mobile": False}
    )
    scraper.headers.update({"Accept-Language": "en-US,en;q=0.9"})
    return scraper


# ---------------------------------------------------------------------------
# Apple Store
# ---------------------------------------------------------------------------

def fetch_apple_price(product: dict, scraper) -> dict | None:
    """
    Tries three Apple endpoints in order:
    1. Per-SKU shop product page (JSON-LD + HTML fallback)
    2. The Mac mini overview page (structured data / "From $X" text)
    3. Apple's product feed XML
    """
    sku_enc = product["sku"].replace("/", "%2F")

    # --- Strategy 1: /shop/product/<SKU> ---
    for url in [
        f"https://www.apple.com/shop/product/{sku_enc}",
        f"https://www.apple.com/shop/go/product/{product['sku'].replace('/', '')}",
    ]:
        try:
            resp = scraper.get(url, timeout=20)
            if resp.status_code == 200:
                result = _parse_apple_page(resp.text, url)
                if result:
                    return result
        except Exception as e:
            log.debug("Apple SKU fetch error (%s): %s", url, e)

    # --- Strategy 2: Mac mini overview page ---
    try:
        resp = scraper.get("https://www.apple.com/mac-mini/", timeout=20)
        if resp.status_code == 200:
            result = _parse_apple_page(resp.text, "https://www.apple.com/mac-mini/")
            if result:
                return result
    except Exception as e:
        log.debug("Apple overview fetch error: %s", e)

    # --- Strategy 3: Apple shop buy-mac/mac-mini page ---
    try:
        resp = scraper.get("https://www.apple.com/shop/buy-mac/mac-mini", timeout=20)
        if resp.status_code == 200:
            result = _parse_apple_page(resp.text, "https://www.apple.com/shop/buy-mac/mac-mini")
            if result:
                return result
    except Exception as e:
        log.debug("Apple buy page fetch error: %s", e)

    log.warning("All Apple strategies failed for %s", product["name"])
    return None


def _parse_apple_page(html: str, source_url: str) -> dict | None:
    soup = BeautifulSoup(html, "lxml")

    # JSON-LD structured data
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string or "")
            if isinstance(data, list):
                data = data[0]
            offers = data.get("offers", {})
            if isinstance(offers, list):
                offers = offers[0]
            price_raw = offers.get("price") or offers.get("lowPrice")
            if price_raw:
                return {
                    "price": float(str(price_raw).replace(",", "")),
                    "currency": offers.get("priceCurrency", "USD"),
                    "source": "apple_ld_json",
                    "url": source_url,
                }
        except (json.JSONDecodeError, KeyError, ValueError, TypeError):
            pass

    # Inline JSON state blobs (Next.js / app state)
    for script in soup.find_all("script"):
        text = script.string or ""
        if "mac mini" in text.lower() and '"price"' in text:
            m = re.search(r'"price"\s*:\s*"?\$?([\d,]+\.?\d*)"?', text)
            if m:
                return {
                    "price": float(m.group(1).replace(",", "")),
                    "currency": "USD",
                    "source": "apple_inline_json",
                    "url": source_url,
                }

    # Visible price elements
    for sel in [
        "[data-autom='productPrice']",
        ".rc-prices-currentprice",
        ".current-price",
        ".product-price .current_price",
        ".price",
    ]:
        el = soup.select_one(sel)
        if el:
            m = re.search(r"\$[\d,]+\.?\d*", el.get_text())
            if m:
                return {
                    "price": float(m.group().replace("$", "").replace(",", "")),
                    "currency": "USD",
                    "source": "apple_html_selector",
                    "url": source_url,
                }

    # "From $X" text anywhere on page
    for tag in soup.find_all(string=re.compile(r"From\s*\$[\d,]+")):
        m = re.search(r"\$[\d,]+\.?\d*", tag)
        if m:
            price = float(m.group().replace("$", "").replace(",", ""))
            if 400 < price < 5000:  # sanity range for Mac mini
                return {
                    "price": price,
                    "currency": "USD",
                    "source": "apple_from_text",
                    "url": source_url,
                }

    return None


# ---------------------------------------------------------------------------
# Amazon
# ---------------------------------------------------------------------------

def fetch_amazon_price(product: dict, scraper) -> dict | None:
    url = f"https://www.amazon.com/dp/{product['asin']}"
    try:
        resp = scraper.get(url, timeout=20)
        if resp.status_code != 200:
            log.warning("Amazon returned %d for %s", resp.status_code, product["name"])
            return None

        html = resp.text

        # CAPTCHA detection
        if re.search(r"(Type the characters|robot check|captcha)", html, re.I):
            log.warning("Amazon CAPTCHA triggered for %s — trying mobile URL", product["name"])
            # Retry with mobile URL
            mobile_url = f"https://www.amazon.com/dp/{product['asin']}?m=1"
            resp2 = scraper.get(mobile_url, timeout=20)
            if resp2.status_code == 200:
                html = resp2.text
            else:
                return None

        soup = BeautifulSoup(html, "lxml")

        selectors = [
            "#priceblock_ourprice",
            "#priceblock_dealprice",
            "#priceblock_saleprice",
            "#corePrice_feature_div .a-price .a-offscreen",
            "#apex_desktop .a-price .a-offscreen",
            "#apex_desktop_newAccordionRow .a-price .a-offscreen",
            ".a-price.aok-align-center .a-offscreen",
            ".a-price .a-offscreen",
        ]
        for sel in selectors:
            el = soup.select_one(sel)
            if el:
                text = el.get_text(strip=True)
                m = re.search(r"\$[\d,]+\.?\d*", text)
                if m:
                    price = float(m.group().replace("$", "").replace(",", ""))
                    if 400 < price < 5000:  # sanity range
                        return {
                            "price": price,
                            "currency": "USD",
                            "source": "amazon_html",
                            "url": url,
                        }

        # JSON-LD on Amazon
        for script in soup.find_all("script", type="application/ld+json"):
            try:
                data = json.loads(script.string or "")
                if isinstance(data, list):
                    data = data[0]
                offers = data.get("offers", {})
                if isinstance(offers, list):
                    offers = offers[0]
                price_raw = offers.get("price") or offers.get("lowPrice")
                if price_raw:
                    price = float(str(price_raw).replace(",", ""))
                    if 400 < price < 5000:
                        return {
                            "price": price,
                            "currency": "USD",
                            "source": "amazon_ld_json",
                            "url": url,
                        }
            except (json.JSONDecodeError, KeyError, ValueError, TypeError):
                pass

        log.warning("Could not extract price from Amazon page for %s", product["name"])
    except Exception as e:
        log.warning("Amazon fetch failed for %s: %s", product["name"], e)

    return None


# ---------------------------------------------------------------------------
# Price history
# ---------------------------------------------------------------------------

def load_history() -> dict:
    if HISTORY_FILE.exists():
        try:
            return json.loads(HISTORY_FILE.read_text())
        except json.JSONDecodeError:
            log.error("Corrupt history file; starting fresh")
    return {}


def save_history(history: dict) -> None:
    HISTORY_FILE.write_text(json.dumps(history, indent=2))


def record_price(history: dict, product_name: str, result: dict) -> bool:
    """Add entry; return True if price dropped vs last record."""
    ts = datetime.utcnow().isoformat(timespec="seconds") + "Z"
    entry = {
        "timestamp": ts,
        "price": result["price"],
        "currency": result["currency"],
        "source": result["source"],
        "url": result["url"],
    }
    records = history.setdefault(product_name, [])
    dropped = False
    if records and result["price"] < records[-1]["price"]:
        dropped = True
        log.info(
            "PRICE DROP: %s  $%.2f → $%.2f  (saved $%.2f)",
            product_name,
            records[-1]["price"],
            result["price"],
            records[-1]["price"] - result["price"],
        )
    records.append(entry)
    return dropped


# ---------------------------------------------------------------------------
# GitHub Issue notification (no SMTP required — uses built-in GITHUB_TOKEN)
# ---------------------------------------------------------------------------

def create_github_issue(drops: list[tuple[str, float, float]]) -> None:
    if not GITHUB_TOKEN:
        log.info("GITHUB_TOKEN not set — skipping issue notification")
        return

    import urllib.request

    title = f"Mac mini Price Drop — {datetime.utcnow().strftime('%Y-%m-%d')}"
    lines = ["The following Mac mini prices have dropped:\n"]
    for name, old, new in drops:
        lines.append(f"- **{name}**: ~~${old:.2f}~~ → **${new:.2f}** (save ${old - new:.2f})")
    lines += [
        "",
        f"_Monitored by [mac-mini price monitor](https://github.com/{GITHUB_REPO}/blob/claude/mac-mini-price-monitor-c0vtc3/mac_mini_monitor.py)_",
    ]
    body = "\n".join(lines)

    payload = json.dumps({"title": title, "body": body, "labels": ["price-alert"]}).encode()
    req = urllib.request.Request(
        f"https://api.github.com/repos/{GITHUB_REPO}/issues",
        data=payload,
        headers={
            "Authorization": f"Bearer {GITHUB_TOKEN}",
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            issue = json.loads(resp.read())
            log.info("Created price-drop issue: %s", issue.get("html_url"))
    except Exception as e:
        log.error("Failed to create GitHub issue: %s", e)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    today = date.today()
    if today > END_DATE:
        log.info("Monitoring period ended (%s > %s). Exiting.", today, END_DATE)
        sys.exit(0)

    log.info("=== Mac mini price check — %s ===", today.isoformat())
    scraper = make_scraper()
    history = load_history()
    price_drops: list[tuple[str, float, float]] = []

    checks = (
        [(p, lambda p=p: fetch_apple_price(p, scraper)) for p in APPLE_PRODUCTS]
        + [(p, lambda p=p: fetch_amazon_price(p, scraper)) for p in AMAZON_PRODUCTS]
    )

    for product, fetcher in checks:
        log.info("Checking %s …", product["name"])
        result = fetcher()
        if result is None:
            log.warning("  No price obtained for %s", product["name"])
            continue
        log.info("  $%.2f  (source: %s)", result["price"], result["source"])
        dropped = record_price(history, product["name"], result)
        if dropped:
            records = history[product["name"]]
            price_drops.append((product["name"], records[-2]["price"], result["price"]))

    save_history(history)
    log.info("Price history saved to %s", HISTORY_FILE)

    if price_drops:
        create_github_issue(price_drops)

    # Summary
    log.info("--- Latest prices ---")
    for name, records in history.items():
        if records:
            r = records[-1]
            log.info("  %-45s $%-8.2f  (%s)", name, r["price"], r["timestamp"])

    days_left = (END_DATE - today).days
    log.info("Monitoring active for %d more day(s) (ends %s).", days_left, END_DATE)


if __name__ == "__main__":
    main()
