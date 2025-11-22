from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
import time
from supabase import create_client
import json

# SUPABASE credentials
SUPABASE_URL="#"
SUPABASE_KEY="#"

# Import ArticleTagger
from tagging import ArticleTagger


def scrape_and_tag_articles():

    tagger = ArticleTagger()

    # connect supabase
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✓ Connected to Supabase\n")
    except Exception as e:
        print(f"✗ Supabase connection error: {e}")
        return

    # browser
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        driver.set_page_load_timeout(30)
        print("✓ Browser initialized\n")
    except WebDriverException as e:
        print(f"✗ Browser error: {e}")
        return

    # ABC AUSTRALIA PAGE
    URL = "https://www.abc.net.au/news/australia"

    try:
        driver.get(URL)
        print("✓ ABC Australia page loaded\n")
        time.sleep(3)
    except Exception as e:
        print(f"✗ Failed to load ABC Australia page: {e}")
        driver.quit()
        return

    # Get article containers <article>
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "article"))
        )
        rows = driver.find_elements(By.CSS_SELECTOR, "article")
        print(f"✓ Found {len(rows)} article blocks\n")
    except TimeoutException:
        print("✗ Could not find any article blocks")
        driver.quit()
        return

    # --- Extract first 5 articles ---
    articles = []

    for row in rows:
        try:
            link_el = row.find_element(By.CSS_SELECTOR, "a[href]")
            link = link_el.get_attribute("href")

            title_el = row.find_element(By.CSS_SELECTOR, "h3")
            title = title_el.text.strip()

            articles.append((title, link))
            print("✓ Article:", title)

            if len(articles) == 5:
                break

        except Exception:
            continue

    if not articles:
        print("✗ No articles extracted")
        driver.quit()
        return

    print("\n✓ Extracted", len(articles), "articles to process")
    print("=" * 80)

    # store results
    tagged_results = []

    # -- PROCESS EACH ARTICLE --
    for idx, (title, link) in enumerate(articles, start=1):
        print(f"\n[{idx}/5] Scraping: {title}")

        try:
            driver.get(link)
            time.sleep(2)

            # TEXT BODY
            try:
                paragraphs_el = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located(
                        (By.CSS_SELECTOR, "p[class^='paragraph_paragraph']")
                    )
                )

                content = [p.text.strip() for p in paragraphs_el if p.text.strip()]

                print(f"    ✓ Extracted {len(content)} paragraphs")

            except TimeoutException:
                print("    ✗ Could not find article body - skipping")
                continue

            if not content:
                print("    ✗ No extractable content - skipping")
                continue

            # TAGGING
            tags = tagger.tag_article(content, threshold=2)

            data = {
                "title": title,
                "link": link,
                "content": content,
                "tags": tags
            }

            tagged_results.append(data)

            # DATABASE INSERT
            try:
                db_row = {
                    "headline": json.dumps({"title": title}),
                    "link": json.dumps({"url": link}),
                    "content": "\n\n".join(content),
                    "tags": tags
                }

                response = supabase.table("Australia_news").insert(db_row).execute()
                print(f"    ✓ Saved to DB (ID: {response.data[0]['id']})")

            except Exception as e:
                print(f"    ✗ DB error: {e}")

        except Exception as e:
            print(f"    ✗ Error: {type(e).__name__}")
            continue

    # close browser
    try:
        driver.quit()
    except:
        pass

    print("\n" + "=" * 80)
    print("FINAL RESULTS")
    print("=" * 80)

    for x in tagged_results:
        print("\nTitle:", x["title"])
        print("Tags:", ", ".join(x["tags"]))
        print("Paragraphs:", len(x["content"]))

    return tagged_results


if __name__ == "__main__":
    scrape_and_tag_articles()
