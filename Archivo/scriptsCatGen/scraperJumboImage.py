import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

SCREENSHOTS_DIR = "jumbo_categorias"
URL = "https://www.jumbo.com.ar/"

def sanitize_filename(name):
    import re
    name = re.sub(r'[<>:"/\\|?*¿¡]', '', name)
    name = name.replace(' ', '_')
    return name[:50]

def main():
    if not os.path.exists(SCREENSHOTS_DIR):
        os.makedirs(SCREENSHOTS_DIR)

    chrome_options = Options()
    chrome_options.add_argument("--window-size=1920,1080")
    # chrome_options.add_argument("--headless")  # Descomenta si no querés ver el navegador

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(URL)
    wait = WebDriverWait(driver, 20)

    wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    time.sleep(3)

    # Cerrar popups si aparecen
    try:
        close_btns = driver.find_elements(By.CSS_SELECTOR, "[aria-label='Cerrar'], .vtex-modal__close-icon, .close")
        for btn in close_btns:
            if btn.is_displayed():
                btn.click()
                time.sleep(1)
    except:
        pass

    # Encontrar el botón "CATEGORÍAS" y hacer hover
    try:
        categorias_btn = wait.until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'vtex-menu-2-x-styledLinkContent--header-category') and contains(text(), 'CATEGORÍAS')]"))
        )
        actions = ActionChains(driver)
        actions.move_to_element(categorias_btn).perform()
        print("✓ Hover sobre 'CATEGORÍAS'")
        time.sleep(2)
        driver.save_screenshot("debug_menu.png")
        print("✓ Screenshot general guardado tras hover")
    except Exception as e:
        print(f"❌ No se pudo hacer hover en el botón de Categorías: {e}")
        driver.save_screenshot("jumbo_debug.png")
        driver.quit()
        return

    # Intentar buscar las categorías principales (opcional, para ver si aparecen)
    try:
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "ul.vtex-menu-2-x-menuContainer--category-menu")))
        categorias = driver.find_elements(By.CSS_SELECTOR, "ul.vtex-menu-2-x-menuContainer--category-menu > li.vtex-menu-2-x-menuItem--category-menu")
        print(f"✓ Encontradas {len(categorias)} categorías principales")
    except Exception as e:
        print(f"❌ No se encontraron categorías principales: {e}")

    driver.quit()
    print("✅ Proceso finalizado.")

if __name__ == "__main__":
    main()
    