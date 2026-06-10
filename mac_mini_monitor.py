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

# Shared page cache — buy page is fetched once and reused for all products
_apple_page_cache: dict[str, str] = {}

# Playwright results — populated once per run, keyed by clean SKU (no slashes)
_playwright_apple_prices: dict[str, dict] = {}
_playwright_ran: bool = False


def _init_playwright_apple() -> None:
    """Launch headless Chromium once, load Apple's buy page, extract all product prices."""
    global _playwright_ran
    if _playwright_ran:
        return
    _playwright_ran = True

    try:
        from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
    except ImportError:
        log.warning("playwright not installed — skipping browser-based Apple fetch")
        return

    url = "https://www.apple.com/shop/buy-mac/mac-mini"
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            ctx = browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0.0.0 Safari/537.36"
                ),
                locale="en-US",
                extra_http_headers={"Accept-Language": "en-US,en;q=0.9"},
            )
            page = ctx.new_page()
            log.info("Playwright: loading %s", url)
            page.goto(url, wait_until="load", timeout=30000)

            # Wait up to 15 s for Apple's product tiles to render
            try:
                page.wait_for_selector("[data-part-number]", timeout=15000)
            except PWTimeout:
                log.warning("Playwright: product tiles did not appear; extracting whatever is present")

            # Extract SKU + price from every rendered product tile
            raw = page.evaluate("""
                () => {
                    const out = [];
                    document.querySelectorAll('[data-part-number]').forEach(el => {
                        const sku = (el.getAttribute('data-part-number') || '').replace(/\\//g, '').toUpperCase();
                        const priceEl = el.querySelector(
                            '[data-autom="productPrice"], .rc-prices-currentprice, ' +
                            '.current-price, .price'
                        );
                        out.push({sku, priceText: priceEl ? priceEl.textContent : ''});
                    });
                    return out;
                }
            """)
            log.info("Playwright: %d product tiles found", len(raw))
            for item in raw:
                m = re.search(r"[\d,]+\.?\d*", (item.get("priceText") or "").replace("$", ""))
                if m and item.get("sku"):
                    try:
                        price = float(m.group().replace(",", ""))
                        if 400 < price < 5000:
                            _playwright_apple_prices[item["sku"]] = {
                                "price": price, "currency": "USD",
                                "source": "apple_playwright", "url": url,
                            }
                            log.info("Playwright: %s → $%.2f", item["sku"], price)
                    except ValueError:
                        pass

            # Fallback: try to pull pricing from JS state objects embedded in the page
            if not _playwright_apple_prices:
                log.info("Playwright: no tiles; scanning JS window state")
                for var in ("__STORE_DATA__", "REDUX_STATE", "APP_STATE", "pageLite"):
                    try:
                        blob = page.evaluate(f"() => JSON.stringify(window['{var}'] || null)")
                        if blob and blob != "null":
                            data = json.loads(blob)
                            walker_found: list[dict] = []
                            _walk_json_for_prices(data, walker_found, url)
                            for it in walker_found:
                                if it["sku"]:
                                    _playwright_apple_prices[it["sku"]] = it
                            if walker_found:
                                log.info("Playwright: window.%s → %d prices", var, len(walker_found))
                                break
                    except Exception:
                        pass

            # Last resort: get the fully-rendered HTML and run static parsers on it
            if not _playwright_apple_prices:
                log.info("Playwright: falling back to rendered HTML parsing")
                rendered_html = page.content()
                _apple_page_cache[url] = rendered_html  # update cache with JS-rendered version

            browser.close()
    except Exception as e:
        log.warning("Playwright initialisation failed: %s", e)


