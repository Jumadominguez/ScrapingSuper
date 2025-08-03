from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import ElementClickInterceptedException, StaleElementReferenceException, TimeoutException
import csv, time, json, os, re
from datetime import datetime

HOME_URL = "https://www.jumbo.com.ar/"

# --- Configurar navegador SIN headless para que puedas ver ---
options = Options()
options.add_argument("--log-level=3")    # Solo errores críticos
options.add_argument("--window-size=1920,1080")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
# NO agregamos --headless para que puedas ver el navegador
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

def wait_for_page_load(driver, timeout=15):
    """Espera a que la página se cargue completamente"""
    try:
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        time.sleep(3)  # Tiempo adicional para elementos dinámicos
        return True
    except:
        return False

def deploy_categories_menu(driver):
    """Despliega el menú de categorías haciendo hover sobre el botón CATEGORÍAS"""
    print("🔄 Desplegando menú de categorías...")
    
    try:
        wait = WebDriverWait(driver, 15)
        categories_button = wait.until(
            EC.element_to_be_clickable((
                By.XPATH,
                "//nav[contains(@class, 'menuContainerNav--category-menu')]//div[contains(@class, 'vtex-menu-2-x-styledLinkContent--header-category') and contains(text(), 'CATEGORÍAS')]"
            ))
        )
        
        print("✅ Botón 'CATEGORÍAS' encontrado")
        ActionChains(driver).move_to_element(categories_button).perform()
        time.sleep(3)
        print("✅ Hover realizado sobre 'CATEGORÍAS'")
        return True
        
    except Exception as e:
        print(f"❌ Error desplegando menú: {e}")
        return False

def get_all_category_links(driver):
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
                                        'href': href
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

def find_category_url(category_links, category_name):
    """Busca la URL de una categoría específica"""
    for link in category_links:
        if category_name.lower() in link['name'].lower():
            # Verificar que sea exactamente la categoría y no una subcategoría
            if link['name'].lower().strip() == category_name.lower():
                return link['href']
    
    # Si no encuentra exacto, buscar que contenga la palabra
    for link in category_links:
        if category_name.lower() in link['name'].lower():
            return link['href']
    
    return None

def navigate_to_category_url(driver, category_name, url):
    """Navega directamente a la URL de la categoría"""
    try:
        print(f"🌐 Navegando a {category_name}: {url}")
        driver.get(url)
        wait_for_page_load(driver)
        
        # Verificar que llegamos a la página correcta
        try:
            # Buscar indicadores de que estamos en la página correcta
            page_indicators = [
                "//div[contains(@class, 'vtex-search-result')]",
                "//div[contains(@class, 'gallery')]",
                "//div[contains(@class, 'search-result')]"
            ]
            
            for indicator in page_indicators:
                try:
                    WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, indicator))
                    )
                    print(f"✅ Página de {category_name} cargada correctamente")
                    return True
                except:
                    continue
                    
            print(f"⚠️ Página cargada pero sin indicadores claros de {category_name}")
            return True
            
        except Exception as e:
            print(f"⚠️ No se pudieron verificar indicadores, pero continuando: {e}")
            return True
            
    except Exception as e:
        print(f"❌ Error navegando a {category_name}: {e}")
        return False

def scroll_filters_panel(driver, max_scrolls=10):
    """Hace scroll en el panel de filtros para asegurar que se carguen todos los filtros"""
    for i in range(max_scrolls):
        driver.execute_script("window.scrollBy(0, 200);")
        time.sleep(0.5)

def find_and_expand_filter_section(driver, section_name, max_attempts=20):
    """Busca la sección de filtros haciendo scroll incremental hasta encontrarla y la expande si tiene botón 'Mostrar más'"""
    print(f"🔍 Buscando sección '{section_name}' con scroll incremental...")

    xpath = f"//span[text()='{section_name}']/ancestor::div[contains(@class, 'vtex-search-result-3-x-filter__container')]"

    for attempt in range(max_attempts):
        try:
            filter_section = driver.find_element(By.XPATH, xpath)
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", filter_section)
            time.sleep(1)
            print(f"✅ Sección '{section_name}' encontrada y visible")

            # Expandir si hay botón "Mostrar más"
            try:
                show_more_button = filter_section.find_element(By.XPATH, ".//button[contains(text(), 'Mostrar')]")
                show_more_button.click()
                time.sleep(2)
                print(f"✅ Sección {section_name} expandida")
            except:
                print(f"ℹ️ No hay botón 'Mostrar más' en {section_name}")
            return True
        except:
            # Scroll incremental hacia abajo
            driver.execute_script("window.scrollBy(0, 200);")
            time.sleep(0.5)
    print(f"❌ No se encontró la sección {section_name} después de scrollear")
    return False

