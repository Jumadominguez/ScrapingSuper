# jumbo_complete_scraper.py
# Requiere: selenium, pandas, webdriver_manager
# > pip install selenium pandas webdriver-manager

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import pandas as pd
import time
import os
from urllib.parse import urlparse

HOME_URL = "https://www.jumbo.com.ar/"

def setup_driver(headless: bool = True):
    opts = Options()
    if headless:
        opts.add_argument("--headless=new")
    opts.add_argument("--window-size=1920,1080")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option('useAutomationExtension', False)
    opts.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)

def wait_for_page_load(driver, wait):
    """Espera a que la página cargue completamente"""
    print("🔄 Esperando que cargue la página...")
    try:
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(5)
        print("✅ Página cargada")
        return True
    except Exception as e:
        print(f"❌ Error esperando carga: {e}")
        return False

def deploy_categories_menu(driver, wait):
    """Despliega el menú de categorías haciendo hover sobre el botón CATEGORÍAS"""
    print("🔄 Desplegando menú de categorías...")
    
    try:
        categories_button = wait.until(
            EC.element_to_be_clickable((
                By.XPATH,
                "//nav[contains(@class, 'menuContainerNav--category-menu')]//div[contains(@class, 'vtex-menu-2-x-styledLinkContent--header-category') and contains(text(), 'CATEGORÍAS')]"
            ))
        )
        
        print("✅ Botón 'CATEGORÍAS' encontrado")
        ActionChains(driver).move_to_element(categories_button).perform()
        time.sleep(2)
        print("✅ Hover realizado sobre 'CATEGORÍAS'")
        return True
        
    except Exception as e:
        print(f"❌ Error desplegando menú: {e}")
        return False

def get_all_category_links(driver, wait):
    """Obtiene todos los enlaces de categorías del menú desplegado"""
    print("🔄 Obteniendo enlaces de todas las categorías...")
    
    try:
        # Selectores para encontrar enlaces de categorías
        category_selectors = [
            "//div[contains(@class, 'vtex-menu-2-x-submenu')]//a",
            "//div[contains(@class, 'vtex-menu-2-x-menuDropdown')]//a",
            "//ul[contains(@class, 'vtex-menu-2-x-submenuList')]//a",
            "//div[contains(@class, 'submenu')]//a",
            "//*[contains(@class, 'vtex-menu')]//a[@href*='jumbo.com.ar']"
        ]
        
        category_links = []
        for selector in category_selectors:
            try:
                elements = driver.find_elements(By.XPATH, selector)
                if elements:
                    for element in elements:
                        if element.is_displayed():
                            href = element.get_attribute('href')
                            text = element.text.strip()
                            if href and text and 'jumbo.com.ar' in href:
                                # Evitar duplicados
                                if not any(link['href'] == href for link in category_links):
                                    category_links.append({
                                        'name': text,
                                        'href': href,
                                        'element': element
                                    })
                    
                    if category_links:
                        print(f"✅ Encontrados {len(category_links)} enlaces con: {selector}")
                        break
                        
            except Exception as e:
                print(f"⚠️  Selector {selector} falló: {e}")
        
        if category_links:
            print("📋 Categorías encontradas:")
            for i, link in enumerate(category_links, 1):
                print(f"  {i}. {link['name']} -> {link['href']}")
        
        return category_links
        
    except Exception as e:
        print(f"❌ Error obteniendo enlaces: {e}")
        return []

