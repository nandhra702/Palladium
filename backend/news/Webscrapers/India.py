from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

def fetch_latest_news():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get("https://www.ndtv.com/latest")

    titles, links = [], []

    rows = driver.find_elements(By.CLASS_NAME, "NwsLstPg_ttl")

    for i in rows:
            title_element = i.find_element(By.CSS_SELECTOR, ".NwsLstPg_ttl-lnk")
            title = title_element.text
            link = title_element.get_attribute("href")

            if title and link:
                titles.append(title)
                links.append(link)


    driver.quit()
    return titles, links


fetch_latest_news()