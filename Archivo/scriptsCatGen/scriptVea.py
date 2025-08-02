import asyncio
from playwright.async_api import async_playwright
import os

async def main():
    url = "https://www.vea.com.ar/"
    screenshots_dir = "vea_categorias_screenshots"
    os.makedirs(screenshots_dir, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto(url)
        await page.wait_for_selector('li.vtex-menu-2-x-menuItem--header-category')

        # Hover sobre el botón "Categorías"
        await page.hover('li.vtex-menu-2-x-menuItem--header-category')
        await page.wait_for_timeout(1200)

        # Selecciona todos los divs de las categorías principales
        categorias = await page.query_selector_all('div.vtex-menu-2-x-styledLinkContent--menu-item-secondary')

        print(f"Encontradas {len(categorias)} categorías principales.")

        for idx, cat in enumerate(categorias):
            nombre = await cat.inner_text()
            nombre = nombre.strip().replace(" ", "_").replace("/", "-")
            print(f"Haciendo hover en: {nombre}")

            # Hover sobre la categoría
            await cat.hover()
            await page.wait_for_timeout(1200)  # Espera a que se despliegue el submenú

            # Screenshot de toda la página (puedes ajustar para solo el menú si identificás el selector)
            screenshot_path = os.path.join(screenshots_dir, f"{idx+1:02d}_{nombre}.png")
            await page.screenshot(path=screenshot_path, full_page=True)
            print(f"Screenshot guardado: {screenshot_path}")

        await browser.close()

asyncio.run(main())