def scrape_category_filters(driver, wait, category_url, category_name):
    """Ejecuta la lógica de menuScraperJumbo.py sobre una categoría específica"""
    print(f"🔄 Scrapeando filtros de: {category_name}")
    
    try:
        # Navegar a la categoría
        driver.get(category_url)
        
        if not wait_for_page_load(driver, wait):
            print(f"❌ No se pudo cargar la página de {category_name}")
            return False
        
        # Buscar contenedor de filtros
        container = find_filter_container(driver)
        if not container:
            print(f"❌ No se encontró contenedor de filtros en {category_name}")
            return False
        
        # Procesar todos los grupos secuencialmente
        filtros = scrape_all_groups_sequentially(container, driver)
        
        if filtros:
            # Generar CSV con nombre de la categoría
            safe_name = "".join(c for c in category_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            csv_filename = f"filtros_{safe_name.replace(' ', '_').lower()}.csv"
            pivot_to_csv(filtros, csv_filename)
            print(f"✅ CSV generado para {category_name}: {csv_filename}")
            return True
        else:
            print(f"⚠️  No se extrajeron datos de {category_name}")
            return False
            
    except Exception as e:
        print(f"❌ Error scrapeando {category_name}: {e}")
        return False

# Funciones del menuScraperJumbo.py adaptadas
def find_filter_container(driver):
    """Busca el contenedor de filtros"""
    selectors = [
        "aside[class*='vtex-search-result-3-x-filter__filtersWrapper']",
        "aside[class*='filtersWrapper']",
        "[class*='filter'][class*='Wrapper']"
    ]

    for selector in selectors:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if elements:
                print(f"✅ Contenedor encontrado con: {selector}")
                return elements[0]
        except Exception as e:
            print(f"⚠️  Selector {selector} falló: {e}")

    print("❌ No se encontró el contenedor de filtros")
    return None

def scroll_container_to_reveal_groups(container, driver):
    """Hace scroll en el contenedor para revelar todos los grupos"""
    print("🔄 Scrolleando contenedor para revelar todos los grupos...")

    driver.execute_script("arguments[0].scrollIntoView(true);", container)
    time.sleep(1)

    last_height = driver.execute_script("return arguments[0].scrollHeight", container)

    while True:
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", container)
        time.sleep(2)

        new_height = driver.execute_script("return arguments[0].scrollHeight", container)
        if new_height == last_height:
            break
        last_height = new_height

    print("✅ Scroll completo del contenedor")

def get_all_group_titles(container):
    """Obtiene todos los títulos de grupos disponibles"""
    title_selectors = [
        "div.vtex-search-result-3-x-filterTitle",
        "div[class*='vtex-search-result-3-x-filterTitle']",
        "[class*='filterTitle']"
    ]

    for selector in title_selectors:
        try:
            groups = container.find_elements(By.CSS_SELECTOR, selector)
            if groups:
                group_names = [grp.text.strip() for grp in groups if grp.text.strip()]
                print(f"✅ Encontrados {len(group_names)} grupos: {group_names}")
                return group_names
        except Exception as e:
            print(f"⚠️  Error con selector {selector}: {e}")

    return []

def process_single_group(container, driver, group_name, group_index):
    """Procesa un grupo específico: encuentra botón 'mostrar más' y extrae opciones"""
    print(f"📂 Procesando grupo {group_index + 1}: {group_name}")

    try:
        group_elements = container.find_elements(By.XPATH, f".//div[contains(@class, 'vtex-search-result-3-x-filterTitle')]//span[contains(text(), '{group_name}')]")

        if not group_elements:
            print(f"  ❌ No se pudo re-encontrar el grupo: {group_name}")
            return []

        group_element = group_elements[0]
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", group_element)
        time.sleep(1)

        parent_container = group_element.find_element(By.XPATH, "./ancestor::div[contains(@class, 'vtex-search-result-3-x-filter__container')]")

        see_more_selectors = [
            ".//div[contains(@class, 'vtex-search-result-3-x-filter__seeMoreButton')]",
            ".//div[contains(@class, 'seeMoreButton')]",
            ".//div[contains(@class, 'seeMore')]",
            ".//button[contains(text(), 'Mostrar')]",
            ".//div[contains(text(), 'Mostrar')]"
        ]

        see_more_button = None
        for selector in see_more_selectors:
            try:
                buttons = parent_container.find_elements(By.XPATH, selector)
                if buttons:
                    see_more_button = buttons[0]
                    print(f"  ✅ Botón 'Mostrar más' encontrado: {see_more_button.text}")
                    break
            except Exception as e:
                print(f"  ⚠️  Error buscando botón con {selector}: {e}")

        if see_more_button:
            try:
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", see_more_button)
                time.sleep(0.5)
                driver.execute_script("arguments[0].click();", see_more_button)
                print(f"  ✅ Click en botón 'Mostrar más'")
                time.sleep(2)
            except Exception as e:
                print(f"  ⚠️  Error haciendo click en botón: {e}")
        else:
            print(f"  ℹ️  No hay botón 'Mostrar más' en este grupo")

        option_selectors = [
            ".//label[contains(@class, 'vtex-checkbox__label') and contains(@class, 'w-100') and contains(@class, 'c-on-base') and contains(@class, 'pointer')]",
            ".//label[contains(@class, 'vtex-checkbox__label')]",
            ".//label[contains(@class, 'checkbox')]"
        ]

        options = []
        for opt_selector in option_selectors:
            try:
                found_options = parent_container.find_elements(By.XPATH, opt_selector)
                if found_options:
                    options = [lbl.text.strip() for lbl in found_options if lbl.text.strip()]
                    print(f"  ✅ {len(options)} opciones encontradas")
                    break
            except Exception as e:
                print(f"  ⚠️  Error extrayendo opciones con {opt_selector}: {e}")

        if not options:
            print(f"  ⚠️  No se encontraron opciones para {group_name}")

        return options

    except Exception as e:
        print(f"  ❌ Error procesando grupo {group_name}: {e}")
        return []

def scrape_all_groups_sequentially(container, driver):
    """Procesa todos los grupos secuencialmente"""
    print("🔄 Iniciando procesamiento secuencial de grupos...")

    scroll_container_to_reveal_groups(container, driver)
    group_names = get_all_group_titles(container)

    if not group_names:
        print("❌ No se encontraron grupos")
        return {}

    all_data = {}
    for i, group_name in enumerate(group_names):
        options = process_single_group(container, driver, group_name, i)
        if options:
            all_data[group_name] = options
        time.sleep(1)

    return all_data

def pivot_to_csv(data: dict, out_file):
    """Genera CSV con formato columnar"""
    if not data:
        print("❌ No hay datos para generar CSV")
        return

    print(f"📊 Generando CSV con {len(data)} grupos...")

    max_len = max(len(opts) for opts in data.values()) if data else 0

    df_data = {}
    for group_name, options in data.items():
        padded_options = options + [""] * (max_len - len(options))
        df_data[group_name] = padded_options

    df = pd.DataFrame(df_data)
    
    # Obtener el path absoluto del script actual
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    
    # Subir dos niveles y armar la ruta relativa
    BASE_PATH = os.path.join(SCRIPT_DIR, "..", "..", "database", "menu", "jumbo")
    BASE_PATH = os.path.abspath(BASE_PATH)  # Normaliza la ruta
    
    # Crear la carpeta si no existe
    os.makedirs(BASE_PATH, exist_ok=True)
    
    # Guardar el CSV en el path correcto
    csv_fullpath = os.path.join(BASE_PATH, out_file)
    df.to_csv(csv_fullpath, index=False, encoding="utf-8-sig")
    print(f"✅ CSV generado: {csv_fullpath}")

    for group, options in data.items():
        print(f"  📋 {group}: {len(options)} opciones")

def main():
    print("🚀 Iniciando scraper completo de todas las categorías de Jumbo...")
    
    driver = setup_driver(headless=True)
    wait = WebDriverWait(driver, 30)

    try:
        print(f"🌐 Navegando al home: {HOME_URL}")
        driver.get(HOME_URL)
        
        if not wait_for_page_load(driver, wait):
            print("❌ La página home no cargó correctamente")
            return
        
        # Desplegar menú de categorías
        if not deploy_categories_menu(driver, wait):
            print("❌ No se pudo desplegar el menú de categorías")
            return
        
        # Obtener todos los enlaces de categorías
        category_links = get_all_category_links(driver, wait)
        if not category_links:
            print("❌ No se encontraron enlaces de categorías")
            return
        
        print(f"🎯 Procesando {len(category_links)} categorías...")
        
        # Procesar cada categoría
        successful_categories = 0
        for i, category in enumerate(category_links, 1):
            print(f"\n{'='*60}")
            print(f"📂 Procesando categoría {i}/{len(category_links)}: {category['name']}")
            print(f"🔗 URL: {category['href']}")
            print(f"{'='*60}")
            
            if scrape_category_filters(driver, wait, category['href'], category['name']):
                successful_categories += 1
                print(f"✅ Categoría {category['name']} procesada exitosamente")
            else:
                print(f"❌ Error procesando categoría {category['name']}")
            
            # Volver al home para la siguiente categoría
            if i < len(category_links):  # No volver al home en la última iteración
                print("🔄 Volviendo al home para la siguiente categoría...")
                driver.get(HOME_URL)
                if wait_for_page_load(driver, wait):
                    if not deploy_categories_menu(driver, wait):
                        print("⚠️  Error desplegando menú para siguiente categoría")
                        break
                else:
                    print("⚠️  Error cargando home para siguiente categoría")
                    break
        
        print(f"\n🎉 ¡Proceso completado!")
        print(f"📊 Categorías procesadas exitosamente: {successful_categories}/{len(category_links)}")

    except Exception as e:
        print(f"❌ Error general: {e}")
        
    finally:
        input("Presiona Enter para cerrar el navegador...")
        driver.quit()

if __name__ == "__main__":
    main()