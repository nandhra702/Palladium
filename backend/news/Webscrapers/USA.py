from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

# Set up driver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# Open the page
driver.get("https://www.usatoday.com/news/nation/")
print("Page loaded successfully")

# Select all <a> tags that contain the links and titles
rows = driver.find_elements(By.CLASS_NAME, "gnt_m_flm_a")

# Loop through and print title + link
print("Gonna print now:")
for i in rows:
    title = i.text.strip()
    link = i.get_attribute("href")
    print(title)
    print(link)
    print("-" * 60)

print("Done printing")

driver.quit()
