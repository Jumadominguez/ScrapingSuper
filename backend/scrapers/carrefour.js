const puppeteer = require('puppeteer');

module.exports = async function scrapCarrefour(producto, config) {
  const url = config.urlBaseBusqueda + encodeURIComponent(producto);
  const browser = await puppeteer.launch({ headless: true });
  const page = await browser.newPage();
  await page.goto(url, { waitUntil: 'networkidle2' });

  await page.waitForSelector(config.claseProducto);

  const resultados = await page.evaluate(cfg => {
    const productos = [];
    document.querySelectorAll(cfg.claseProducto).forEach(item => {
      const nombre = item.querySelector(cfg.claseNombre)?.innerText?.trim();
      const precio = item.querySelector(cfg.clasePrecio)?.innerText?.trim();
      if (nombre && precio) productos.push({ nombre, precio });
    });
    return productos;
  }, config);

  await browser.close();
  return resultados;
};