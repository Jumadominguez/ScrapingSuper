import asyncio
from playwright.async_api import async_playwright
import os

async def main():
    url = "https://www.cotodigital.com.ar/sitios/cdigi/"
    screenshots_dir = "coto_categorias_screenshots"
    os.makedirs(screenshots_dir, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto(url)
        await page.wait_for_selector("li.categoria-producto")
        categorias = await page.query_selector_all("li.categoria-producto")

        print(f"Encontradas {len(categorias)} categorías.")

        for idx, cat in enumerate(categorias):
            nombre = await cat.inner_text()
            nombre = nombre.strip().replace(" ", "_").replace("/", "-")
            print(f"Haciendo hover en: {nombre}")

            await cat.hover()
            await page.wait_for_timeout(1200)  # Espera a que se despliegue el menú

            # Ajustá este selector al del menú desplegado real
            submenu = await cat.query_selector(".submenu-categoria")
            if submenu:
                screenshot_path = os.path.join(screenshots_dir, f"{idx+1:02d}_{nombre}.png")
                await submenu.screenshot(path=screenshot_path)
                print(f"Screenshot guardado: {screenshot_path}")
            else:
                print(f"No se encontró el menú desplegado para: {nombre}")

        await browser.close()

asyncio.run(main())