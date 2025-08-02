# jumbo_filters_to_csv.py
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

URL = "https://www.jumbo.com.ar/almacen"

def setup_driver(headless: bool = False):
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
        time.sleep(5)  # Tiempo adicional para JS y carga completa
        print("✅ Página cargada")
        return True
    except Exception as e:
        print(f"❌ Error esperando carga: {e}")
        return False

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

    # Scroll inicial al contenedor
    driver.execute_script("arguments[0].scrollIntoView(true);", container)
    time.sleep(1)

    # Scroll dentro del contenedor hacia abajo
    last_height = driver.execute_script("return arguments[0].scrollHeight", container)

    while True:
        # Scroll hacia abajo dentro del contenedor
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", container)
        time.sleep(2)

        # Calcular nueva altura
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
        # Re-encontrar el grupo por su texto (evita stale elements)
        group_elements = container.find_elements(By.XPATH, f".//div[contains(@class, 'vtex-search-result-3-x-filterTitle')]//span[contains(text(), '{group_name}')]")

        if not group_elements:
            print(f"  ❌ No se pudo re-encontrar el grupo: {group_name}")
            return []

        group_element = group_elements[0]

        # Scroll al grupo
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", group_element)
        time.sleep(1)

        # Encontrar el contenedor padre del grupo (el div completo del filtro)
        parent_container = group_element.find_element(By.XPATH, "./ancestor::div[contains(@class, 'vtex-search-result-3-x-filter__container')]")

        # Buscar botón "Mostrar N más" dentro de este grupo
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

        # Hacer clic en el botón si existe
        if see_more_button:
            try:
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", see_more_button)
                time.sleep(0.5)
                driver.execute_script("arguments[0].click();", see_more_button)
                print(f"  ✅ Click en botón 'Mostrar más'")
                time.sleep(2)  # Esperar a que carguen las opciones adicionales
            except Exception as e:
                print(f"  ⚠️  Error haciendo click en botón: {e}")
        else:
            print(f"  ℹ️  No hay botón 'Mostrar más' en este grupo")

        # Extraer todas las opciones clickeables del grupo
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

    # Primero, hacer scroll completo para revelar todos los grupos
    scroll_container_to_reveal_groups(container, driver)

    # Obtener lista de todos los grupos
    group_names = get_all_group_titles(container)

    if not group_names:
        print("❌ No se encontraron grupos")
        return {}

    # Procesar cada grupo individualmente
    all_data = {}
    for i, group_name in enumerate(group_names):
        options = process_single_group(container, driver, group_name, i)
        if options:
            all_data[group_name] = options

        # Pequeña pausa entre grupos
        time.sleep(1)

    return all_data

def pivot_to_csv(data: dict, out_file="jumbo_filtros.csv"):
    """Genera CSV con formato columnar"""
    if not data:
        print("❌ No hay datos para generar CSV")
        return

    print(f"📊 Generando CSV con {len(data)} grupos...")

    # Encontrar la longitud máxima
    max_len = max(len(opts) for opts in data.values()) if data else 0

    # Crear DataFrame columnar
    df_data = {}
    for group_name, options in data.items():
        # Rellenar con strings vacíos hasta max_len
        padded_options = options + [""] * (max_len - len(options))
        df_data[group_name] = padded_options

    df = pd.DataFrame(df_data)
    df.to_csv(out_file, index=False, encoding="utf-8-sig")
    print(f"✅ CSV generado: {out_file}")

    # Mostrar resumen
    for group, options in data.items():
        print(f"  📋 {group}: {len(options)} opciones")

if __name__ == "__main__":
    print("🚀 Iniciando scraper secuencial de filtros Jumbo...")

    driver = setup_driver(headless=False)  # Modo visible para debug
    wait = WebDriverWait(driver, 30)

    try:
        print(f"🌐 Navegando a: {URL}")
        driver.get(URL)

        # Esperar carga completa
        if not wait_for_page_load(driver, wait):
            print("❌ La página no cargó correctamente")
            exit(1)

        # Buscar contenedor de filtros
        container = find_filter_container(driver)
        if not container:
            print("❌ No se pudo encontrar el contenedor de filtros")
            exit(1)

        # Procesar todos los grupos secuencialmente
        filtros = scrape_all_groups_sequentially(container, driver)

        if filtros:
            # Generar CSV
            pivot_to_csv(filtros)
            print("🎉 ¡Proceso completado exitosamente!")
        else:
            print("❌ No se extrajeron datos")

    except Exception as e:
        print(f"❌ Error general: {e}")

    finally:
        input("Presiona Enter para cerrar el navegador...")
        driver.quit()