def fetch_apple_price(product: dict, scraper) -> dict | None:
    """
    Per-product price lookup — four strategies in priority order:
    0. Playwright headless Chromium (fully-rendered JS page — most accurate)
    1. Individual SKU product pages
    2. Shared buy-mac/mac-mini listing page (static HTML; only default model in JSON-LD)
    3. Mac mini compare page
    4. Overview page
    """
    sku_no_slash = product["sku"].replace("/", "")
    sku_enc = product["sku"].replace("/", "%2F")
    expected = product.get("expected_price", 0.0)

    # Strategy 0: Playwright — runs once, results shared across all products
    _init_playwright_apple()
    sku_clean = product["sku"].replace("/", "").upper()
    if sku_clean in _playwright_apple_prices:
        r = _playwright_apple_prices[sku_clean]
        return {"price": r["price"], "currency": r["currency"],
                "source": r["source"], "url": r["url"]}

    # Strategy 1: individual product pages
    for url in [
        f"https://www.apple.com/shop/product/{sku_no_slash}",
        f"https://www.apple.com/shop/product/{sku_enc}",
        f"https://www.apple.com/shop/go/product/{sku_no_slash}",
    ]:
        html = _apple_fetch_cached(url, scraper)
        if html:
            result = _best_price_match(_collect_all_apple_prices(html, url), product["sku"], expected)
            if result:
                return result

    # Strategy 2: shared buy page (fetched once for all three products)
    buy_url = "https://www.apple.com/shop/buy-mac/mac-mini"
    html = _apple_fetch_cached(buy_url, scraper)
    if html:
        result = _best_price_match(_collect_all_apple_prices(html, buy_url), product["sku"], expected)
        if result:
            return result

    # Strategy 3: Mac mini compare page
    compare_url = "https://www.apple.com/mac-mini/compare/"
    html = _apple_fetch_cached(compare_url, scraper)
    if html:
        result = _best_price_match(_collect_all_apple_prices(html, compare_url), product["sku"], expected)
        if result:
            return result

    # Strategy 4: overview page
    overview_url = "https://www.apple.com/mac-mini/"
    html = _apple_fetch_cached(overview_url, scraper)
    if html:
        result = _best_price_match(_collect_all_apple_prices(html, overview_url), product["sku"], expected)
        if result:
            return result

    log.warning("All Apple strategies exhausted for %s", product["name"])
    return None


def _apple_fetch_cached(url: str, scraper) -> str | None:
    if url not in _apple_page_cache:
        try:
            resp = scraper.get(url, timeout=20)
            log.info("Apple %s -> HTTP %d (%d bytes)", url, resp.status_code, len(resp.text))
            if resp.status_code == 200:
                _apple_page_cache[url] = resp.text
        except Exception as e:
            log.debug("Apple fetch error (%s): %s", url, e)
    return _apple_page_cache.get(url)


def _walk_json_for_prices(obj, found: list, source_url: str, depth: int = 0) -> None:
    """Recursively walk any JSON structure collecting {partNumber, price/amount} pairs."""
    if depth > 15 or not obj:
        return
    if isinstance(obj, dict):
        part = obj.get("partNumber") or obj.get("sku") or obj.get("part_number") or ""
        # Look for price nearby: {"amount": 599}, {"currentPrice": 599}, {"price": 599}
        price = (
            (obj.get("currentPrice") or {}).get("amount")
            or (obj.get("price") or {}).get("currentPrice", {}).get("amount") if isinstance(obj.get("price"), dict) else None
            or obj.get("amount")
            or (obj.get("price") if isinstance(obj.get("price"), (int, float, str)) else None)
        )
        if part and price:
            try:
                found.append({
                    "price": float(str(price).replace(",", "").replace("$", "")),
                    "currency": "USD",
                    "sku": str(part).replace("/", "").upper(),
                    "source": "apple_next_data",
                    "url": source_url,
                })
            except ValueError:
                pass
        for v in obj.values():
            _walk_json_for_prices(v, found, source_url, depth + 1)
    elif isinstance(obj, list):
        for item in obj:
            _walk_json_for_prices(item, found, source_url, depth + 1)


