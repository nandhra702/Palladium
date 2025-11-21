from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
import time
from supabase import create_client
import json


# Import ArticleTagger
from tagging import ArticleTagger

SUPABASE_URL="https://mydfflfgggqoliryamtn.supabase.co"
SUPABASE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im15ZGZmbGZnZ2dxb2xpcnlhbXRuIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjE2Nzg5NTksImV4cCI6MjA3NzI1NDk1OX0.mVM685NQKkxUV0ja5TZC3jf3uio9HhW6_ugVLHmgb5U"


def create_driver():
    """Create a fresh Chrome driver with optimized settings."""
    chrome_options = Options()
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-infobars')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # Reduce memory usage
    chrome_options.add_argument('--disable-images')
    chrome_options.add_argument('--blink-settings=imagesEnabled=false')
    
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )
    driver.set_page_load_timeout(20)  # Reduced from 30
    return driver


def safe_get_page(driver, url, max_retries=2):
    """Safely load a page with timeout handling and retries."""
    for attempt in range(max_retries):
        try:
            driver.get(url)
            time.sleep(1.5)
            return True
        except TimeoutException:
            print(f"    ⚠ Timeout on attempt {attempt + 1}/{max_retries}")
            if attempt < max_retries - 1:
                try:
                    driver.execute_script("window.stop();")
                except:
                    pass
                time.sleep(1)
            else:
                return False
        except Exception as e:
            print(f"    ✗ Error loading page: {type(e).__name__}")
            return False
    return False


def extract_article_content(driver):
    """Extract article content with multiple fallback strategies."""
    content = []
    
    # Strategy 1: Try specific NDTV selectors
    selectors = [
        "div.sp_txt p",
        "div.story__content p",
        "div.story_content p",
        "div[class*='story'] p"
    ]
    
    for selector in selectors:
        try:
            elements = WebDriverWait(driver, 3).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector))
            )
            temp_content = [p.text.strip() for p in elements if p.text.strip()]
            
            if len(temp_content) >= 3:  # At least 3 paragraphs
                content = temp_content
                print(f"    ✓ Found {len(content)} paragraphs ({selector})")
                return content
        except:
            continue
    
    # Strategy 2: Fallback to all paragraphs
    if not content:
        try:
            all_paragraphs = driver.find_elements(By.TAG_NAME, "p")
            content = [p.text.strip() for p in all_paragraphs 
                      if p.text.strip() and len(p.text.strip()) > 50]
            if len(content) >= 3:
                print(f"    ✓ Found {len(content)} paragraphs (fallback)")
                return content
        except:
            pass
    
    return content


def scrape_and_tag_articles():
    """Main function to scrape NDTV articles and automatically tag them."""

    # Initialize tagger
    tagger = ArticleTagger()

    # Initialize Supabase client
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✓ Connected to Supabase\n")
    except Exception as e:
        print(f"✗ Failed to connect to Supabase: {e}")
        return

    # Clear existing data
    supabase.table("India_news").delete().neq("id", -1).execute()

    # Setup initial browser
    try:
        driver = create_driver()
        print("✓ Browser initialized\n")
    except WebDriverException as e:
        print(f"✗ Browser error: {e}")
        return

    # Load NDTV latest news page
    try:
        if not safe_get_page(driver, "https://www.ndtv.com/latest"):
            print("✗ Failed to load main page")
            driver.quit()
            return
        print("✓ Page loaded successfully")
        time.sleep(2)
    except Exception as e:
        print(f"✗ Failed to load main page: {e}")
        driver.quit()
        return

    # Find article containers
    try:
        rows = driver.find_elements(By.CLASS_NAME, "NwsLstPg_ttl")
        print(f"✓ Found {len(rows)} article containers\n")
    except NoSuchElementException:
        print("✗ Could not find article elements on page")
        driver.quit()
        return

    # Extract first 10 articles
    articles = []
    for i in rows:
        try:
            title_element = i.find_element(By.CSS_SELECTOR, ".NwsLstPg_ttl-lnk")
            title = title_element.text.strip()
            link = title_element.get_attribute("href")

            if title and link and link.startswith("https://"):
                articles.append((title, link))
                print(f"✓ Found: {title[:50]}...")

            if len(articles) == 10:
                break
        except Exception:
            continue

    if len(articles) == 0:
        print("✗ No articles found")
        driver.quit()
        return

    print(f"\n✓ Extracted {len(articles)} articles to process\n")
    
    # Results
    tagged_results = []
    
    # Process articles with periodic browser refresh
    for idx, (title, link) in enumerate(articles, start=1):
        print(f"[{idx}/{len(articles)}] Processing: {title[:60]}...")

        # Refresh browser every 3 articles to prevent memory issues
        if idx > 1 and idx % 3 == 0:
            print("    ♻ Refreshing browser...")
            try:
                driver.quit()
            except:
                pass
            time.sleep(1)
            try:
                driver = create_driver()
                print("    ✓ Browser refreshed")
            except Exception as e:
                print(f"    ✗ Failed to refresh browser: {e}")
                break

        try:
            # Load article page with retry
            if not safe_get_page(driver, link):
                print("    ✗ Could not load page - skipping")
                continue
            
            print("    ✓ Page loaded, extracting...")

            # Extract content
            content = extract_article_content(driver)

            if not content or len(content) < 2:
                print("    ✗ Insufficient content - skipping")
                continue

            # Tag article
            print("    → Tagging article...")
            tags = tagger.tag_article(content, threshold=2)

            # Save in results
            article_data = {
                "title": title,
                "link": link,
                "tags": tags,
                "content": content
            }
            tagged_results.append(article_data)

            # Insert into Supabase
            try:
                db_data = {
                    "headline": json.dumps({"title": title}),
                    "link": json.dumps({"url": link}),
                    "content": "\n\n".join(content),
                    "tags": tags
                }
                response = supabase.table("India_news").insert(db_data).execute()
                print(f"    ✓ Tagged: {', '.join(tags)}")
                print(f"    ✓ Saved to DB (ID: {response.data[0]['id']})")
            except Exception as e:
                print(f"    ✓ Tagged: {', '.join(tags)}")
                print(f"    ✗ DB error: {str(e)[:50]}")

        except Exception as e:
            print(f"    ✗ Error: {type(e).__name__}")
            continue

    # Close browser
    try:
        driver.quit()
        print("\n✓ Browser closed")
    except:
        pass

    # Final summary
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