def get_filter_options(driver, section_name):
    """Obtiene todas las opciones clickeables de una sección de filtros"""
    print(f"🔍 Obteniendo opciones de filtro de '{section_name}'...")

    # Usar el mismo XPATH robusto para la sección
    xpath = f"//span[text()='{section_name}']/ancestor::div[contains(@class, 'vtex-search-result-3-x-filter__container')]"
    try:
        filter_section = driver.find_element(By.XPATH, xpath)
        # Buscar todos los labels dentro de la sección
        options = filter_section.find_elements(By.XPATH, ".//label[contains(@class, 'vtex-checkbox__label')]")
        print(f"✅ Encontradas {len(options)} opciones de filtro en '{section_name}'")
        return options
    except Exception as e:
        print(f"❌ Error obteniendo opciones de {section_name}: {e}")
        return []

def click_filter_option(driver, option, select=True, max_retries=3):
    """Clickea una opción de filtro para seleccionar/deseleccionar con manejo de errores y reintentos"""
    option_text = ""
    for attempt in range(max_retries):
        try:
            option_text = option.text.strip()

            # Scroll al elemento centrado
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", option)
            time.sleep(1)

            wait = WebDriverWait(driver, 10)
            wait.until(EC.element_to_be_clickable(option))

            try:
                option.click()
            except ElementClickInterceptedException:
                print(f"⚠️ Click interceptado, intentando click con JS en: {option_text}")
                driver.execute_script("arguments[0].click();", option)

            time.sleep(4)  # Esperar a que se carguen los productos filtrados

            action = "seleccionada" if select else "deseleccionada"
            print(f"✅ Opción {action}: {option_text}")
            return True

        except StaleElementReferenceException:
            print(f"⚠️ StaleElementReferenceException en opción '{option_text}', reintentando ({attempt+1}/{max_retries})...")
            # Rebuscar el elemento antes de reintentar
            try:
                xpath = f".//label[contains(text(), '{option_text}')]"
                option = driver.find_element(By.XPATH, xpath)
            except Exception:
                pass
            time.sleep(2)

        except TimeoutException:
            print(f"⚠️ Timeout esperando que opción '{option_text}' sea clickable, reintentando ({attempt+1}/{max_retries})...")
            time.sleep(2)

        except Exception as e:
            print(f"❌ Error clickeando opción '{option_text}': {e}")
            break

    print(f"❌ No se pudo clickear la opción '{option_text}' después de {max_retries} intentos")
    return False

def check_and_reload_aw_snap(driver, max_retries=3):
    """Detecta pantalla 'Aw Snap!' y recarga la página si aparece"""
    for attempt in range(max_retries):
        try:
            aw_snap_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Aw, Snap!')]")
            if aw_snap_elements:
                print("⚠️ Pantalla 'Aw Snap!' detectada, recargando página...")
                driver.refresh()
                wait_for_page_load(driver)
                time.sleep(3)
                continue
            else:
                return False
        except Exception as e:
            print(f"⚠️ Error detectando 'Aw Snap!': {e}")
            time.sleep(2)
    return False

