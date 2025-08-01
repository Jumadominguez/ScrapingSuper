import requests
from bs4 import BeautifulSoup
import csv
import time
import json
from urllib.parse import urljoin, urlparse
import re

def get_carrefour_categories():
    """
    Extrae todas las categorías, subcategorías y subsecciones de Carrefour Argentina
    """
    base_url = "https://www.carrefour.com.ar"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    print("🔍 Iniciando scraping de Carrefour...")
    
    try:
        # Hacer request a la página principal
        response = requests.get(base_url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Buscar el menú de categorías (puede estar en diferentes elementos)
        menu_selectors = [
            'nav[data-testid="menu"]',
            '.vtex-menu-2-x-styledLinkContainer',
            '.vtex-store-components-3-x-menuContainer',
            '[data-testid="store-menu"]',
            '.menu-container',
            'nav.menu',
            '.category-menu'
        ]
        
        menu_element = None
        for selector in menu_selectors:
            menu_element = soup.select_one(selector)
            if menu_element:
                print(f"✅ Menú encontrado con selector: {selector}")
                break
        
        if not menu_element:
            print("❌ No se pudo encontrar el menú principal")
            # Intentar buscar links que contengan categorías conocidas
            all_links = soup.find_all('a', href=True)
            category_links = []
            
            known_categories = [
                'electro', 'tecnologia', 'bazar', 'textil', 'almacen', 
                'desayuno', 'merienda', 'bebidas', 'lacteos', 'frescos',
                'carnes', 'pescados', 'frutas', 'verduras', 'panaderia',
                'congelados', 'limpieza', 'perfumeria', 'bebe', 'mascotas',
                'indumentaria'
            ]
            
            for link in all_links:
                href = link.get('href', '').lower()
                text = link.get_text(strip=True).lower()
                
                if any(cat in href or cat in text for cat in known_categories):
                    category_links.append({
                        'text': link.get_text(strip=True),
                        'href': link.get('href')
                    })
            
            print(f"📋 Enlaces de categorías encontrados: {len(category_links)}")
            for link in category_links[:10]:  # Mostrar solo los primeros 10
                print(f"  - {link['text']}: {link['href']}")
            
            return []
        
        # Extraer categorías del menú
        categories = []
        category_links = menu_element.find_all('a', href=True)
        
        print(f"📋 Enlaces encontrados en el menú: {len(category_links)}")
        
        for link in category_links:
            text = link.get_text(strip=True)
            href = link.get('href')
            
            if text and href and len(text) > 2:  # Filtrar enlaces vacíos o muy cortos
                full_url = urljoin(base_url, href)
                categories.append({
                    'name': text,
                    'url': full_url,
                    'href': href
                })
        
        # Filtrar y limpiar categorías
        filtered_categories = []
        for cat in categories:
            # Filtrar URLs que parecen ser categorías de productos
            if any(keyword in cat['href'].lower() for keyword in [
                '/c/', '/categoria', '/products', '/busca'
            ]) or any(keyword in cat['name'].lower() for keyword in [
                'electro', 'tecnologia', 'bazar', 'textil', 'almacen',
                'bebidas', 'lacteos', 'carnes', 'frutas', 'verduras',
                'limpieza', 'perfumeria', 'mascotas', 'indumentaria'
            ]):
                filtered_categories.append(cat)
        
        print(f"✅ Categorías principales encontradas: {len(filtered_categories)}")
        for cat in filtered_categories:
            print(f"  - {cat['name']}: {cat['url']}")
        
        return filtered_categories
        
    except Exception as e:
        print(f"❌ Error al obtener categorías: {str(e)}")
        return []

def scrape_subcategories(category_url, category_name, headers):
    """
    Extrae subcategorías y subsecciones de una categoría específica
    """
    print(f"🔍 Explorando: {category_name}")
    
    try:
        response = requests.get(category_url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Buscar subcategorías en diferentes elementos posibles
        subcategory_selectors = [
            '.vtex-menu-2-x-submenuContainer a',
            '.category-menu-item a',
            '.subcategory-link',
            '.filter-navigator a',
            '.department-list a',
            '[data-testid="category-item"] a'
        ]
        
        subcategories = []
        
        for selector in subcategory_selectors:
            elements = soup.select(selector)
            if elements:
                print(f"  📋 Subcategorías encontradas con selector: {selector}")
                
                for element in elements:
                    text = element.get_text(strip=True)
                    href = element.get('href')
                    
                    if text and href and len(text) > 2:
                        full_url = urljoin(category_url, href)
                        subcategories.append({
                            'name': text,
                            'url': full_url,
                            'href': href
                        })
                break
        
        # Si no encontramos subcategorías con selectores específicos, buscar todos los enlaces
        if not subcategories:
            all_links = soup.find_all('a', href=True)
            for link in all_links:
                text = link.get_text(strip=True)
                href = link.get('href')
                
                # Filtrar enlaces que parecen subcategorías
                if (text and href and len(text) > 2 and len(text) < 100 and
                    any(keyword in href.lower() for keyword in ['/c/', '/categoria', '/products']) and
                    text.lower() not in ['home', 'inicio', 'carrefour', 'mi cuenta']):
                    
                    full_url = urljoin(category_url, href)
                    subcategories.append({
                        'name': text,
                        'url': full_url,
                        'href': href
                    })
        
        # Eliminar duplicados
        seen = set()
        unique_subcategories = []
        for sub in subcategories:
            if sub['name'] not in seen:
                seen.add(sub['name'])
                unique_subcategories.append(sub)
        
        print(f"  ✅ {len(unique_subcategories)} subcategorías encontradas")
        
        return unique_subcategories[:20]  # Limitar a 20 para evitar demasiados requests
        
    except Exception as e:
        print(f"  ❌ Error al obtener subcategorías de {category_name}: {str(e)}")
        return []

def main():
    """
    Función principal que ejecuta todo el scraping
    """
    print("🚀 Iniciando scraping completo de Carrefour Argentina")
    print("=" * 60)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'es-AR,es;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    
    # Obtener categorías principales
    categories = get_carrefour_categories()
    
    if not categories:
        print("❌ No se pudieron obtener las categorías principales")
        return
    
    # Preparar datos para CSV
    csv_data = []
    
    # Procesar cada categoría
    for i, category in enumerate(categories[:10], 1):  # Limitar a 10 categorías para prueba
        print(f"\n📂 [{i}/{min(10, len(categories))}] Procesando: {category['name']}")
        
        # Obtener subcategorías
        subcategories = scrape_subcategories(category['url'], category['name'], headers)
        
        if not subcategories:
            # Si no hay subcategorías, agregar solo la categoría principal
            csv_data.append({
                'Categoria': category['name'],
                'Subcategoria': '',
                'Subseccion': ''
            })
        else:
            # Procesar cada subcategoría
            for j, subcategory in enumerate(subcategories[:5], 1):  # Limitar a 5 subcategorías por categoría
                print(f"  📁 [{j}/{min(5, len(subcategories))}] Subcategoría: {subcategory['name']}")
                
                # Intentar obtener subsecciones (tercer nivel)
                subsections = scrape_subcategories(subcategory['url'], subcategory['name'], headers)
                
                if not subsections:
                    # Si no hay subsecciones, agregar solo categoría y subcategoría
                    csv_data.append({
                        'Categoria': category['name'],
                        'Subcategoria': subcategory['name'],
                        'Subseccion': ''
                    })
                else:
                    # Agregar cada subsección
                    for subsection in subsections[:3]:  # Limitar a 3 subsecciones por subcategoría
                        csv_data.append({
                            'Categoria': category['name'],
                            'Subcategoria': subcategory['name'],
                            'Subseccion': subsection['name']
                        })
                
                # Pausa entre requests para no sobrecargar el servidor
                time.sleep(1)
        
        # Pausa entre categorías
        time.sleep(2)
    
    # Guardar en CSV
    if csv_data:
        filename = 'carrefour_categorias_completo.csv'
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Categoria', 'Subcategoria', 'Subseccion']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for row in csv_data:
                writer.writerow(row)
        
        print(f"\n✅ Scraping completado!")
        print(f"📄 Archivo generado: {filename}")
        print(f"📊 Total de registros: {len(csv_data)}")
        
        # Mostrar muestra de los datos
        print(f"\n📋 Muestra de los primeros 10 registros:")
        print("-" * 80)
        for i, row in enumerate(csv_data[:10], 1):
            print(f"{i:2d}. {row['Categoria']:<25} | {row['Subcategoria']:<25} | {row['Subseccion']}")
        
        if len(csv_data) > 10:
            print(f"... y {len(csv_data) - 10} registros más")
    
    else:
        print("❌ No se pudieron extraer datos")

# Ejecutar el scraping
if __name__ == "__main__":
    main()