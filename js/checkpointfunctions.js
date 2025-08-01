console.log("✅ functions.js cargado correctamente"); 

// 🟩 Agrega un producto a la lista
window.agregarProducto = function() {
  const producto = document.getElementById('producto').value.trim();
  const marca = document.getElementById('marca').value.trim();
  const presentacion = document.getElementById('presentacion').value.trim();

  if (producto && marca && presentacion) {
    const texto = `${producto} ${marca} ${presentacion}`;

    const item = document.createElement('li');
    item.className = 'list-group-item d-flex justify-content-between align-items-center';
    item.textContent = texto;

    const btn = document.createElement('button');
    btn.className = 'btn btn-sm btn-outline-danger';
    btn.textContent = '🗑️ Eliminar';
    btn.onclick = () => item.remove();

    item.appendChild(btn);
    document.getElementById('lista-productos').appendChild(item);

    document.getElementById('producto').value = '';
    document.getElementById('marca').value = '';
    document.getElementById('presentacion').value = '';
  } else {
    alert('Completá todos los campos antes de agregar.');
  }
};

// 🟦 Compara productos y simula precios
window.compararProductos = function() {
  const items = document.querySelectorAll('#lista-productos li');
  const productos = [];
  items.forEach(item => {
    const texto = item.textContent.replace('🗑️ Eliminar', '').trim();
    productos.push(texto);
  });

  const supermercados = [];
  ['jumbo', 'coto', 'carrefour', 'disco', 'vea'].forEach(id => {
    if (document.getElementById(id).checked) {
      supermercados.push(id);
    }
  });

  const consulta = { supermercados, productos };
  console.log("Consulta generada:", consulta);

  // 🧪 Simulación con 15 productos
  const simulacion = [
    { producto: "Arroz Molinos Ala 1kg", precios: { jumbo: "$810", coto: "$799", carrefour: "$820", disco: "$815", vea: "$805" } },
    { producto: "Aceite Cocinero 900ml", precios: { jumbo: "$990", coto: "$970", carrefour: "$985", disco: "$980", vea: "$975" } },
    { producto: "Azúcar Ledezma 1kg", precios: { jumbo: "$100", coto: "$150", carrefour: "$75", disco: "$129", vea: "$135" } },
    { producto: "Jamon La Paulina 100g", precios: { jumbo: "$300", coto: "$270", carrefour: "$385", disco: "$180", vea: "$275" } },
    { producto: "Queso Sancor 1kg", precios: { jumbo: "$450", coto: "$200", carrefour: "$385", disco: "$420", vea: "$435" } },
    { producto: "Yerba Taragüí 1kg", precios: { jumbo: "$820", coto: "$790", carrefour: "$805", disco: "$815", vea: "$800" } },
    { producto: "Leche La Serenísima 1L", precios: { jumbo: "$310", coto: "$295", carrefour: "$300", disco: "$305", vea: "$290" } },
    { producto: "Galletitas Pepitos 180g", precios: { jumbo: "$280", coto: "$265", carrefour: "$275", disco: "$270", vea: "$260" } },
    { producto: "Café La Virginia 500g", precios: { jumbo: "$950", coto: "$910", carrefour: "$920", disco: "$925", vea: "$905" } },
    { producto: "Pan Lactal Bimbo 550g", precios: { jumbo: "$620", coto: "$590", carrefour: "$605", disco: "$610", vea: "$585" } },
    { producto: "Coca-Cola 2.25L", precios: { jumbo: "$780", coto: "$750", carrefour: "$765", disco: "$770", vea: "$745" } },
    { producto: "Harina Pureza 1kg", precios: { jumbo: "$165", coto: "$150", carrefour: "$155", disco: "$160", vea: "$145" } },
    { producto: "Lavandina Ayudín 1L", precios: { jumbo: "$110", coto: "$105", carrefour: "$108", disco: "$107", vea: "$102" } },
    { producto: "Detergente Magistral 750ml", precios: { jumbo: "$330", coto: "$310", carrefour: "$320", disco: "$325", vea: "$315" } },
    { producto: "Papel Higiénico Higienol x4", precios: { jumbo: "$490", coto: "$470", carrefour: "$480", disco: "$485", vea: "$465" } }
  ];

  window.mostrarResultados(simulacion);
};

