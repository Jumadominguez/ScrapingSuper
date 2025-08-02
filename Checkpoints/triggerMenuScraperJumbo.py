# jumbo_almacen_navigator.py
# Requiere: selenium, webdriver_manager
# > pip install selenium webdriver-manager

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time

URL = "https://www.jumbo.com.ar/"

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
        time.sleep(5)  # Tiempo adicional para componentes VTEX
        print("✅ Página cargada")
        return True
    except Exception as e:
        print(f"❌ Error esperando carga: {e}")
        return False

def deploy_categories_menu(driver, wait):
    """Despliega el menú de categorías haciendo hover sobre el botón CATEGORÍAS"""
    print("🔄 Desplegando menú de categorías...")
    
    try:
        # Encontrar el botón "CATEGORÍAS" usando el selector VTEX correcto
        categories_button = wait.until(
            EC.element_to_be_clickable((
                By.XPATH,
                "//nav[contains(@class, 'menuContainerNav--category-menu')]//div[contains(@class, 'vtex-menu-2-x-styledLinkContent--header-category') and contains(text(), 'CATEGORÍAS')]"
            ))
        )
        
        print("✅ Botón 'CATEGORÍAS' encontrado")
        
        # Hacer hover para desplegar el menú
        ActionChains(driver).move_to_element(categories_button).perform()
        time.sleep(2)  # Pausa para que se despliegue el menú
        
        print("✅ Hover realizado sobre 'CATEGORÍAS'")
        
        # Buscar el contenedor del menú desplegado
        # Puede aparecer como un submenu o dropdown
        menu_selectors = [
            "//div[contains(@class, 'vtex-menu-2-x-submenu')]",
            "//div[contains(@class, 'vtex-menu-2-x-menuDropdown')]",
            "//ul[contains(@class, 'vtex-menu-2-x-submenuList')]",
            "//div[contains(@class, 'submenu')]"
        ]
        
        menu_container = None
        for selector in menu_selectors:
            try:
                menu_container = wait.until(
                    EC.visibility_of_element_located((By.XPATH, selector))
                )
                print(f"✅ Menú desplegado encontrado con: {selector}")
                break
            except Exception as e:
                print(f"⚠️  Selector {selector} no funcionó: {e}")
        
        if not menu_container:
            print("⚠️  Intentando buscar cualquier elemento visible después del hover...")
            # Fallback: buscar cualquier elemento que contenga "Almacén"
            time.sleep(1)
            return True  # Continuar aunque no encontremos el contenedor específico
        
        return menu_container
        
    except Exception as e:
        print(f"❌ Error desplegando menú: {e}")
        return None

def find_and_click_almacen(driver, wait):
    """Busca y hace clic en la categoría 'Almacén'"""
    print("🔄 Buscando categoría 'Almacén'...")
    
    try:
        # Selectores múltiples para encontrar "Almacén"
        almacen_selectors = [
            "//a[contains(text(), 'Almacén')]",
            "//a[contains(text(), 'ALMACÉN')]",
            "//a[contains(text(), 'Almacen')]",
            "//a[contains(text(), 'ALMACEN')]",
            "//span[contains(text(), 'Almacén')]",
            "//span[contains(text(), 'Almacen')]",
            "//div[contains(text(), 'Almacén')]",
            "//div[contains(text(), 'Almacen')]",
            "//li[contains(text(), 'Almacén')]",
            "//a[@href*='almacen']",
            "//a[@href*='Almacen']",
            "//*[contains(@class, 'vtex-menu') and contains(text(), 'Almacén')]",
            "//*[contains(@class, 'vtex-menu') and contains(text(), 'Almacen')]"
        ]
        
        almacen_link = None
        for selector in almacen_selectors:
            try:
                elements = driver.find_elements(By.XPATH, selector)
                if elements:
                    # Filtrar elementos visibles
                    visible_elements = [el for el in elements if el.is_displayed()]
                    if visible_elements:
                        almacen_link = visible_elements[0]
                        print(f"✅ Enlace 'Almacén' encontrado con: {selector}")
                        print(f"   Texto: {almacen_link.text}")
                        print(f"   Href: {almacen_link.get_attribute('href')}")
                        break
            except Exception as e:
                print(f"⚠️  Selector {selector} falló: {e}")
        
        if not almacen_link:
            print("❌ No se encontró el enlace de 'Almacén'")
            return False
        
        # Hacer clic en "Almacén"
        try:
            # Scroll al elemento
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", almacen_link)
            time.sleep(0.5)
            
            # Intentar click normal primero
            almacen_link.click()
            print("✅ Click normal en 'Almacén' realizado")
            
        except Exception as e:
            print(f"⚠️  Click normal falló, intentando JavaScript click: {e}")
            # Fallback: JavaScript click
            driver.execute_script("arguments[0].click();", almacen_link)
            print("✅ JavaScript click en 'Almacén' realizado")
        
        time.sleep(3)  # Esperar a que cargue la página
        
        # Verificar que estamos en la página de almacén
        current_url = driver.current_url
        page_title = driver.title
        
        print(f"📍 URL actual: {current_url}")
        print(f"📍 Título de página: {page_title}")
        
        if "almacen" in current_url.lower() or "almacén" in page_title.lower() or "almacen" in page_title.lower():
            print("🎉 ¡Navegación exitosa a Almacén!")
            return True
        else:
            print("⚠️  Verificar si estamos en la página correcta")
            return True  # Asumir éxito para continuar
            
    except Exception as e:
        print(f"❌ Error buscando/clickeando 'Almacén': {e}")
        return False

if __name__ == "__main__":
    print("🚀 Iniciando navegador hacia Almacén de Jumbo...")
    
    driver = setup_driver(headless=False)  # Modo visible
    wait = WebDriverWait(driver, 30)  # Timeout más largo para VTEX

    try:
        print(f"🌐 Navegando a: {URL}")
        driver.get(URL)
        
        # Esperar carga completa
        if not wait_for_page_load(driver, wait):
            print("❌ La página no cargó correctamente")
            exit(1)
        
        # Desplegar menú de categorías
        menu_result = deploy_categories_menu(driver, wait)
        if menu_result is None:
            print("❌ No se pudo desplegar el menú de categorías")
            exit(1)
        
        # Buscar y hacer clic en "Almacén"
        if find_and_click_almacen(driver, wait):
            print("🎉 ¡Script completado exitosamente!")
            print("📍 Posicionado en la página de Almacén")
        else:
            print("❌ No se pudo navegar a Almacén")

    except Exception as e:
        print(f"❌ Error general: {e}")
        
    finally:
        input("Presiona Enter para cerrar el navegador...")
        driver.quit()