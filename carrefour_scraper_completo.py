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
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--headless=new")  # Headless moderno
    chrome_options.add_argument("--window-size=1920,1080")  # Tamaño de ventana virtual
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

def click_menu_button(driver):
    """
    Busca y hace clic en el botón del menú hamburguesa
    """
    print("🔍 Buscando el botón del menú hamburguesa...")
    
    # Selectores específicos para el botón del menú
    menu_button_selectors = [
        'div[role="button"].carrefourar-mega-menu-0-x-closedMenu',
        '.vtex-store-drawer-0-x-drawerTriggerContainer--menuIconDrawer',
        '.vtex-store-drawer-0-x-openIconContainer--menuCategoryMobile',
        '.carrefourar-mega-menu-0-x-closedMenu',
        '[role="button"][class*="closedMenu"]',
        '[class*="drawerTriggerContainer"]',
        '[class*="openIconContainer"]'
    ]
    
    for selector in menu_button_selectors:
        try:
            print(f"  🔍 Probando selector: {selector}")
            menu_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
            )
            
            if menu_button:
                print(f"  ✅ Botón encontrado con selector: {selector}")
                
                # Hacer clic en el botón
                print("  🖱️  Haciendo clic en el botón del menú...")
                driver.execute_script("arguments[0].click();", menu_button)
                
                # Esperar un momento para que se abra el menú
                time.sleep(3)
                
                return True
                
        except Exception as e:
            print(f"  ❌ No funciona selector {selector}: {str(e)}")
            continue
    
    print("❌ No se pudo encontrar el botón del menú")
    return False

def extract_all_categories(driver):
    """
    Extrae todas las categorías y subcategorías del menú abierto
    """
    print("📋 Extrayendo todas las categorías del menú abierto...")
    
    csv_data = []
    
    try:
        # Esperar a que el menú vertical esté visible
        print("⏳ Esperando que el menú se despliegue completamente...")
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.carrefourar-mega-menu-0-x-openMenu'))
        )
        
        # Buscar todos los <li> de categorías principales
        print("🔍 Buscando elementos <li> de categorías principales...")
        category_lis = driver.find_elements(By.CSS_SELECTOR, 'li.carrefourar-mega-menu-0-x-menuItemVertical')
        
        print(f"📊 Elementos <li> encontrados: {len(category_lis)}")
        
        for i, li in enumerate(category_lis, 1):
            try:
                # El texto de la categoría está en un <div> con clase carrefourar-mega-menu-0-x-styledLinkText
                text_div = li.find_element(By.CSS_SELECTOR, 'div.carrefourar-mega-menu-0-x-styledLinkText')
                category_name = text_div.text.strip()
                
                if category_name:
                    print(f"  📂 {i:2d}. Categoría encontrada: {category_name}")
                    
                    # Agregar la categoría principal al CSV
                    csv_data.append({
                        'Categoria': category_name,
                        'Subcategoria': '',
                        'Subseccion': ''
                    })
                    
                    # Intentar hacer hover para ver subcategorías
                    try:
                        print(f"    🖱️  Explorando subcategorías de: {category_name}")
                        
                        # Hacer hover sobre el elemento
                        actions = ActionChains(driver)
                        actions.move_to_element(li).perform()
                        time.sleep(2)  # Esperar a que aparezca el submenu
                        
                        # Buscar submenús que aparezcan
                        submenu_selectors = [
                            '.carrefourar-mega-menu-0-x-submenuContainer',
                            '.carrefourar-mega-menu-0-x-submenu',
                            '.submenu',
                            '.dropdown-menu',
                            '.category-submenu',
                            '[data-testid="submenu"]'
                        ]
                        
                        subcategories_found = []
                        
                        for submenu_selector in submenu_selectors:
                            try:
                                submenu_elements = driver.find_elements(By.CSS_SELECTOR, submenu_selector)
                                for submenu in submenu_elements:
                                    if submenu.is_displayed():
                                        # Buscar enlaces dentro del submenu
                                        sub_links = submenu.find_elements(By.TAG_NAME, "a")
                                        for sub_link in sub_links:
                                            sub_text = sub_link.text.strip()
                                            if sub_text and len(sub_text) > 2 and len(sub_text) < 100:
                                                subcategories_found.append(sub_text)
                                        
                                        # También buscar divs con texto
                                        sub_divs = submenu.find_elements(By.CSS_SELECTOR, 'div[class*="styledLinkText"]')
                                        for sub_div in sub_divs:
                                            sub_text = sub_div.text.strip()
                                            if sub_text and len(sub_text) > 2 and len(sub_text) < 100:
                                                subcategories_found.append(sub_text)
                            except:
                                continue
                        
                        # Eliminar duplicados
                        subcategories_found = list(set(subcategories_found))
                        
                        if subcategories_found:
                            print(f"    📁 Subcategorías encontradas: {len(subcategories_found)}")
                            for j, subcat in enumerate(subcategories_found[:10], 1):  # Mostrar solo las primeras 10
                                print(f"      {j:2d}. {subcat}")
                                csv_data.append({
                                    'Categoria': category_name,
                                    'Subcategoria': subcat,
                                    'Subseccion': ''
                                })
                        else:
                            print(f"    ⚠️  No se encontraron subcategorías para {category_name}")
                        
                        # Mover el mouse fuera para cerrar el submenu
                        actions.move_to_element(driver.find_element(By.TAG_NAME, "body")).perform()
                        time.sleep(1)
                        
                    except Exception as e:
                        print(f"    ❌ Error explorando subcategorías de {category_name}: {str(e)}")
                        continue
                
            except Exception as e:
                print(f"  ❌ No se pudo extraer el nombre de la categoría {i}: {str(e)}")
                continue
        
        print(f"\n📊 Total de registros extraídos: {len(csv_data)}")
        
    except Exception as e:
        print(f"❌ Error general extrayendo categorías: {str(e)}")
    
    return csv_data

