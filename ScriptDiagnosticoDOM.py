from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

# Inicializar navegador
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)
driver.get("https://www.carrefour.com.ar/")
time.sleep(5)

# Buscar tarjetas de productos
cards = driver.find_elements(By.CLASS_NAME, "vtex-product-summary-2-x-container")
print("🔍 Tarjetas encontradas:", len(cards))

with open("estructura_dom_home.txt", "w", encoding="utf-8") as f:
    for i, card in enumerate(cards[:5], start=1):
        f.write(f"\n📦 Producto {i}\n")
        children = card.find_elements(By.XPATH, ".//*")
        for child in children:
            clase = child.get_attribute("className")
            texto = child.text.strip()
            if clase and texto:
                f.write(f"→ Clase: {clase} | Texto: {texto}\n")

driver.quit()
print("✅ Mapeo DOM guardado en estructura_dom_home.txt")
