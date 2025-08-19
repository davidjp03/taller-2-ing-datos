from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
from pymongo import MongoClient
import pandas as pd
import os
from dotenv import load_dotenv

# Configuración del driver
service = Service('/usr/bin/chromedriver')
driver = webdriver.Chrome(service=service)
driver.delete_all_cookies()
wait = WebDriverWait(driver, 10)

# Configuración de MongoDB
load_dotenv()
mongo_url = os.getenv('DB_URL')
client = MongoClient(mongo_url)
db = client['scraping_db']
collection = db['mercadolibre_items']

def search_items(term, pages=1):
    #driver.delete_all_cookies()

    driver.get("https://www.mercadolibre.com.co/")
    
    # Buscar el término
    search_box = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="cb1-edit"]')))
    search_box.send_keys(term)
    search_box.send_keys(Keys.ENTER)
    
    # Click en botón buscar si aparece
    try:
        search_button = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/header/div/div[2]/form/button')))
        search_button.click()
    except:
        pass
    
    all_data = []
    
    for p in range(pages):
        print(f"Procesando página {p+1}...")
        
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'li.ui-search-layout__item')))
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        
        # URLs de productos
        items = soup.select("li.ui-search-layout__item a.poly-component__title")
        
        for i, link in enumerate(items): 
            url = link.get("href")
            print(f" - Extrayendo producto {i+1}: {url}")
            data = extract_item_info(url)
            all_data.append(data)
        
        # Pasar a la siguiente página
        try:
            next_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="root-app"]/div/div[2]/section/div[6]/nav/ul/li[12]/a')))
            next_button.click()
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'li.ui-search-layout__item')))
        except:
            print("No hay más páginas disponibles.")
            break

    print("Extracción completa.")
    return all_data



def extract_item_info(url):
    driver.get(url)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "h1.ui-pdp-title")))  # Espera a que la página cargue completamente
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    data = {}
    data['url'] = url
     # Título
    title = soup.find("h1", {"class": "ui-pdp-title"})
    data["Título"] = title.text.strip() if title else None
    
    # Precio
    price = soup.find("span", {"class": "andes-money-amount__fraction"})
    data["Precio"] = price.text.strip() if price else None
    
    # Estado (Nuevo/Usado)
    condition = soup.find("span", {"class": "ui-pdp-subtitle"})
    data["Condición"] = condition.text.strip() if condition else None
    
    # Disponibilidad / stock
    stock = soup.find("span", {"class": "ui-pdp-buybox__quantity__available"})
    data["Disponibilidad"] = stock.text.strip() if stock else None
    
    # Vendedor
    seller = soup.find("a", {"class": "ui-pdp-media__title"})
    data["Vendedor"] = seller.text.strip() if seller else None
    
    # Ubicación
    location = soup.find("p", {"class": "ui-seller-info__status-info__subtitle"})
    data["Ubicación"] = location.text.strip() if location else None
    
    # rating
    rating = soup.find("span", {"class": "ui-pdp-review__rating"})
    data["Rating"] = rating.text.strip() if rating else None
    
    return data

results = search_items('m4 f82', pages=2)

df = pd.DataFrame(results)
print(df)
# df.to_csv('mercadolibre_results.csv', index=False)

if results:
    collection.insert_many(results)
    print(f"Insertados {len(results)} documentos en MongoDB.")
    
driver.quit()
