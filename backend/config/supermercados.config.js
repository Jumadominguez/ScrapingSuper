module.exports = {
  supermercados: {
    jumbo: {
      nombre: "Jumbo",
      dominio: "jumbo.com.ar",
      urlBaseBusqueda: "https://www.jumbo.com.ar/search/?text=",
      catalogoAccesible: true,
      proteccionBot: "moderada",
      requiereLogin: false,
      metodoScraping: "html",
      claseProducto: ".product-item",
      claseNombre: ".product-name",
      clasePrecio: ".price"
    },
    coto: {
      nombre: "Coto",
      dominio: "coto.com.ar",
      urlBaseBusqueda: "https://www.coto.com.ar/buscador?q=",
      catalogoAccesible: false,
      requiereLogin: true,
      proteccionBot: "alta",
      metodoScraping: "inaccesible",
      claseProducto: null,
      claseNombre: null,
      clasePrecio: null
    },
    carrefour: {
      nombre: "Carrefour",
      dominio: "carrefour.com.ar",
      urlBaseBusqueda: "https://www.carrefour.com.ar/buscar?q=",
      catalogoAccesible: true,
      proteccionBot: "baja",
      requiereLogin: false,
      metodoScraping: "html",
      claseProducto: ".product-item",
      claseNombre: ".product-name",
      clasePrecio: ".price"
    },
    disco: {
      nombre: "Disco",
      dominio: "disco.virtual.com.ar",
      urlBaseBusqueda: "https://www.disco.com.ar/search/?text=",
      catalogoAccesible: true,
      proteccionBot: "moderada",
      requiereLogin: false,
      metodoScraping: "html",
      claseProducto: ".product-item",
      claseNombre: ".product-name",
      clasePrecio: ".price"
    },
    vea: {
      nombre: "Vea",
      dominio: "vea.virtual.com.ar",
      urlBaseBusqueda: "https://www.vea.com.ar/search/?text=",
      catalogoAccesible: true,
      proteccionBot: "moderada",
      requiereLogin: false,
      metodoScraping: "html",
      claseProducto: ".product-item",
      claseNombre: ".product-name",
      clasePrecio: ".price"
    }
  }
};