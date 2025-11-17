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

# SUPABASE keys (temporary local)
SUPABASE_URL = "https://mydfflfgggqoliryamtn.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im15ZGZmbGZnZ2dxb2xpcnlhbXRuIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjE2Nzg5NTksImV4cCI6MjA3NzI1NDk1OX0.mVM685NQKkxUV0ja5TZC3jf3uio9HhW6_ugVLHmgb5U"

# Import ArticleTagger
from tagging import ArticleTagger


def scrape_and_tag_articles():
    """Main function to scrape TASS articles and automatically tag them."""

    # Initialize tagger
    tagger = ArticleTagger()

    # Initialize Supabase client
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✓ Connected to Supabase\n")
    except Exception as e:
        print(f"✗ Failed to connect to Supabase: {e}")
        return

    # Setup browser
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        driver.set_page_load_timeout(30)
        wait = WebDriverWait(driver, 10)
        print("✓ Browser initialized successfully\n")
    except WebDriverException as e:
        print(f"✗ Failed to initialize browser: {e}")
        return

    # Load TASS homepage
    try:
        driver.get("https://tass.com")
        print("✓ Page loaded, waiting for content...")
        time.sleep(3)
    except Exception as e:
        print(f"✗ Failed to load main page: {e}")
        driver.quit()
        return

    # Wait for article containers
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "news-list__item"))
        )
        news_items = driver.find_elements(By.CLASS_NAME, "news-list__item")
        print(f"✓ Found {len(news_items)} article containers\n")
    except TimeoutException:
        print("✗ Could not find article elements on page")
        driver.quit()
        return

    # Extract the first 5 articles
    articles = []
    for item in news_items:
        try:
            # Skip empty placeholders
            if not item.find_elements(By.CSS_SELECTOR, "a.news-preview.news-preview_default"):
                continue

            link_element = item.find_element(By.CSS_SELECTOR, "a.news-preview.news-preview_default")
            link = link_element.get_attribute("href")

            title_element = item.find_element(By.CLASS_NAME, "news-preview__title")
            title = title_element.text.strip()

            if link and not link.startswith("http"):
                link = "https://tass.com" + link

            articles.append((title, link))
            print("✓", title)

            if len(articles) == 5:
                break

        except Exception:
            continue

    if len(articles) == 0:
        print("✗ No articles found")
        driver.quit()
        return

    print(f"\n✓ Extracted {len(articles)} articles to process")
    print("=" * 80)

    # RESULTS
    tagged_results = []

    for idx, (title, link) in enumerate(articles, start=1):
        print(f"\n[{idx}/{len(articles)}] Processing: {title[:60]}...")

        try:
            driver.get(link)
            print("    ✓ Page opened, extracting content...")
            time.sleep(2)

            content = []
            try:
                text_content = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "text-content"))
                )
                paragraphs = text_content.find_elements(By.TAG_NAME, "p")
                content = [p.text.strip() for p in paragraphs if p.text.strip()]
                print(f"    ✓ Extracted {len(content)} paragraphs from article")
            except TimeoutException:
                print("    ✗ Could not find article content - skipping")
                continue

            if not content:
                print("    ✗ No usable text extracted - skipping")
                continue

            print("    → Tagging article...")
            tags = tagger.tag_article(content, threshold=2)

            article_data = {
                "title": title,
                "link": link,
                "tags": tags,
                "content": content
            }
            tagged_results.append(article_data)

            try:
                db_data = {
                    "headline": json.dumps({"title": title}),
                    "link": json.dumps({"url": link}),
                    "content": "\n\n".join(content),
                    "tags": tags
                }
                response = supabase.table("Russia_news").insert(db_data).execute()
                print(f"    ✓ Tagged as: {', '.join(tags)}")
                print(f"    ✓ Saved to DB (ID: {response.data[0]['id']})")
            except Exception as e:
                print(f"    ✓ Tagged as: {', '.join(tags)}")
                print(f"    ✗ Database error: {e}")

        except Exception as e:
            print(f"    ✗ Error processing article: {type(e).__name__}")
            continue

    try:
        driver.quit()
        print("\n✓ Browser closed")
    except:
        pass

    print("\n" + "=" * 80)
    print("FINAL RESULTS - TAGGED ARTICLES")
    print("=" * 80)

    for idx, result in enumerate(tagged_results, start=1):
        print(f"\n[{idx}] {result['title']}")
        print(f"    Link: {result['link']}")
        print(f"    Tags: {', '.join(result['tags'])}")
        print(f"    Paragraphs: {len(result['content'])}")

    print("\n" + "=" * 80)
    print(f"Successfully tagged & saved {len(tagged_results)} / {len(articles)} articles")
    print("=" * 80)

    return tagged_results


# ---------- RUN ----------
if __name__ == "__main__":
    scrape_and_tag_articles()