def scrape_carrefour_categories():
    """
    Función principal que hace scraping de las categorías de Carrefour
    """
    print("🚀 Iniciando scraping completo de Carrefour con Selenium...")
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
        time.sleep(5)
        
        # Hacer clic en el botón del menú
        menu_opened = click_menu_button(driver)
        
        if menu_opened:
            print("✅ Menú abierto exitosamente")
            
            # Esperar a que el menú se despliegue completamente
            time.sleep(3)
            
            # Extraer todas las categorías del menú abierto
            csv_data = extract_all_categories(driver)
            
        else:
            print("❌ No se pudo abrir el menú")
            
        print(f"\n📊 Resumen final: {len(csv_data)} registros extraídos")
        
    except Exception as e:
        print(f"❌ Error general: {str(e)}")
        
    finally:
        if driver:
            print("🔒 Cerrando navegador...")
            driver.quit()
    
    return csv_data

def save_to_csv(data, filename="carrefour_categorias_completo.csv"):
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
        
        # Mostrar estadísticas
        categories = set(row['Categoria'] for row in data)
        subcategories = set(row['Subcategoria'] for row in data if row['Subcategoria'])
        
        print(f"\n📈 Estadísticas:")
        print(f"  📂 Categorías principales: {len(categories)}")
        print(f"  📁 Subcategorías: {len(subcategories)}")
        
        # Mostrar muestra de los datos
        print(f"\n📋 Muestra de los primeros 20 registros:")
        print("-" * 80)
        for i, row in enumerate(data[:20], 1):
            print(f"{i:2d}. {row['Categoria']:<30} | {row['Subcategoria']:<25} | {row['Subseccion']}")
        
        if len(data) > 20:
            print(f"... y {len(data) - 20} registros más")
        
        return True
        
    except Exception as e:
        print(f"❌ Error guardando archivo: {str(e)}")
        return False

# Función principal
def main():
    """
    Función principal que ejecuta todo el proceso
    """
    print("🎯 SCRAPER COMPLETO DE CARREFOUR CON SELENIUM")
    print("=" * 55)
    print("Este script va a:")
    print("1. Abrir Chrome en modo headless")
    print("2. Navegar a carrefour.com.ar")
    print("3. Hacer clic en el botón del menú hamburguesa")
    print("4. Extraer TODAS las categorías y subcategorías")
    print("5. Guardar todo en un archivo CSV completo")
    print("=" * 55)
    
    # Ejecutar scraping
    data = scrape_carrefour_categories()
    
    # Guardar resultados
    if data:
        save_to_csv(data)
        print("\n🎉 ¡Scraping completado exitosamente!")
        print("\n📄 El archivo CSV está listo para usar.")
    else:
        print("\n❌ No se pudieron extraer datos")

if __name__ == "__main__":
    main()
