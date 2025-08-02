import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import time

def scrape_jumbo_product(product_url):
    """
    Extrae información de un producto específico de Jumbo
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(product_url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extraer información del producto
        product_data = {}
        
        # Nombre del producto
        name_element = soup.find('span', class_='vtex-product-summary-2-x-productBrand')
        product_data['nombre'] = name_element.text.strip() if name_element else 'No encontrado'
        
        # Marca
        brand_element = soup.find('span', class_='vtex-product-summary-2-x-productBrandName')
        product_data['marca'] = brand_element.text.strip() if brand_element else 'No encontrado'
        
        # Precio
        price_element = soup.find('div', class_=re.compile('vtex-price-format'))
        product_data['precio'] = price_element.text.strip() if price_element else 'No encontrado'
        
        # Imagen
        img_element = soup.find('img', class_='vtex-product-summary-2-x-image')
        product_data['imagen_url'] = img_element.get('src') if img_element else 'No encontrado'
        
        # URL del producto
        product_data['url'] = product_url
        
        return product_data
        
    except Exception as e:
        print(f"Error al procesar {product_url}: {str(e)}")
        return None

def scrape_jumbo_category(category_url, max_products=10):
    """
    Extrae productos de una categoría de Jumbo
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(category_url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Buscar todos los enlaces de productos
        product_links = soup.find_all('a', class_='vtex-product-summary-2-x-clearLink')
        
        products_data = []
        count = 0
        
        for link in product_links[:max_products]:
            if count >= max_products:
                break
                
            href = link.get('href')
            if href:
                # Construir URL completa
                if href.startswith('/'):
                    product_url = 'https://www.jumbo.com.ar' + href
                else:
                    product_url = href
                
                # Extraer datos del HTML del enlace actual
                product_data = extract_product_from_element(link)
                if product_data:
                    product_data['url'] = product_url
                    products_data.append(product_data)
                    count += 1
                    print(f"Producto {count}: {product_data.get('nombre', 'Sin nombre')}")
                
                # Pausa para no sobrecargar el servidor
                time.sleep(1)
        
        return products_data
        
    except Exception as e:
        print(f"Error al procesar la categoría: {str(e)}")
        return []

def extract_product_from_element(product_element):
    """
    Extrae información de un elemento de producto del HTML
    """
    try:
        product_data = {}
        
        # Nombre del producto
        name_element = product_element.find('span', class_='vtex-product-summary-2-x-productBrand')
        product_data['nombre'] = name_element.text.strip() if name_element else 'No encontrado'
        
        # Marca
        brand_element = product_element.find('span', class_='vtex-product-summary-2-x-productBrandName')
        product_data['marca'] = brand_element.text.strip() if brand_element else 'No encontrado'
        
        # Precio - buscar diferentes clases de precio
        price_element = product_element.find('div', class_=re.compile('vtex-price-format|price'))
        if not price_element:
            # Buscar en elementos con texto que contenga $
            price_elements = product_element.find_all(text=re.compile(r'\$[\d,\.]+'))
            if price_elements:
                product_data['precio'] = price_elements[0].strip()
            else:
                product_data['precio'] = 'No encontrado'
        else:
            product_data['precio'] = price_element.text.strip()
        
        # Imagen
        img_element = product_element.find('img')
        product_data['imagen_url'] = img_element.get('src') if img_element else 'No encontrado'
        
        # Promoción (si existe)
        promo_element = product_element.find('span', class_=re.compile('promo|offer|discount'))
        product_data['promocion'] = promo_element.text.strip() if promo_element else 'Sin promoción'
        
        return product_data
        
    except Exception as e:
        print(f"Error al extraer datos del elemento: {str(e)}")
        return None

# Ejemplo de uso
if __name__ == "__main__":
    # URL de la categoría almacén
    category_url = "https://www.jumbo.com.ar/almacen"
    
    print("🔍 Iniciando scraping de productos de Jumbo...")
    print(f"📂 Categoría: {category_url}")
    print("-" * 50)
    
    # Extraer productos
    products = scrape_jumbo_category(category_url, max_products=5)
    
    if products:
        # Crear DataFrame
        df = pd.DataFrame(products)
        
        # Mostrar resultados
        print(f"\n✅ Se encontraron {len(products)} productos:")
        print(df.to_string(index=False))
        
        # Guardar en CSV
        df.to_csv('productos_jumbo.csv', index=False, encoding='utf-8')
        print(f"\n💾 Datos guardados en 'productos_jumbo.csv'")
        
    else:
        print("❌ No se pudieron extraer productos")

print("Script de scraping de Jumbo creado exitosamente!")