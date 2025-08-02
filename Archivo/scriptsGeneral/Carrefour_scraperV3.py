from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import csv, time, json, os, re
from datetime import datetime

# Inicializar navegador
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

# Acceder al home
driver.get("https://www.carrefour.com.ar/")
time.sleep(5)

# --- Validador DOM dinámico ---
def mapear_dom_selenium(driver):
    estructura = {
        "card": "vtex-product-summary-2-x-container",
        "nombre": "vtex-product-summary-2-x-productBrand",
        "precio": [
            "valtech-carrefourar-product-price-0-x-currencyCode",
            "valtech-carrefourar-product-price-0-x-currencyLiteral",
            "valtech-carrefourar-product-price-0-x-currencyInteger",
            "valtech-carrefourar-product-price-0-x-currencyGroup",
            "valtech-carrefourar-product-price-0-x-currencyDecimal",
            "valtech-carrefourar-product-price-0-x-currencyFraction"
        ],
        "bloque_precio": "valtech-carrefourar-product-price-0-x-currencyContainer"
    }
    return estructura

def verificar_checkpoint(actual, esperado):
    return actual == esperado

# Cargar o crear checkpoint
checkpoint_path = "layout_checkpoint.json"
estructura_actual = mapear_dom_selenium(driver)

if not os.path.exists(checkpoint_path):
    print("📁 Checkpoint no encontrado. Creando nuevo...")
    with open(checkpoint_path, "w") as f:
        json.dump(estructura_actual, f)
else:
    with open(checkpoint_path) as f:
        estructura_esperada = json.load(f)
    if not verificar_checkpoint(estructura_actual, estructura_esperada):
        print("⚠️ DOM cambió. Actualizando checkpoint...")
        with open(checkpoint_path, "w") as f:
            json.dump(estructura_actual, f)
    else:
        print("✅ DOM válido. Continuando...")

# Buscar tarjetas de productos
cards = driver.find_elements(By.CLASS_NAME, estructura_actual["card"])
print("🔍 Productos encontrados:", len(cards))

# Encabezados CSV
encabezados = [
    "ID_Producto", "Nombre", "Precio_de_lista",
    "Precio_de_oferta", "Precio_float", "Fecha", "Fuente", "EsOferta"
]
productos = []

# Función auxiliar para convertir precio visual a float
def convertir_a_float(precio_str):
    try:
        limpio = re.sub(r"[^\d,]", "", precio_str).replace(",", ".")
        return float(limpio)
    except:
        return None

# Función para reconstruir precio visual desde un bloque individual
def reconstruir_precio_desde_container(container, clases_precio):
    simbolo = container.find_element(By.CLASS_NAME, clases_precio[0]).text.strip()
    espacio = container.find_element(By.CLASS_NAME, clases_precio[1]).text.strip()
    integer_parts = container.find_elements(By.CLASS_NAME, clases_precio[2])
    group_separators = container.find_elements(By.CLASS_NAME, clases_precio[3])
    decimal = container.find_element(By.CLASS_NAME, clases_precio[4]).text.strip()
    fraccion = container.find_element(By.CLASS_NAME, clases_precio[5]).text.strip()
    numero = ""
    for j in range(len(integer_parts)):
        numero += integer_parts[j].text.strip()
        if j < len(group_separators):
            numero += group_separators[j].text.strip()
    return f"{simbolo}{espacio}{numero}{decimal}{fraccion}"

for i, card in enumerate(cards, start=1):
    try:
        nombre = card.find_element(By.CLASS_NAME, estructura_actual["nombre"]).text.strip()
        bloques = card.find_elements(By.CLASS_NAME, estructura_actual["bloque_precio"])

        precios_reconstruidos = []
        precios_float = []

        for bloque in bloques[:2]:  # Solo tomar hasta 2 bloques
            precio_str = reconstruir_precio_desde_container(bloque, estructura_actual["precio"])
            precio_valor = convertir_a_float(precio_str)
            if precio_valor:
                precios_reconstruidos.append(precio_str)
                precios_float.append(precio_valor)

        if len(precios_float) == 2:
            idx_max = precios_float.index(max(precios_float))
            idx_min = precios_float.index(min(precios_float))
            precio_de_lista = precios_reconstruidos[idx_max]
            precio_de_oferta = precios_reconstruidos[idx_min]
            precio_float = precios_float[idx_min]
            es_oferta = precios_float[0] != precios_float[1]
        elif len(precios_float) == 1:
            precio_de_lista = precios_reconstruidos[0]
            precio_de_oferta = ""
            precio_float = precios_float[0]
            es_oferta = False
        else:
            precio_de_lista = precio_de_oferta = ""
            precio_float = None
            es_oferta = False

        productos.append([
            f"P{i}", nombre, precio_de_lista, precio_de_oferta,
            precio_float, datetime.today().strftime('%Y-%m-%d'),
            "Home Carrefour", es_oferta
        ])

    except Exception as e:
        print(f"⚠️ Producto {i} no procesado: {e}")
        continue

# Crear carpeta segura y versionar por fecha
output_dir = "./DBproductos"
os.makedirs(output_dir, exist_ok=True)
fecha_actual = datetime.today().strftime('%Y-%m-%d')
csv_filename = f"carrefour_productos_{fecha_actual}.csv"
csv_path = os.path.join(output_dir, csv_filename)

# Guardar CSV
with open(csv_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(encabezados)
    writer.writerows(productos)

print(f"✅ CSV guardado con {len(productos)} productos en {csv_path}")