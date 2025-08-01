from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time, csv, os

# 🚀 Configuración del navegador
options = Options()
# Para ver el navegador, comentá la siguiente línea:
# options.add_argument("--headless")
options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=options)
driver.get("https://www.carrefour.com.ar/")
wait = WebDriverWait(driver, 15)

# 🧭 Paso 1: Intentar click en botón "Categorías"
boton = None
try:
    boton = wait.until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, "button[data-id='mega-menu-trigger-button']")
    ))
except:
    try:
        boton = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//button[.//span[text()='Categorías']]")
        ))
    except:
        print("❌ No se encontró el botón 'Categorías'. Guardando HTML para diagnóstico…")
        html = driver.execute_script("return document.body.innerHTML")
        os.makedirs("diagnostico", exist_ok=True)
        with open("diagnostico/carrefour_debug.html", "w", encoding="utf-8") as f:
            f.write(html)
        driver.quit()
        exit()

# 🖱️ Click vía JavaScript
try:
    driver.execute_script("arguments[0].click();", boton)
    time.sleep(3)
except Exception as e:
    print("❌ Falló el click en 'Categorías':", e)
    driver.quit()
    exit()

# 📦 Paso 2: Extraer categorías principales
try:
    categorias = wait.until(EC.presence_of_all_elements_located(
        (By.CSS_SELECTOR, "li.carrefourar-mega-menu-0-x-menuItem a")
    ))
except Exception as e:
    print("❌ No se encontraron categorías principales:", e)
    driver.quit()
    exit()

# 🗂️ Paso 3: Guardar resultados
resultados = []
for cat in categorias:
    nombre = cat.text.strip()
    url = cat.get_attribute("href")
    if nombre and url:
        resultados.append({"Categoria": nombre, "URL": url})

# 📄 Paso 4: Exportar a CSV
with open("carrefour_categorias.csv", "w", newline="", encoding="utf-8") as archivo:
    writer = csv.DictWriter(archivo, fieldnames=["Categoria", "URL"])
    writer.writeheader()
    writer.writerows(resultados)

print(f"✅ Extracción completada: {len(resultados)} categorías exportadas.")
driver.quit()