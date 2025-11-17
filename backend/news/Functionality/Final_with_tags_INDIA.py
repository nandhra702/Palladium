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


# Import ArticleTagger
from tagging import ArticleTagger


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

    # Setup browser
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        driver.set_page_load_timeout(30)
        wait = WebDriverWait(driver, 10)
        print("✓ Browser initialized successfully\n")
    except WebDriverException as e:
        print(f"✗ Failed to initialize browser: {e}")
        return

    # Load NDTV latest news page
    try:
        driver.get("https://www.ndtv.com/latest")
        print("✓ Page loaded, waiting for content...")
        time.sleep(3)  # Give page time to load
    except Exception as e:
        print(f"✗ Failed to load main page: {e}")
        driver.quit()
        return

    # Find article containers using the working selector from your code
    try:
        rows = driver.find_elements(By.CLASS_NAME, "NwsLstPg_ttl")
        print(f"✓ Found {len(rows)} article containers\n")
    except NoSuchElementException:
        print("✗ Could not find article elements on page")
        driver.quit()
        return

    # Extract first 5 articles (using your working code logic)
    articles = []
    for i in rows:
        try:
            title_element = i.find_element(By.CSS_SELECTOR, ".NwsLstPg_ttl-lnk")
            title = title_element.text.strip()
            link = title_element.get_attribute("href")

            if title and link and link.startswith("https://"):
                articles.append((title, link))
                print(f"✓ Found: {title[:50]}...")

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

    # Results
    tagged_results = []

    # Visit each article and extract content
    for idx, (title, link) in enumerate(articles, start=1):
        print(f"\n[{idx}/{len(articles)}] Processing: {title[:60]}...")

        try:
            # Load article page
            driver.get(link)
            print("    ✓ Page opened, extracting content...")
            time.sleep(2)

            # NDTV article content extraction - using exact selector from HTML
            content = []
            
            try:
                # Wait for the filteredParagraphs to load
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "filteredParagraphs"))
                )
                
                # Extract all paragraphs with class "filteredParagraphs"
                paragraphs = driver.find_elements(By.CLASS_NAME, "filteredParagraphs")
                content = [p.text.strip() for p in paragraphs if p.text.strip()]
                
                print(f"    ✓ Extracted {len(content)} paragraphs from article")
                
            except TimeoutException:
                print("    ✗ Could not find article paragraphs - skipping")
            except Exception as e:
                print(f"    ✗ Error extracting content: {type(e).__name__}")

            # If still no content found, skip article
            if not content:
                print("    ✗ No usable text extracted - skipping")
                continue

            # Tag article using your tagger
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
                print(f"    ✓ Tagged as: {', '.join(tags)}")
                print(f"    ✓ Saved to DB (ID: {response.data[0]['id']})")
            except Exception as e:
                print(f"    ✓ Tagged as: {', '.join(tags)}")
                print(f"    ✗ Database error: {e}")

        except Exception as e:
            print(f"    ✗ Error processing article: {type(e).__name__}")
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
