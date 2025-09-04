from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from pymongo import MongoClient
import pandas as pd
import os
import time
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

def extract_item_info(url):
    """Extrae la información detallada de un producto en MercadoLibre"""
    data = {"url": url}
    try:
        driver.execute_script("window.open(arguments[0]);", url)
        driver.switch_to.window(driver.window_handles[1])

        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "h1.ui-pdp-title")))
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        # Datos básicos
        title = soup.find("h1", {"class": "ui-pdp-title"})
        data["Título"] = title.text.strip() if title else None

        price = soup.find("span", {"class": "andes-money-amount__fraction"})
        data["Precio"] = price.text.strip() if price else None

        condition = soup.find("span", {"class": "ui-pdp-subtitle"})
        data["Condición"] = condition.text.strip() if condition else None

        stock = soup.find("span", {"class": "ui-pdp-buybox__quantity__available"})
        data["Disponibilidad"] = stock.text.strip() if stock else None

        seller = soup.find("a", {"class": "ui-pdp-media__title"})
        data["Vendedor"] = seller.text.strip() if seller else None

        location = soup.find("p", {"class": "ui-seller-info__status-info__subtitle"})
        data["Ubicación"] = location.text.strip() if location else None

        rating = soup.find("span", {"class": "ui-pdp-review__rating"})
        data["Rating"] = rating.text.strip() if rating else None

        # Características
        caracteristicas_elements = driver.find_elements(By.CSS_SELECTOR, 'tr.andes-table__row')
        caracteristicas = []
        for elem in caracteristicas_elements:
            try:
                clave = elem.find_element(By.CSS_SELECTOR, 'th').text.strip()
                valor = elem.find_element(By.CSS_SELECTOR, 'td').text.strip()
                caracteristicas.append(f"{clave}: {valor}")
            except:
                continue
        data["Características"] = caracteristicas if caracteristicas else ["No se encontraron características"]

    except Exception as e:
        print("Error al extraer producto:", e)
    finally:
        # Cierra la pestaña y regresa
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
    return data

def search_items(term, pages=1):
    """Busca un término en MercadoLibre y navega por las páginas"""
    driver.get("https://www.mercadolibre.com.co/")

    # Buscar el término
    search_box = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="cb1-edit"]')))
    search_box.send_keys(term)
    search_box.submit()

    all_data = []

    pagina_actual = 1
    while pagina_actual <= pages:
        print(f"\n=== Página {pagina_actual} ====================================================")
        time.sleep(5)

        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'li.ui-search-layout__item')))
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        items = soup.select('li.ui-search-layout__item a.poly-component__title')

        for i, link in enumerate(items):
            url = link.get("href")
            print(f" - Extrayendo producto {i+1}: {url}")
            data = extract_item_info(url)
            all_data.append(data)
            collection.insert_one(data)  # Guardar directo en MongoDB

        # Ir a la siguiente página
        pagina_actual += 1
        try:
            next_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'li.andes-pagination__button--next a')))
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth'});", next_button)
            time.sleep(3)
            next_button.click()
        except:
            print("No se pudo encontrar el botón de siguiente página.")
            break

    print("Extracción completa.")
    return all_data


# Ejecutar scraping
#results = search_items('audi')

# Exportar a CSV
#df = pd.DataFrame(results)
#print(df)
#df.to_csv('mercadolibre_results.csv', index=False)

driver.quit()


# =========================
# QUERIES ORIENTADAS A CARROS
# =========================

# 1. Buscar todos los BMW con precio mayor a 100 millones
query1 = collection.find(
    {
        "Título": {"$regex": "BMW", "$options": "i"},
        "Precio": {"$regex": r"^[1-9]\d{2}\.\d{3}\.\d{3}$"}  # formato como "155.000.000"
    },
    {"Título": 1, "Precio": 1}
)
print("BMW con precio mayor a 200 millones:")
for doc in query1:
    precio = int(doc["Precio"].replace(".", ""))  # limpiar el string
    if precio > 200_000_000:
        print(doc["Título"], "-", precio)


# 2. Buscar Audi publicados en los últimos 6 meses
query2 = collection.find(
    {
        "Título": {"$regex": "Audi", "$options": "i"},
        "Condición": {"$regex": "Publicado hace [1-6] mes"}
    },
    {"Título": 1, "Condición": 1}
)
print("Audi publicados en los últimos 6 meses:")
for doc in query2:
    print(doc)


# 3. Extraer todos los carros modelo 2020
query3 = collection.find(
    {"Condición": {"$regex": r"^2020"}},
    {"Título": 1, "Condición": 1}
)
print("Carros modelo 2020:")
for doc in query3:
    print(doc)


# 4. Agregación: precio promedio por marca (BMW vs Audi)
pipeline = [
    {"$match": {"Título": {"$regex": "BMW|Audi", "$options": "i"}, "Precio": {"$exists": True}}},
    {"$project": {
        "Marca": {
            "$cond": [
                {"$regexMatch": {"input": "$Título", "regex": "BMW", "options": "i"}}, "BMW", "Audi"
            ]
        },
        "Precio": {
            "$toInt": {
                "$replaceAll": {"input": "$Precio", "find": ".", "replacement": ""}
            }
        }
    }},
    {"$group": {"_id": "$Marca", "PromedioPrecio": {"$avg": "$Precio"}, "Carros": {"$sum": 1}}},
    {"$sort": {"PromedioPrecio": -1}}
]
results_agg = collection.aggregate(pipeline)
print("Promedio de precios por marca:")
for r in results_agg:
    print(r)