// 🟥 Muestra tabla comparativa en pantalla
window.mostrarResultados = function(dataComparativo) {
  const tabla = document.createElement('table');
  tabla.className = 'table table-sm table-bordered table-hover align-middle';

  // Encabezado
  const thead = document.createElement('thead');
  const encabezado = document.createElement('tr');
  encabezado.innerHTML = `<th>Producto</th>`;
  const supermercados = Object.keys(dataComparativo[0].precios);
  supermercados.forEach(supermercado => {
    encabezado.innerHTML += `<th>${supermercado.toUpperCase()}</th>`;
  });
  encabezado.innerHTML += `<th class="col-mejor">Mejor precio</th>`;
  encabezado.innerHTML += `<th class="col-scrapingsuper">Scrapingsuper</th>`;
  thead.appendChild(encabezado);
  tabla.appendChild(thead);

  // Cuerpo
  const tbody = document.createElement('tbody');
  dataComparativo.forEach(item => {
    const fila = document.createElement('tr');
    fila.innerHTML = `<td>${item.producto}</td>`;

    let menorPrecio = null;
    let supermercadoGanador = '';
    const preciosProcesados = [];

    Object.entries(item.precios).forEach(([supermercado, precio]) => {
      const valor = parseFloat(precio.replace('$', ''));
      preciosProcesados.push({ supermercado, precio, valor });
      if (!isNaN(valor) && (menorPrecio === null || valor < menorPrecio)) {
        menorPrecio = valor;
        supermercadoGanador = supermercado;
      }
    });

    preciosProcesados.forEach(({ supermercado, precio }) => {
      const cellClass = supermercado === supermercadoGanador ? 'table-success fw-bold text-center' : 'text-center';
      fila.innerHTML += `<td class="${cellClass}">${precio}</td>`;
    });

    fila.innerHTML += `<td class="table-success fw-bold text-center">${supermercadoGanador.toUpperCase()}</td>`;
    fila.innerHTML += `<td class="table-success fw-bold text-center">$${menorPrecio.toFixed(2)}</td>`;
    tbody.appendChild(fila);
  });

  tabla.appendChild(tbody);

  // Insertar tabla principal en el contenedor
  document.getElementById('resultados').innerHTML = '';
  const contenedor = document.createElement('div');
  contenedor.className = 'px-3';
  contenedor.appendChild(tabla);
  document.getElementById('resultados').appendChild(contenedor);

  // Tabla resumen de totales
  const resumen = document.createElement('table');
  resumen.className = 'table table-sm table-bordered table-hover align-middle mt-5';

  const theadResumen = document.createElement('thead');
  const headerResumen = document.createElement('tr');
  headerResumen.innerHTML = `<th>Total</th>`;
  supermercados.forEach(supermercado => {
    headerResumen.innerHTML += `<th>${supermercado.toUpperCase()}</th>`;
  });
  headerResumen.innerHTML += `<th>Scrapingsuper</th>`;
  theadResumen.appendChild(headerResumen);
  resumen.appendChild(theadResumen);

  const totales = {};
  supermercados.forEach(s => totales[s] = 0);
  let totalScraping = 0;

  dataComparativo.forEach(item => {
    let menorPrecio = null;
    Object.entries(item.precios).forEach(([supermercado, precio]) => {
      const valor = parseFloat(precio.replace('$', ''));
      if (!isNaN(valor)) {
        totales[supermercado] += valor;
        if (menorPrecio === null || valor < menorPrecio) {
          menorPrecio = valor;
        }
      }
    });
    if (menorPrecio !== null) {
      totalScraping += menorPrecio;
    }
  });

  const tbodyResumen = document.createElement('tbody');
  const filaTotal = document.createElement('tr');
  filaTotal.innerHTML = `<td class="fw-bold text-end">Suma total</td>`;
  supermercados.forEach(supermercado => {
    filaTotal.innerHTML += `<td class="fw-bold text-success text-center">$${totales[supermercado].toFixed(2)}</td>`;
  });
  filaTotal.innerHTML += `<td class="fw-bold text-success text-center">$${totalScraping.toFixed(2)}</td>`;
  tbodyResumen.appendChild(filaTotal);
  const filaComprar = document.createElement('tr');
  filaComprar.innerHTML = `<td class="fw-bold text-end">Acción</td>`;

  supermercados.forEach(supermercado => {
  filaComprar.innerHTML += `
    <td class="text-center">
      <button class="btn btn-sm btn-outline-primary" onclick="alert('Comprar en ${supermercado.toUpperCase()}')">Comprar</button>
    </td>`;
  });

  // Botón final para Scrapingsuper
  filaComprar.innerHTML += `
  <td class="text-center">
    <button class="btn btn-sm btn-success" onclick="alert('Comprar con precios óptimos')">Comprar</button>
  </td>`;

  tbodyResumen.appendChild(filaComprar);
  // 🧮 Fila de conteo de compras por supermercado
const filaDistribucion = document.createElement('tr');
filaDistribucion.innerHTML = `<td class="fw-bold text-end">Vas a comprar</td>`;

// Cálculo del conteo
const conteoPorSuper = {};
supermercados.forEach(s => conteoPorSuper[s] = 0);

dataComparativo.forEach(item => {
  let menorPrecio = null;
  let supermercadoGanador = '';
  Object.entries(item.precios).forEach(([supermercado, precio]) => {
    const valor = parseFloat(precio.replace('$', ''));
    if (!isNaN(valor) && (menorPrecio === null || valor < menorPrecio)) {
      menorPrecio = valor;
      supermercadoGanador = supermercado;
    }
  });
  if (supermercadoGanador) conteoPorSuper[supermercadoGanador]++;
});

// Celdas vacías
supermercados.forEach(() => {
  filaDistribucion.innerHTML += `<td></td>`;
});

// Celda final con resumen
let textoResumen = Object.entries(conteoPorSuper).map(([supermercado, cantidad]) => {
  const nombre = supermercado.charAt(0).toUpperCase() + supermercado.slice(1);
  const singularPlural = cantidad === 1 ? 'producto' : 'productos';
  return `${cantidad} ${singularPlural} de ${nombre}`;
}).join('<br>');

filaDistribucion.innerHTML += `<td class="text-center text-muted" colspan="2">${textoResumen}</td>`;
tbodyResumen.appendChild(filaDistribucion);
  resumen.appendChild(tbodyResumen);


  // Insertar tabla resumen debajo
  document.getElementById('resultados').appendChild(resumen);
};