def _collect_all_apple_prices(html: str, source_url: str) -> list[dict]:
    """Extract every distinct price from an Apple page, each tagged with its SKU."""
    found = []
    soup = BeautifulSoup(html, "lxml")

    # __NEXT_DATA__ — Next.js SSR JSON contains full product catalogue for the page
    next_data_tag = soup.find("script", id="__NEXT_DATA__")
    if next_data_tag:
        try:
            nd = json.loads(next_data_tag.string or "")
            _walk_json_for_prices(nd, found, source_url)
            log.info("__NEXT_DATA__ yielded %d price candidates from %s", len(found), source_url)
        except (json.JSONDecodeError, TypeError):
            pass

    # JSON-LD — walk every item and every offer in that item
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            raw = json.loads(script.string or "")
            items = raw if isinstance(raw, list) else [raw]
            for item in items:
                item_sku = (item.get("sku") or "").replace("/", "").upper()
                offers = item.get("offers", {})
                price_entries = offers if isinstance(offers, list) else [offers]
                for offer in price_entries:
                    p = offer.get("price") or offer.get("lowPrice")
                    if not p:
                        continue
                    try:
                        found.append({
                            "price": float(str(p).replace(",", "")),
                            "currency": offer.get("priceCurrency", "USD"),
                            "sku": item_sku,
                            "source": "apple_ld_json",
                            "url": source_url,
                        })
                    except ValueError:
                        pass
        except (json.JSONDecodeError, TypeError):
            pass

    # Inline JS blobs — grab every numeric price near "mac mini"
    for script in soup.find_all("script"):
        text = script.string or ""
        if "mac mini" in text.lower() and '"price"' in text:
            for m in re.finditer(r'"price"\s*:\s*"?\$?([\d,]+\.?\d*)"?', text):
                try:
                    found.append({
                        "price": float(m.group(1).replace(",", "")),
                        "currency": "USD",
                        "sku": "",
                        "source": "apple_inline_json",
                        "url": source_url,
                    })
                except ValueError:
                    pass

    # Visible price elements — collect all, not just first
    for sel in [
        "[data-autom='productPrice']",
        ".rc-prices-currentprice",
        ".current-price",
        ".product-price .current_price",
    ]:
        for el in soup.select(sel):
            m = re.search(r"\$[\d,]+\.?\d*", el.get_text())
            if m:
                try:
                    found.append({
                        "price": float(m.group().replace("$", "").replace(",", "")),
                        "currency": "USD",
                        "sku": "",
                        "source": "apple_html_selector",
                        "url": source_url,
                    })
                except ValueError:
                    pass

    # "From $X" text
    for tag in soup.find_all(string=re.compile(r"From\s*\$[\d,]+")):
        m = re.search(r"\$[\d,]+\.?\d*", tag)
        if m:
            try:
                found.append({
                    "price": float(m.group().replace("$", "").replace(",", "")),
                    "currency": "USD",
                    "sku": "",
                    "source": "apple_from_text",
                    "url": source_url,
                })
            except ValueError:
                pass

    # Product grid tiles on the buy page — each tile usually has a price
    # and a data-part-number / data-product-part attribute with the SKU
    for tile in soup.select(
        "[data-part-number], [data-product-part], "
        ".rf-product-cell, .product-cell, .rf-bfe-cell"
    ):
        sku_attr = (
            tile.get("data-part-number")
            or tile.get("data-product-part")
            or ""
        ).replace("/", "").upper()
        price_el = tile.select_one(
            "[data-autom='productPrice'], .rc-prices-currentprice, "
            ".current-price, .price"
        )
        if price_el:
            m = re.search(r"\$[\d,]+\.?\d*", price_el.get_text())
            if m:
                try:
                    found.append({
                        "price": float(m.group().replace("$", "").replace(",", "")),
                        "currency": "USD",
                        "sku": sku_attr,
                        "source": "apple_tile_html",
                        "url": source_url,
                    })
                except ValueError:
                    pass

    # Apple sometimes embeds a JS variable like:
    # {"partNumber":"MYLT3LLA","price":{"currentPrice":{"amount":599}}}
    for script in soup.find_all("script"):
        text = script.string or ""
        for m in re.finditer(
            r'"partNumber"\s*:\s*"([A-Z0-9]{10,12})"'
            r'.*?"amount"\s*:\s*(\d+)',
            text,
        ):
            try:
                found.append({
                    "price": float(m.group(2)),
                    "currency": "USD",
                    "sku": m.group(1).upper(),
                    "source": "apple_js_partNumber",
                    "url": source_url,
                })
            except ValueError:
                pass

    deduped = {(e["price"], e["sku"]): e for e in found if 400 < e["price"] < 5000}
    return list(deduped.values())


def _best_price_match(prices: list[dict], sku: str, expected: float) -> dict | None:
    """
    Pick the most relevant price from a candidate list:
    1. Exact SKU match (most precise — works when Apple product pages embed SKU in JSON-LD)
    2. Price closest to expected_price within 25% tolerance (buy-page fallback)
    """
    if not prices:
        return None

    sku_clean = sku.replace("/", "").upper()

    for p in prices:
        if p["sku"] == sku_clean:
            return {"price": p["price"], "currency": p["currency"],
                    "source": p["source"], "url": p["url"]}

    if expected > 0:
        best = min(prices, key=lambda x: abs(x["price"] - expected))
        if abs(best["price"] - expected) / expected <= 0.25:
            return {"price": best["price"], "currency": best["currency"],
                    "source": best["source"], "url": best["url"]}

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
