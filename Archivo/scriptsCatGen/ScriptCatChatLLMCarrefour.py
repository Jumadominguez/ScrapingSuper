import os
import time
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from datetime import datetime

class CarrefourCategoryScraper:
    def __init__(self):
        self.driver = None
        self.screenshots_dir = "carrefour_screenshots"
        self.csv_output = "carrefour_categorias_automatico.csv"
        self.setup_directories()
        
    def setup_directories(self):
        if not os.path.exists(self.screenshots_dir):
            os.makedirs(self.screenshots_dir)
            print(f"✓ Directorio creado: {self.screenshots_dir}")

    def setup_driver(self):
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        # chrome_options.add_argument("--headless")  # Descomenta para headless
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            print("✓ Driver de Chrome iniciado correctamente")
            return True
        except Exception as e:
            print(f"❌ Error al iniciar Chrome: {e}")
            return False

    def navigate_to_carrefour(self):
        try:
            print("🌐 Navegando a Carrefour...")
            self.driver.get("https://www.carrefour.com.ar/")
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            time.sleep(3)
            self.close_popups()
            print("✓ Página de Carrefour cargada")
            return True
        except Exception as e:
            print(f"❌ Error al navegar a Carrefour: {e}")
            return False

    def close_popups(self):
        try:
            popup_selectors = [
                "[data-testid='cookie-banner-close']",
                ".cookie-close",
                ".modal-close",
                ".popup-close",
                "[aria-label='Close']",
                "[aria-label='Cerrar']",
                ".close-button",
                "button[class*='close']",
                ".modal .close",
                ".popup .close"
            ]
            for selector in popup_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed():
                            element.click()
                            time.sleep(1)
                            print(f"✓ Popup cerrado: {selector}")
                except:
                    continue
        except Exception as e:
            print(f"⚠️ No se pudieron cerrar algunos popups: {e}")

        def open_categories_menu(self):
            """Abre el menú de categorías solo si no está abierto"""
            try:
                print("📂 Verificando si el menú de categorías ya está abierto...")
                # Selector del menú abierto
                menu_open_selector = ".vtex-menu-2-x-menuDrawerContent"
                menu_already_open = False
                try:
                    menu_open = self.driver.find_element(By.CSS_SELECTOR, menu_open_selector)
                    if menu_open.is_displayed():
                        menu_already_open = True
                except:
                    pass  # Si no lo encuentra, seguimos

                if menu_already_open:
                    print("✓ El menú de categorías ya está abierto")
                    return True

                print("📂 Abriendo menú de categorías...")
                menu_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button.vtex-menu-2-x-styledLink--menu-categorias"))
                )
                print("✓ Botón 'Categorías' encontrado")
                menu_button.click()
                time.sleep(2)
                print("✓ Menú de categorías abierto")
                return True
            except Exception as e:
                print(f"❌ Error al abrir el menú: {e}")
                return False

    def get_main_categories(self):
        try:
            print("🔍 Buscando categorías principales...")
            category_selectors = [
                ".vtex-menu-2-x-styledLink.vtex-menu-2-x-styledLink--category",
                ".vtex-menu-2-x-styledLink--category",
                ".vtex-menu-2-x-styledLink",
                ".menu-categories > li",
                ".categories-list > li"
            ]
            categories = []
            for selector in category_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    visible_elements = [el for el in elements if el.is_displayed()]
                    if visible_elements and len(visible_elements) > 3:
                        categories = visible_elements
                        break
                except:
                    continue
            if not categories:
                print("❌ No se encontraron categorías")
                return []
            print(f"✓ Encontradas {len(categories)} categorías principales")
            return categories
        except Exception as e:
            print(f"❌ Error al obtener categorías: {e}")
            return []

    def take_category_screenshots(self, categories):
        screenshots_taken = []
        print(f"📸 Iniciando captura de {len(categories)} categorías...")
        for i, category in enumerate(categories):
            try:
                category_name = self.get_category_name(category)
                print(f"📸 Screenshot {i+1}/{len(categories)}: {category_name}")
                self.driver.execute_script("arguments[0].scrollIntoView(true);", category)
                time.sleep(1)
                actions = ActionChains(self.driver)
                actions.move_to_element(category).perform()
                time.sleep(2)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                safe_name = self.sanitize_filename(category_name)
                filename = f"categoria_{i+1:02d}_{safe_name}_{timestamp}.png"
                filepath = os.path.join(self.screenshots_dir, filename)
                self.driver.save_screenshot(filepath)
                screenshots_taken.append({
                    'filename': filename,
                    'filepath': filepath,
                    'category_name': category_name,
                    'index': i+1
                })
                print(f"✓ Screenshot guardado: {filename}")
                time.sleep(1)
            except Exception as e:
                print(f"❌ Error al tomar screenshot de categoría {i+1}: {e}")
                continue
        print(f"✅ Capturas completadas: {len(screenshots_taken)} screenshots guardados")
        return screenshots_taken

    def get_category_name(self, category_element):
        try:
            text_selectors = ["a", "span", ".category-name", ".menu-text", "button"]
            for selector in text_selectors:
                try:
                    text_element = category_element.find_element(By.CSS_SELECTOR, selector)
                    text = text_element.text.strip()
                    if text and len(text) > 1:
                        return text
                except:
                    continue
            text = category_element.text.strip()
            if text and len(text) > 1:
                return text
            for attr in ['aria-label', 'title', 'data-category']:
                try:
                    attr_text = category_element.get_attribute(attr)
                    if attr_text and len(attr_text.strip()) > 1:
                        return attr_text.strip()
                except:
                    continue
            return f"Categoria_{datetime.now().strftime('%H%M%S')}"
        except:
            return f"Categoria_{datetime.now().strftime('%H%M%S')}"

    def sanitize_filename(self, filename):
        import re
        filename = re.sub(r'[<>:\"/\\\\|?*¿¡]', '', filename)
        filename = filename.replace(' ', '_')
        filename = filename.replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')
        filename = filename.replace('ñ', 'n')
        return filename[:50]

    def generate_example_csv_data(self, screenshots_data):
        csv_data = [["Supermercado", "Categoria", "Subcategoria", "Subseccion"]]
        for screenshot in screenshots_data:
            category_name = screenshot['category_name']
            csv_data.extend([
                ["Carrefour", category_name, f"Subcategoria 1 de {category_name}", f"Subseccion A"],
                ["Carrefour", category_name, f"Subcategoria 1 de {category_name}", f"Subseccion B"],
                ["Carrefour", category_name, f"Subcategoria 2 de {category_name}", f"Subseccion C"],
            ])
        return csv_data

    def save_csv(self, csv_data):
        try:
            with open(self.csv_output, 'w', encoding='utf-8-sig', newline='') as f:
                writer = csv.writer(f)
                writer.writerows(csv_data)
            print(f"✓ CSV guardado: {self.csv_output}")
            print(f"📊 Total de filas: {len(csv_data)}")
            return True
        except Exception as e:
            print(f"❌ Error al guardar CSV: {e}")
            return False

    def run(self):
        print("🚀 Iniciando extracción automatizada de categorías de Carrefour")
        print("=" * 60)
        try:
            if not self.setup_driver():
                return False
            if not self.navigate_to_carrefour():
                return False
            if not self.open_categories_menu():
                return False
            categories = self.get_main_categories()
            if not categories:
                return False
            screenshots_data = self.take_category_screenshots(categories)
            if not screenshots_data:
                print("❌ No se pudieron tomar screenshots")
                return False
            print("📊 Generando CSV con datos de ejemplo...")
            csv_data = self.generate_example_csv_data(screenshots_data)
            self.save_csv(csv_data)
            print("=" * 60)
            print("✅ Proceso completado exitosamente!")
            print(f"📸 Screenshots guardados en: {self.screenshots_dir}")
            print(f"📊 CSV generado: {self.csv_output}")
            print("\n📋 Próximos pasos:")
            print("1. Revisa los screenshots generados")
            print("2. Sube las imágenes al asistente IA para análisis detallado")
            print("3. El asistente generará un CSV completo con todas las subcategorías")
            return True
        except Exception as e:
            print(f"❌ Error general: {e}")
            return False
        finally:
            if self.driver:
                self.driver.quit()
                print("🔒 Driver cerrado")

def main():
    print("🛒 EXTRACTOR AUTOMÁTICO DE CATEGORÍAS - CARREFOUR")
    print("=" * 60)
    scraper = CarrefourCategoryScraper()
    success = scraper.run()
    if success:
        print("\n🎉 ¡Proceso completado! Revisa los archivos generados.")
        print("\n💡 Para obtener un CSV completo y detallado:")
        print("   1. Sube los screenshots al asistente IA")
        print("   2. Pide que analice las imágenes y genere el CSV completo")
    else:
        print("\n❌ El proceso falló. Revisa los errores anteriores.")

if __name__ == "__main__":
    main()