def extract_product_info(product_element):
    """Extrae información de un producto individual"""
    try:
        base_url = "https://www.jumbo.com.ar"

        # Nombre del producto
        try:
            nombre_elem = product_element.find_element(By.CLASS_NAME, "vtex-product-summary-2-x-productBrand")
            nombre = nombre_elem.text.strip()
        except:
            try:
                nombre_elem = product_element.find_element(By.XPATH, ".//span[contains(@class, 'productBrand')]")
                nombre = nombre_elem.text.strip()
            except:
                nombre = "Sin nombre"

        # Marca
        try:
            marca_elem = product_element.find_element(By.CLASS_NAME, "vtex-product-summary-2-x-productBrandName")
            marca = marca_elem.text.strip()
        except:
            marca = "SIN MARCA"

        # URL del producto (relativa)
        try:
            url_elem = product_element.find_element(By.XPATH, ".//a[contains(@class, 'vtex-product-summary-2-x-clearLink')]")
            href = url_elem.get_attribute('href')
            if href:
                if href.startswith("/"):
                    url = base_url + href
                else:
                    url = href
            else:
                url = ""
        except:
            url = ""

        # Precio regular (por kg, etc.) - solo la parte antes de "PRECIO SIN IMPUESTOS NACIONALES"
        try:
            precio_regular_elem = product_element.find_element(By.XPATH, ".//span[contains(@class, 'vtex-custom-unit-price')]")
            precio_regular_text = precio_regular_elem.text.strip()
            precio_regular = precio_regular_text.split("PRECIO SIN IMPUESTOS NACIONALES")[0].strip()
        except:
            precio_regular = ""

        return {
            'nombre': nombre,
            'marca': marca,
            'url': url,
            'precio_regular': precio_regular
        }
    except Exception as e:
        print(f"❌ Error extrayendo info del producto: {e}")
        return None

def scrape_products_on_page(driver):
    """Scrapea todos los productos visibles en la página actual"""
    try:
        print("🔍 Scrapeando productos en la página...")

        # Scroll para cargar todos los productos
        last_height = driver.execute_script("return document.body.scrollHeight")
        for i in range(5):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        # Buscar productos
        product_selectors = [
            "vtex-product-summary-2-x-element",
            "vtex-product-summary-2-x-container",
            "product-summary"
        ]

        products = []
        for selector in product_selectors:
            try:
                product_elements = driver.find_elements(By.CLASS_NAME, selector)
                if product_elements:
                    products = product_elements
                    print(f"✅ Encontrados {len(products)} productos usando selector: {selector}")
                    break
            except:
                continue

        if not products:
            print("❌ No se encontraron productos en la página")
            return []

        # Extraer información de cada producto
        productos_info = []
        for i, product in enumerate(products, 1):
            info = extract_product_info(product)
            if info:
                productos_info.append(info)
                if i <= 3:  # Mostrar info de los primeros 3 productos
                    print(f"📦 Producto {i}: {info['nombre'][:50]}...")

        print(f"✅ Información extraída de {len(productos_info)} productos")
        return productos_info
    except Exception as e:
        print(f"❌ Error scrapeando productos: {e}")
        return []

def convertir_a_float(precio_str):
    """Convierte string de precio a float"""
    try:
        limpio = re.sub(r"[^\d,]", "", precio_str).replace(",", ".")
        return float(limpio)
    except:
        return None

def process_category_with_filters(driver, category_name, category_url, max_retries=3):
    print(f"\n🔄 Procesando categoría: {category_name}")

    if not navigate_to_category_url(driver, category_name, category_url):
        return []

    scroll_filters_panel(driver)

    if not find_and_expand_filter_section(driver, "Tipo de Producto"):
        print("ℹ️ No se encontraron filtros, scrapeando todos los productos...")
        products = scrape_products_on_page(driver)
        for product in products:
            product['categoria'] = category_name
            product['tipo_de_producto'] = "Todos"
            product['filtro'] = "Todos"
        return products

    all_products = []
    for attempt in range(max_retries):
        try:
            filter_options = get_filter_options(driver, "Tipo de Producto")
            if not filter_options:
                print("ℹ️ No se encontraron opciones de filtro, scrapeando todos los productos...")
                products = scrape_products_on_page(driver)
                for product in products:
                    product['categoria'] = category_name
                    product['tipo_de_producto'] = "Todos"
                    product['filtro'] = "Todos"
                return products

            # Limitar a los primeros 5 filtros
            filter_options = filter_options[:5]

            for i, option in enumerate(filter_options):
                option_name = option.text.strip()
                print(f"\n📋 Procesando opción {i+1}/{len(filter_options)}: {option_name}")

                if click_filter_option(driver, option, select=True):
                    products = scrape_products_on_page(driver)
                    for product in products:
                        product['categoria'] = category_name
                        product['tipo_de_producto'] = option_name
                        product['filtro'] = option_name
                    all_products.extend(products)
                    print(f"✅ Scrapeados {len(products)} productos para {option_name}")
                    click_filter_option(driver, option, select=False)
            return all_products

        except StaleElementReferenceException:
            print(f"⚠️ StaleElementReferenceException detectado, reintentando obtener filtros y productos (intento {attempt+1}/{max_retries})...")
            time.sleep(3)
            continue

    print("❌ No se pudo completar el scraping debido a StaleElementReferenceException persistente.")
    return all_products

