const puppeteer = require('puppeteer');

module.exports = async function scrapCarrefourDebug(producto, config) {
  const url = config.urlBaseBusqueda + encodeURIComponent(producto);
  console.log(`🔗 Navegando a: ${url}`);

  const browser = await puppeteer.launch({
    headless: false,
    slowMo: 100,
    defaultViewport: null
  });

  const page = await browser.newPage();

  try {
    console.log(`🌐 Cargando página...`);
    await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });

    console.log(`🔍 Esperando selector: ${config.claseProducto}`);
    await page.waitForSelector(config.claseProducto, { timeout: 30000 });

    const resultados = await page.evaluate(cfg => {
      const productos = [];
      document.querySelectorAll(cfg.claseProducto).forEach(item => {
        const nombre = item.querySelector(cfg.claseNombre)?.innerText?.trim();
        const precio = item.querySelector(cfg.clasePrecio)?.innerText?.trim();
        if (nombre && precio) {
          productos.push({ nombre, precio });
        }
      });
      return productos;
    }, config);

    console.log(`✅ Productos extraídos: ${resultados.length}`);
    await browser.close();
    return resultados;

  } catch (error) {
    console.error(`❌ Error durante scraping: ${error.message}`);
    await page.screenshot({ path: `error_${producto.replace(/\s+/g, '_')}.png` });
    await browser.close();
    return [];
  }
};