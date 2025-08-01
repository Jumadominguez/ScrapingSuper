import requests
from bs4 import BeautifulSoup
import urllib.parse
import time

# Simular headers para evitar bloqueos
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "es-ES,es;q=0.9"
}

# Función para buscar productos en Jumbo
def buscar_producto_jumbo(nombre_producto):
    query = urllib.parse.quote(nombre_producto)
    url = f"https://www.jumbo.com.ar/busqueda?q={query}"
    response = requests.get(url, headers=HEADERS)

    if response.status_code != 200:
        return {"producto": nombre_producto, "precio": "Error de conexión"}

    soup = BeautifulSoup(response.text, "html.parser")
    resultados = soup.select("div.product-item")

    if not resultados:
        return {"producto": nombre_producto, "precio": "No disponible"}

    # Seleccionar el primer resultado relevante
    item = resultados[0]
    try:
        nombre = item.select_one("p.product-name").text.strip()
        precio = item.select_one("span.best-price").text.strip()
    except AttributeError:
        return {"producto": nombre_producto, "precio": "Datos incompletos"}

    return {"producto": nombre_producto, "match": nombre, "precio": precio}

# Lista de productos normalizados
productos = [
    "Arroz Molinos Ala 1kg",
    "Aceite Girasol Cocinero 900ml"
]

# Ejecutar el scraper
resultados = []
for prod in productos:
    resultado = buscar_producto_jumbo(prod)
    resultados.append(resultado)
    time.sleep(1)  # pequeña pausa para no saturar el servidor

# Mostrar resultados
for r in resultados:
    print(f"{r['producto']}: {r.get('precio', 'Sin precio')} — Match: {r.get('match', 'Sin coincidencia')}")