def save_to_csv(products, filename):
    """Guarda los productos en CSV con formato Carrefour y columna 'Tipo de Producto'"""
    encabezados = [
        "ID_Producto", "Categoria", "Tipo de Producto", "Nombre", "Marca", "URL",
        "Precio_regular", "Precio_float", "Fecha", "Filtro"
    ]

    output_dir = "./Scraping Super/database/productos/DBproductos"
    os.makedirs(output_dir, exist_ok=True)
    csv_path = os.path.join(output_dir, filename)

    with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(encabezados)

        for i, product in enumerate(products, 1):
            precio_float = convertir_a_float(product.get('precio_regular', ''))

            writer.writerow([
                f"P{i}",
                product.get('categoria', ''),
                product.get('tipo_de_producto', ''),  # NUEVA COLUMNA
                product.get('nombre', ''),
                product.get('marca', ''),
                product.get('url', ''),
                product.get('precio_regular', ''),
                precio_float,
                datetime.today().strftime('%Y-%m-%d'),
                product.get('filtro', '')
            ])

    print(f"✅ CSV guardado con {len(products)} productos en {csv_path}")

# --- Ejecución principal ---
try:
    print("🚀 Iniciando scraper de Jumbo...")
    print("👁️ Navegador visible para debugging")
    print("🎯 Extracción dinámica de URLs de categorías")
    print("🔍 Búsqueda robusta de filtros 'Tipo de Producto'")

    # 1. Ir a la página principal
    print("\n🌐 Navegando a jumbo.com.ar...")
    driver.get(HOME_URL)
    wait_for_page_load(driver)

    # 2. Desplegar menú de categorías
    if not deploy_categories_menu(driver):
        raise Exception("No se pudo desplegar el menú de categorías")

    # 3. Obtener todas las URLs de categorías
    category_links = get_all_category_links(driver)
    if not category_links:
        raise Exception("No se pudieron obtener las URLs de categorías")

    # 4. Buscar URLs específicas de Carnes y Rotisería
    target_categories = ["Carnes", "Rotisería"]
    found_categories = {}

    for category_name in target_categories:
        url = find_category_url(category_links, category_name)
        if url:
            found_categories[category_name] = url
            print(f"✅ {category_name} encontrada: {url}")
        else:
            print(f"❌ {category_name} no encontrada")

    if not found_categories:
        raise Exception("No se encontraron las categorías objetivo")

    # 5. Procesar cada categoría encontrada
    all_products = []

    for category_name, category_url in found_categories.items():
        print("\n" + "="*60)
        print(f"🎯 PROCESANDO: {category_name}")
        print("="*60)
        
        category_products = process_category_with_filters(driver, category_name, category_url)
        all_products.extend(category_products)
        
        print(f"✅ {category_name}: {len(category_products)} productos scrapeados")

    # 6. Guardar todos los productos en CSV
    fecha_actual = datetime.today().strftime('%Y-%m-%d')
    filename = f"jumbo_carnes_rotiseria_{fecha_actual}.csv"
    save_to_csv(all_products, filename)

    print(f"\n🎉 Scraping completado!")
    print(f"📊 Total de productos: {len(all_products)}")
    print(f"📁 Archivo guardado: {filename}")
    
    # Mostrar resumen por categoría
    print("\n📋 Resumen por categoría:")
    for category_name in found_categories.keys():
        count = len([p for p in all_products if p.get('categoria') == category_name])
        print(f"  • {category_name}: {count} productos")
    
    # Mostrar resumen por tipo de producto
    print("\n📋 Resumen por tipo de producto:")
    tipos = {}
    for product in all_products:
        tipo = product.get('tipo_de_producto', 'Sin tipo')
        tipos[tipo] = tipos.get(tipo, 0) + 1
    
    for tipo, count in sorted(tipos.items()):
        print(f"  • {tipo}: {count} productos")
    
    print("\n🔚 Presiona Enter para cerrar el navegador...")
    input()

except Exception as e:
    print(f"❌ Error general: {e}")
    print("🔚 Presiona Enter para cerrar el navegador...")
    input()

finally:
    driver.quit()
    print("🔚 Navegador cerrado")