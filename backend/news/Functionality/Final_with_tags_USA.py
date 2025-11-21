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
import sys
import os


# Import the ArticleTagger from tagging.py
from tagging import ArticleTagger

SUPABASE_URL="https://mydfflfgggqoliryamtn.supabase.co"
SUPABASE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im15ZGZmbGZnZ2dxb2xpcnlhbXRuIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjE2Nzg5NTksImV4cCI6MjA3NzI1NDk1OX0.mVM685NQKkxUV0ja5TZC3jf3uio9HhW6_ugVLHmgb5U"

# ---------- MAIN SCRAPER WITH TAGGING ----------
def scrape_and_tag_articles():
    """Main function to scrape articles and automatically tag them."""
    
    # Initialize tagger
    tagger = ArticleTagger()
    
    # Initialize Supabase client
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✓ Connected to Supabase\n")
    except Exception as e:
        print(f"✗ Failed to connect to Supabase: {e}")
        return
    
    # Setup browser with page load timeout
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        driver.set_page_load_timeout(30)  # Maximum 30 seconds to load any page
        wait = WebDriverWait(driver, 10)
        print("✓ Browser initialized successfully\n")
    except WebDriverException as e:
        print(f"✗ Failed to initialize browser: {e}")
        return
    
    # Load main page
    try:
        driver.get("https://www.usatoday.com/news/nation/")
        time.sleep(2)
        print("✓ Page loaded successfully\n")
    except Exception as e:
        print(f"✗ Failed to load main page: {e}")
        driver.quit()
        return
    
    # Find article links
    try:
        rows = driver.find_elements(By.CLASS_NAME, "gnt_m_flm_a")
    except NoSuchElementException:
        print("✗ Could not find article elements on page")
        driver.quit()
        return
    
    # Extract first 10 article links
    articles = []
    for r in rows:
        try:
            title = r.text.strip()
            link = r.get_attribute("href")
            if title and link and link.startswith("https://"):
                articles.append((title, link))
            if len(articles) == 10:
                break
        except Exception:
            continue
    
    print(f"✓ Found {len(articles)} articles to process\n")
    print("=" * 80)
    
    # Results storage
    tagged_results = []
    
    # Visit each article and tag it
    for idx, (title, link) in enumerate(articles, start=1):
        print(f"\n[{idx}/{len(articles)}] Processing: {title[:60]}...")
        
        try:
            # Try to load the page with timeout protection
            try:
                driver.get(link)
                time.sleep(2)  # Reduced from 3 to 2 seconds
            except TimeoutException:
                print("    ✗ Page load timeout (30s exceeded) - skipping")
                continue
            except Exception as e:
                print(f"    ✗ Error loading page: {type(e).__name__} - skipping")
                continue
            
            # Wait for article with timeout
            try:
                article = WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.TAG_NAME, "article"))
                )
            except TimeoutException:
                print("    ✗ Article content timeout (15s) - skipping")
                # Try to stop page loading before moving on
                try:
                    driver.execute_script("window.stop();")
                except:
                    pass
                continue
            
            # Extract content
            try:
                paragraphs = article.find_elements(By.TAG_NAME, "p")
                
                if not paragraphs:
                    print("    ✗ No content found - skipping")
                    continue
                
                # Get text from paragraphs
                content = []
                for p in paragraphs:
                    text = p.text.strip()
                    if text:
                        content.append(text)
                
                if not content:
                    print("    ✗ No text extracted - skipping")
                    continue
                
                # Tag the article
                tags = tagger.tag_article(content, threshold=2)
                
                # Store result
                article_data = {
                    "title": title,
                    "link": link,
                    "tags": tags,
                    "content": content
                }
                tagged_results.append(article_data)
                
                # Insert into Supabase
                try:
                    # Prepare data for insertion
                    db_data = {
                        "headline": json.dumps({"title": title}),  # Store as JSON
                        "link": json.dumps({"url": link}),  # Store as JSON
                        "content": "\n\n".join(content),  # Join paragraphs with double newline
                        "tags": tags  # PostgreSQL text array
                    }
                    
                    response = supabase.table("USA_news").insert(db_data).execute()
                    print(f"    ✓ Tagged as: {', '.join(tags)}")
                    print(f"    ✓ Saved to database (ID: {response.data[0]['id']})")
                    
                except Exception as e:
                    print(f"    ✓ Tagged as: {', '.join(tags)}")
                    print(f"    ✗ Database error: {e}")
                    # Continue processing even if DB insert fails
                
            except NoSuchElementException:
                print("    ✗ Could not extract content - skipping")
                continue
                
        except Exception as e:
            print(f"    ✗ Error: {type(e).__name__}")
            continue
    
    # Close browser
    try:
        driver.quit()
    except Exception:
        pass
    
    # Display final results
    print("\n\n" + "=" * 80)
    print("FINAL RESULTS - TAGGED ARTICLES")
    print("=" * 80 + "\n")
    
    for idx, result in enumerate(tagged_results, start=1):
        print(f"[{idx}] {result['title']}")
        print(f"    Link: {result['link']}")
        print(f"    Tags: {', '.join(result['tags'])}")
        print(f"    Paragraphs: {len(result['content'])}")
        print()
    
    print("=" * 80)
    print(f"Successfully tagged and saved {len(tagged_results)} out of {len(articles)} articles to database")
    print("=" * 80)
    
    return tagged_results


# ---------- RUN THE SCRIPT ----------
if __name__ == "__main__":
    results = scrape_and_tag_articles()
