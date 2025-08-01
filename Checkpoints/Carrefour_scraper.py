from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import csv, time
from datetime import datetime

# Inicializar navegador
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

# Acceder al sitio
driver.get("https://www.carrefour.com.ar/productos")
time.sleep(5)  # Esperar carga dinámica

# Buscar contenedores de productos
cards = driver.find_elements(By.CLASS_NAME, "vtex-product-summary-2-x-container")  # contenedor visual de cada producto

# Encabezados CSV según tu lógica
encabezados = [
    "ID_Producto", "Supermercado", "Marca", "Nombre_Comercial", "Presentacion",
    "Unidad", "Cantidad", "Categoria", "Subcategoria", "Codigo_Subcategoria",
    "Precio", "Fecha_Oferta", "Fuente"
]

productos = []
for i, card in enumerate(cards, start=1):
    try:
        simbolo = card.find_element(By.CLASS_NAME, "valtech-carrefourar-product-price-0-x-currencyCode").text.strip()
        espacio = card.find_element(By.CLASS_NAME, "valtech-carrefourar-product-price-0-x-currencyLiteral").text.strip()
        entero1 = card.find_elements(By.CLASS_NAME, "valtech-carrefourar-product-price-0-x-currencyInteger")[0].text.strip()
        grupo = card.find_element(By.CLASS_NAME, "valtech-carrefourar-product-price-0-x-currencyGroup").text.strip()
        entero2 = card.find_elements(By.CLASS_NAME, "valtech-carrefourar-product-price-0-x-currencyInteger")[1].text.strip()
        decimal = card.find_element(By.CLASS_NAME, "valtech-carrefourar-product-price-0-x-currencyDecimal").text.strip()
        fraccion = card.find_element(By.CLASS_NAME, "valtech-carrefourar-product-price-0-x-currencyFraction").text.strip()
        precio = f"{simbolo}{espacio}{entero1}{grupo}{entero2}{decimal}{fraccion}"
    except:
        continue

    producto = [
        i,
        "Carrefour",
        "Desconocida",
        nombre,
        "Sin definir",
        "Unidad",
        1,
        "Sin definir",
        "Sin definir",
        "SIN_CODIGO",
        precio,
        datetime.today().strftime('%Y-%m-%d'),
        "Web"
    ]
    productos.append(producto)

# Generar CSV
with open("productos_carrefour.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(encabezados)
    writer.writerows(productos)

print("CSV generado correctamente con", len(productos), "productos.")
driver.quit()