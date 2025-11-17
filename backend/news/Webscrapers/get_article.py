from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Set up driver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

driver.get("https://www.usatoday.com/story/news/nation/2025/11/15/food-banks-hunger-government-shutdown-snap/87215291007/")
print("Page loaded")

# Wait until the article is present
article = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.TAG_NAME, "article"))
)

# Find all <p> tags inside the article
paragraphs = article.find_elements(By.TAG_NAME, "p")

print("\n=== Article Paragraphs ===\n")

for p in paragraphs:
    text = p.text.strip()
    if text:
        print(text)
        print()

driver.quit()
