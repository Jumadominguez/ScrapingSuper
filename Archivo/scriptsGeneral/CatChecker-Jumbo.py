import csv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def setup_chrome_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    driver = webdriver.Chrome(options=chrome_options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver

def open_menu(driver):
    # Espera y hace click en el botón de menú "CATEGORÍAS"
    menu_btn = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.XPATH, '//div[contains(@class, "vtex-menu-2-x-styledLinkContent--header-category") and contains(text(), "CATEGORÍAS")]'))
    )
    menu_btn.click()
    time.sleep(2)

def extract_categories_and_subcategories(driver):
    data = []
    actions = ActionChains(driver)
    # Espera a que aparezcan las categorías principales
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.vtex-menu-2-x-menuContainer'))
    )
    categories = driver.find_elements(By.CSS_SELECTOR, 'div.vtex-menu-2-x-menuContainer > div > div > div > a')
    print(f"Encontradas {len(categories)} categorías principales")
    for i, cat in enumerate(categories, 1):
        try:
            cat_name = cat.text.strip()
            print(f"{i:2d}. {cat_name}")
            # Hover para mostrar subcategorías (si existen)
            actions.move_to_element(cat).perform()
            time.sleep(1)
            # Buscar subcategorías (si existen)
            subcat_selector = 'div.vtex-menu-2-x-submenu > div > a'
            subcats = cat.find_elements(By.XPATH, '../../following-sibling::div//a')
            if subcats:
                for sub in subcats:
                    subcat_name = sub.text.strip()
                    if subcat_name:
                        data.append({'Categoria': cat_name, 'Subcategoria': subcat_name})
            else:
                data.append({'Categoria': cat_name, 'Subcategoria': ''})
            actions.move_by_offset(10, 10).perform()
        except Exception as e:
            print(f"    ❌ Error con {cat_name}: {str(e)}")
            continue
    return data

def save_to_csv(data, filename="jumbo_categorias.csv"):
    if not data:
        print("❌ No hay datos para guardar")
        return False
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Categoria', 'Subcategoria']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)
    print(f"✅ Archivo guardado: {filename}")
    print(f"📊 Registros guardados: {len(data)}")
    return True

def main():
    print("🎯 SCRAPER DE CATEGORÍAS DE JUMBO")
    driver = setup_chrome_driver()
    try:
        driver.get("https://www.jumbo.com.ar/")
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        time.sleep(3)
        open_menu(driver)
        data = extract_categories_and_subcategories(driver)
        save_to_csv(data)
        print("🎉 ¡Scraping completado!")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()