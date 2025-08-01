#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import os

def setup_chrome_driver():
    """
    Configura y retorna el driver de Chrome
    """
    chrome_options = Options()
    
    # Configuraciones para mejor compatibilidad
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # User agent para parecer un navegador real
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # Intentar encontrar chromedriver en diferentes ubicaciones
    possible_paths = [
        "/usr/local/bin/chromedriver",
        "/opt/homebrew/bin/chromedriver",
        os.path.expanduser("~/chromedriver"),
        "chromedriver"  # Si está en PATH
    ]
    
    driver_path = None
    for path in possible_paths:
        if os.path.exists(path) or path == "chromedriver":
            driver_path = path
            break
    
    if driver_path and driver_path != "chromedriver":
        service = Service(driver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
    else:
        # Intentar sin especificar path (si está en PATH)
        driver = webdriver.Chrome(options=chrome_options)
    
    # Configurar script para evitar detección
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    return driver

def scrape_carrefour_categories():
    """
    Función principal que hace scraping de las categorías de Carrefour
    """
    print("🚀 Iniciando scraping de Carrefour con Selenium...")
    print("=" * 60)
    
    driver = None
    csv_data = []
    
    try:
        # Configurar driver
        print("🔧 Configurando ChromeDriver...")
        driver = setup_chrome_driver()
        
        # Navegar a Carrefour
        print("🌐 Navegando a Carrefour Argentina...")
        driver.get("https://www.carrefour.com.ar")
        
        # Esperar a que la página cargue
        print("⏳ Esperando que la página cargue...")
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # Esperar un poco más para que cargue el JavaScript
        time.sleep(3)
        
        print("🔍 Buscando el menú de categorías...")
        
        # Intentar diferentes selectores para encontrar el menú
        menu_selectors = [
            '[data-testid="menu"]',
            '.vtex-menu-2-x-styledLinkContainer',
            '.vtex-store-components-3-x-menuContainer',
            '[data-testid="store-menu"]',
            '.menu-container',
            'nav[role="navigation"]',
            '.category-menu',
            '.main-menu',
            '.navigation-menu'
        ]
        
        menu_found = False
        menu_element = None
        
        for selector in menu_selectors:
            try:
                menu_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if menu_elements:
                    menu_element = menu_elements[0]
                    print(f"✅ Menú encontrado con selector: {selector}")
                    menu_found = True
                    break
            except Exception as e:
                continue
        
        if not menu_found:
            print("⚠️  No se encontró el menú con selectores específicos.")
            print("🔍 Buscando enlaces de categorías en toda la página...")
            
            # Buscar todos los enlaces que podrían ser categorías
            all_links = driver.find_elements(By.TAG_NAME, "a")
            category_links = []
            
            known_categories = [
                'electro', 'tecnologia', 'bazar', 'textil', 'almacen',
                'desayuno', 'merienda', 'bebidas', 'lacteos', 'frescos',
                'carnes', 'pescados', 'frutas', 'verduras', 'panaderia',
                'congelados', 'limpieza', 'perfumeria', 'bebe', 'mascotas',
                'indumentaria', 'hogar'
            ]
            
            for link in all_links:
                try:
                    href = link.get_attribute('href') or ''
                    text = link.text.strip()
                    
                    if (text and len(text) > 2 and len(text) < 50 and
                        any(cat in href.lower() or cat in text.lower() for cat in known_categories)):
                        category_links.append({
                            'text': text,
                            'href': href,
                            'element': link
                        })
                except:
                    continue
            
            print(f"📋 Enlaces de categorías encontrados: {len(category_links)}")
            
            # Mostrar los primeros enlaces encontrados
            for i, link in enumerate(category_links[:10]):
                print(f"  {i+1}. {link['text']}: {link['href']}")
            
            # Intentar hacer hover sobre algunos enlaces para ver subcategorías
            print("\n🖱️  Explorando subcategorías con hover...")
            
            actions = ActionChains(driver)
            
            for i, link in enumerate(category_links[:5]):  # Solo los primeros 5
                try:
                    print(f"\n📂 Explorando: {link['text']}")
                    
                    # Hacer hover sobre el enlace
                    actions.move_to_element(link['element']).perform()
                    time.sleep(2)  # Esperar a que aparezca el submenu
                    
                    # Buscar submenús que aparezcan
                    submenu_selectors = [
                        '.submenu',
                        '.dropdown-menu',
                        '.category-submenu',
                        '.vtex-menu-2-x-submenuContainer',
                        '[data-testid="submenu"]'
                    ]
                    
                    subcategories_found = []
                    
                    for submenu_selector in submenu_selectors:
                        try:
                            submenu_elements = driver.find_elements(By.CSS_SELECTOR, submenu_selector)
                            for submenu in submenu_elements:
                                if submenu.is_displayed():
                                    sub_links = submenu.find_elements(By.TAG_NAME, "a")
                                    for sub_link in sub_links:
                                        sub_text = sub_link.text.strip()
                                        if sub_text and len(sub_text) > 2:
                                            subcategories_found.append(sub_text)
                        except:
                            continue
                    
                    if subcategories_found:
                        print(f"  📁 Subcategorías encontradas: {len(subcategories_found)}")
                        for subcat in subcategories_found[:5]:  # Mostrar solo las primeras 5
                            print(f"    - {subcat}")
                            csv_data.append({
                                'Categoria': link['text'],
                                'Subcategoria': subcat,
                                'Subseccion': ''
                            })
                    else:
                        print(f"  ⚠️  No se encontraron subcategorías para {link['text']}")
                        csv_data.append({
                            'Categoria': link['text'],
                            'Subcategoria': '',
                            'Subseccion': ''
                        })
                    
                    # Mover el mouse fuera para cerrar el submenu
                    actions.move_to_element(driver.find_element(By.TAG_NAME, "body")).perform()
                    time.sleep(1)
                    
                except Exception as e:
                    print(f"  ❌ Error explorando {link['text']}: {str(e)}")
                    continue
        
        else:
            # Si encontramos el menú, extraer categorías de él
            print("📋 Extrayendo categorías del menú...")
            
            try:
                category_links = menu_element.find_elements(By.TAG_NAME, "a")
                
                for link in category_links:
                    try:
                        text = link.text.strip()
                        href = link.get_attribute('href') or ''
                        
                        if text and len(text) > 2:
                            print(f"📂 Categoría encontrada: {text}")
                            csv_data.append({
                                'Categoria': text,
                                'Subcategoria': '',
                                'Subseccion': ''
                            })
                    except:
                        continue
                        
            except Exception as e:
                print(f"❌ Error extrayendo del menú: {str(e)}")
        
        print(f"\n📊 Total de registros extraídos: {len(csv_data)}")
        
    except Exception as e:
        print(f"❌ Error general: {str(e)}")
        
    finally:
        if driver:
            print("🔒 Cerrando navegador...")
            driver.quit()
    
    return csv_data

def save_to_csv(data, filename="carrefour_selenium_scraping.csv"):
    """
    Guarda los datos en un archivo CSV
    """
    if not data:
        print("❌ No hay datos para guardar")
        return False
    
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Categoria', 'Subcategoria', 'Subseccion']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for row in data:
                writer.writerow(row)
        
        print(f"✅ Archivo guardado: {filename}")
        print(f"📊 Registros guardados: {len(data)}")
        
        # Mostrar muestra de los datos
        print(f"\n📋 Muestra de los primeros 10 registros:")
        print("-" * 80)
        for i, row in enumerate(data[:10], 1):
            print(f"{i:2d}. {row['Categoria']:<25} | {row['Subcategoria']:<25} | {row['Subseccion']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error guardando archivo: {str(e)}")
        return False

# Función principal
def main():
    """
    Función principal que ejecuta todo el proceso
    """
    print("🎯 SCRAPER DE CARREFOUR CON SELENIUM")
    print("=" * 50)
    print("Este script va a:")
    print("1. Abrir Chrome en modo visible")
    print("2. Navegar a carrefour.com.ar")
    print("3. Extraer categorías y subcategorías")
    print("4. Guardar todo en un archivo CSV")
    print("=" * 50)
    
    # Ejecutar scraping
    data = scrape_carrefour_categories()
    
    # Guardar resultados
    if data:
        save_to_csv(data)
        print("\n🎉 ¡Scraping completado exitosamente!")
    else:
        print("\n❌ No se pudieron extraer datos")

if __name__ == "__main__":
    main()
