import csv
import requests
from urllib.parse import quote

# Lista de subcategorías
subcategorias = [
    "Smart TVs", "Smart TV", "Soportes y accesorios", "Celulares", "Celulares libres",
    "Teléfonos fijos e inalámbricos", "Accesorios de celulares", "Climatización",
    "Aires acondicionados", "Ventiladores y climatizadores", "Calefacción eléctrica",
    "Calefacción a gas", "Calefacción a leña", "Pequeños electrodomésticos", "Cafeteras",
    "Jarras eléctricas", "Jugueras y exprimidores", "Tostadoras y sandwicheras",
    "Licuadoras, procesadoras y gasificadoras", "Batidoras", "Cocción", "Planchas",
    "Aspiradoras", "Lavado", "Lavarropas", "Secarropas", "Lavasecarropas", "Lavavajillas",
    "Termotanques y calefones", "Calefones", "Termotanques a gas", "Termotanques eléctricos",
    "Cocinas y hornos", "Cocinas", "Anafes", "Hornos", "Microondas", "Campanas y purificadores",
    "Audio", "Parlantes portátiles", "Equipos de sonido", "Auriculares", "Audio para autos",
    "Radios", "Cuidado personal y salud", "Planchitas de pelo", "Secadores de pelo",
    "Depiladoras", "Afeitadoras, cortabarba y cortapelo", "Salud y bienestar",
    "Informática y gaming", "Notebooks y PC", "Consolas y joysticks", "Impresoras y cartuchos",
    "Tablets", "Monitores y proyectores", "Componentes", "Teclados y mouse",
    "Accesorios e informática", "Gaming", "Cámaras de seguridad", "Heladeras y freezers",
    "Heladeras", "Freezers", "Cavas"
]

base_url = "https://www.carrefour.com.ar/"
resultados = []

for nombre in subcategorias:
    # Convertir a formato slug
    slug = quote(nombre.lower().replace(" ", "-"))
    url = base_url + slug

    try:
        r = requests.get(url, timeout=10)
        status_code = r.status_code
        existe = status_code == 200 and "vtex-product-summary" in r.text
    except Exception as e:
        status_code = "Error"
        existe = False

    resultados.append({
        "subcategoria": slug,
        "url": url,
        "status_code": status_code,
        "existe": existe
    })

# Exportar a CSV
with open("carrefour_urls_validadas.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["subcategoria", "url", "status_code", "existe"])
    writer.writeheader()
    for fila in resultados:
        writer.writerow(fila)

print("✅ Archivo carrefour_urls_validadas.csv generado correctamente.")