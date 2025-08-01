const config = require('../config/supermercados.config').supermercados;
const jumbo = require('../scrapers/jumbo');
const carrefour = require('../scrapers/carrefour');
// Agregá los otros scrapers cuando estén listos

// Mapeo dinámico supermercado → módulo
const scraperMap = {
  jumbo,
  carrefour,
  disco: require('../scrapers/disco'),
  vea: require('../scrapers/vea')
  // coto quedaría fuera por ahora
};

async function scrapPorProducto(req, res) {
  const { producto, supermercado } = req.query;

  if (!producto || !supermercado) {
    return res.status(400).json({ error: 'Faltan parámetros: producto y supermercado son obligatorios.' });
  }

  const configSuper = config[supermercado];
  const scraperFunc = scraperMap[supermercado];

  if (!configSuper || !scraperFunc) {
    return res.status(404).json({ error: 'Supermercado no disponible para scraping.' });
  }

  try {
    const resultados = await scraperFunc(producto, configSuper);
    return res.json({ supermercado, producto, resultados });
  } catch (error) {
    console.error(`❌ Error al scrapear ${supermercado}:`, error.message);
    return res.status(500).json({ error: 'Falló el scraping para este supermercado.' });
  }
}

module.exports = { scrapPorProducto };