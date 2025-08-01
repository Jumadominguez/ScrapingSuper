from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import csv, time, json, os, re
from datetime import datetime

# --- Configurar navegador con opciones limpias ---
options = Options()
options.add_argument("--log-level=3")         # Solo errores críticos
options.add_argument("--headless=new")        # Ejecución sin ventana
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# --- Funciones auxiliares ---
def mapear_dom_selenium(driver):
    return {
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

def extraer_nombre_de_oferta(card):
    try:
        elemento = card.find_element(By.CLASS_NAME, "tooltipText")
        texto = elemento.text.strip()
        if texto and len(texto) < 100:
            return texto
    except:
        pass
    posibles_clases = ["label", "tag", "badge", "promo", "highlight", "leyenda"]
    for clase in posibles_clases:
        try:
            elemento = card.find_element(By.CLASS_NAME, clase)
            texto = elemento.text.strip()
            if texto and len(texto) < 100:
                return texto
        except:
            continue
    return ""

def convertir_a_float(precio_str):
    try:
        limpio = re.sub(r"[^\d,]", "", precio_str).replace(",", ".")
        return float(limpio)
    except:
        return None

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

def procesar_categoria(driver, url, fuente, categoria, estructura, id_inicial):
    driver.get(url)
    time.sleep(5)
    last_height = driver.execute_script("return document.body.scrollHeight")
    for _ in range(8):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
    cards = driver.find_elements(By.CLASS_NAME, estructura["card"])
    productos = []
    for i, card in enumerate(cards, start=id_inicial):
        try:
            nombre = card.find_element(By.CLASS_NAME, estructura["nombre"]).text.strip()
            bloques = card.find_elements(By.CLASS_NAME, estructura["bloque_precio"])
            precios_reconstruidos = []
            precios_float = []
            for bloque in bloques[:2]:
                precio_str = reconstruir_precio_desde_container(bloque, estructura["precio"])
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
            nombre_de_oferta = extraer_nombre_de_oferta(card)
            productos.append([
                f"P{i}", categoria, nombre, precio_de_lista, precio_de_oferta,
                precio_float, datetime.today().strftime('%Y-%m-%d'),
                fuente, es_oferta, nombre_de_oferta
            ])
        except Exception as e:
            print(f"⚠️ Producto {i} no procesado: {e}")
            continue
    return productos

# --- Checkpoint DOM ---
checkpoint_path = "layout_checkpoint.json"
estructura_actual = mapear_dom_selenium(driver)
if not os.path.exists(checkpoint_path):
    with open(checkpoint_path, "w") as f:
        json.dump(estructura_actual, f)
else:
    with open(checkpoint_path) as f:
        estructura_esperada = json.load(f)
    if estructura_actual != estructura_esperada:
        with open(checkpoint_path, "w") as f:
            json.dump(estructura_actual, f)

# --- Ejecución ---
productos_almacen = procesar_categoria(
    driver,
    "https://www.carrefour.com.ar/almacen",
    "Almacén Carrefour",
    "Almacén",
    estructura_actual,
    id_inicial=1
)

# --- Guardar CSV único ---
encabezados = [
    "ID_Producto", "Categoria", "Nombre", "Precio_de_lista",
    "Precio_de_oferta", "Precio_float", "Fecha", "Fuente",
    "EsOferta", "Oferta"
]
output_dir = "./DBproductos"
os.makedirs(output_dir, exist_ok=True)
fecha_actual = datetime.today().strftime('%Y-%m-%d')
csv_filename = f"carrefour_almacen_{fecha_actual}.csv"
csv_path = os.path.join(output_dir, csv_filename)

with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.writer(f)
    writer.writerow(encabezados)
    writer.writerows(productos_almacen)

print(f"✅ CSV guardado con {len(productos_almacen)} productos en {csv_path}")