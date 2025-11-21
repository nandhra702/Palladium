from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import time, json
from supabase import create_client
from tagging import ArticleTagger

SUPABASE_URL="https://mydfflfgggqoliryamtn.supabase.co"
SUPABASE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im15ZGZmbGZnZ2dxb2xpcnlhbXRuIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjE2Nzg5NTksImV4cCI6MjA3NzI1NDk1OX0.mVM685NQKkxUV0ja5TZC3jf3uio9HhW6_ugVLHmgb5U"


# ----------------------------------------------------------------------
# BROWSER
def get_driver():
    chrome = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    chrome.set_page_load_timeout(30)
    return chrome

# ----------------------------------------------------------------------
# SUPABASE
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def clear_table(table):
    supabase.table(table).delete().neq("id", -1).execute()

def save_to_db(table, title, link, content, tags):
    db_row = {
        "headline": json.dumps({"title": title}),
        "link": json.dumps({"url": link}),
        "content": "\n\n".join(content),
        "tags": tags
    }
    supabase.table(table).insert(db_row).execute()

# ----------------------------------------------------------------------
# MAIN SCRAPING ROUTINE
def scrape_site(config):
    print("\n==============================")
    print(f"▶ Starting: {config['name']}")
    print("==============================")

    tagger = ArticleTagger()
    clear_table(config["table"])

    driver = get_driver()
    driver.get(config["url"])
    time.sleep(3)

    # headline list
    headlines = config["extract_headlines"](driver)
    print(f"✓ Found {len(headlines)} headlines")

    results = []

    for idx, (title, link) in enumerate(headlines, start=1):
        print(f"\n[{idx}] {title}")
        driver.get(link)
        time.sleep(2)

        paragraphs = config["extract_article"](driver)
        if not paragraphs:
            print(" ✗ no text, skipped")
            continue

        tags = tagger.tag_article(paragraphs, threshold=2)
        save_to_db(config["table"], title, link, paragraphs, tags)
        print(f" ✓ saved → tags: {', '.join(tags)}")

        results.append((title, tags, len(paragraphs)))

    driver.quit()
    return results

# ----------------------------------------------------------------------
# WEBSITE-SPECIFIC SELECTORS

def cnn_headlines(driver):
    rows = driver.find_elements(By.CSS_SELECTOR, "li[data-uri]")
    out = []
    for i in rows:
        try:
            title_el = i.find_element(By.CSS_SELECTOR, ".container__headline")
            link_el = i.find_element(By.CSS_SELECTOR, "a.container__link")
            out.append((title_el.text.strip(), link_el.get_attribute("href")))
        except:
            continue
        if len(out) == 10: break
    return out

def cnn_article(driver):
    try:
        body = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.article__content"))
        )
        return [p.text.strip() for p in body.find_elements(By.TAG_NAME, "p") if p.text.strip()]
    except:
        return []

def ndtv_headlines(driver):
    rows = driver.find_elements(By.CLASS_NAME, "NwsLstPg_ttl")
    out = []
    for r in rows:
        try:
            el = r.find_element(By.CSS_SELECTOR, ".NwsLstPg_ttl-lnk")
            out.append((el.text.strip(), el.get_attribute("href")))
        except:
            continue
        if len(out) == 10: break
    return out

def ndtv_article(driver):
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "filteredParagraphs"))
        )
        return [
            p.text.strip()
            for p in driver.find_elements(By.CLASS_NAME, "filteredParagraphs")
            if p.text.strip()
        ]
    except:
        return []

# ----------------------------------------------------------------------
# CONFIG REGISTRY
SITES = [
    {
        "name": "CNN China",
        "url": "https://edition.cnn.com/world/china",
        "table": "China_news",
        "extract_headlines": cnn_headlines,
        "extract_article": cnn_article,
    },
    {
        "name": "NDTV India",
        "url": "https://www.ndtv.com/latest",
        "table": "India_news",
        "extract_headlines": ndtv_headlines,
        "extract_article": ndtv_article,
    }
]

# ----------------------------------------------------------------------
# LAUNCH
if __name__ == "__main__":
    for site in SITES:
        results = scrape_site(site)
        print("\nDONE:", site["name"], "→", len(results), "articles stored\n")
