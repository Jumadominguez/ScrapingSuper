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

// 🌐 Variables globales
let eleccionesUsuario = {};
window.__DATA_COMPARATIVO = null;
let celdaScrapingsuperTotal = null;
let celdaDistribucionTexto = null;

// 🔁 Actualiza elección de supermercado por producto
function actualizarSeleccion(index, supermercado) {
  eleccionesUsuario[index] = supermercado;
  actualizarTotalesReactivos();
}

// ✅ Recalcula solo las celdas reactivas
function actualizarTotalesReactivos() {
  const dataComparativo = window.__DATA_COMPARATIVO;
  if (!dataComparativo || !celdaScrapingsuperTotal || !celdaDistribucionTexto) return;

  let total = 0;
  const conteo = {};
  const supermercados = Object.keys(dataComparativo[0].precios);
  supermercados.forEach(s => conteo[s] = 0);

  dataComparativo.forEach((item, index) => {
    const elegido = eleccionesUsuario[index];
    if (elegido) {
      const valor = parseFloat(item.precios[elegido].replace('$', ''));
      if (!isNaN(valor)) {
        total += valor;
        conteo[elegido]++;
      }
    }
  });

  celdaScrapingsuperTotal.textContent = `$${total.toFixed(2)}`;

  const resumenTexto = Object.entries(conteo)
    .map(([supermercado, cantidad]) => {
      const nombre = supermercado.charAt(0).toUpperCase() + supermercado.slice(1);
      const plural = cantidad === 1 ? 'producto' : 'productos';
      return `${cantidad} ${plural} de ${nombre}`;
    }).join('\n');

  celdaDistribucionTexto.innerHTML = resumenTexto.replace(/\n/g, '<br>');
}

// 🧠 Genera tabla principal con menús por producto
window.mostrarResultados = function(dataComparativo) {
  window.__DATA_COMPARATIVO = dataComparativo;

  const tabla = document.createElement('table');
  tabla.className = 'table table-sm table-bordered table-hover align-middle';

  const supermercados = Object.keys(dataComparativo[0].precios);

  const thead = document.createElement('thead');
  const encabezado = document.createElement('tr');
  encabezado.innerHTML = `<th>Producto</th>`;
  supermercados.forEach(supermercado => {
    encabezado.innerHTML += `<th>${supermercado.toUpperCase()}</th>`;
  });
  encabezado.innerHTML += `<th>Supermercado Seleccionado</th>`;
  encabezado.innerHTML += `<th>Scrapingsuper</th>`;
  thead.appendChild(encabezado);
  tabla.appendChild(thead);

  const tbody = document.createElement('tbody');

  dataComparativo.forEach((item, index) => {
    const fila = document.createElement('tr');
    fila.innerHTML = `<td>${item.producto}</td>`;

    // Procesar precios y encontrar el menor
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

    // Celdas por supermercado
    preciosProcesados.forEach(({ supermercado, precio }) => {
      const destacado = supermercado === supermercadoGanador;
      const clase = destacado ? 'table-success fw-bold text-center' : 'text-center';
      fila.innerHTML += `<td class="${clase}">${precio}</td>`;
    });

    // Menú desplegable
    const select = document.createElement('select');
    select.className = 'form-select form-select-sm text-center';
    select.onchange = () => actualizarSeleccion(index, select.value);

    preciosProcesados.forEach(({ supermercado }) => {
      const option = document.createElement('option');
      option.value = supermercado;
      option.text = supermercado.charAt(0).toUpperCase() + supermercado.slice(1);
      select.appendChild(option);
    });

    select.value = supermercadoGanador;
    eleccionesUsuario[index] = supermercadoGanador;

    const tdSelect = document.createElement('td');
    tdSelect.className = 'text-center';
    tdSelect.appendChild(select);
    fila.appendChild(tdSelect);

    // Precio mínimo visual
    const tdMinimo = document.createElement('td');
    tdMinimo.className = 'table-success fw-bold text-center';
    tdMinimo.textContent = `$${menorPrecio.toFixed(2)}`;
    fila.appendChild(tdMinimo);

    tbody.appendChild(fila);
  });

  tabla.appendChild(tbody);

  document.getElementById('resultados').innerHTML = '';
  const contenedor = document.createElement('div');
  contenedor.className = 'px-3';
  contenedor.appendChild(tabla);
  document.getElementById('resultados').appendChild(contenedor);

  crearTablaTotales(dataComparativo, supermercados);
};

// 📊 Crea la tabla de Totales UNA sola vez
function crearTablaTotales(dataComparativo, supermercados) {
  const tabla = document.createElement('table');
  tabla.className = 'table table-sm table-bordered table-hover align-middle mt-4';

  const thead = document.createElement('thead');
  const encabezado = document.createElement('tr');
  encabezado.innerHTML = `<th>Total por columna</th>`;
  supermercados.forEach(s => {
    encabezado.innerHTML += `<th>${s.toUpperCase()}</th>`;
  });
  encabezado.innerHTML += `<th>Scrapingsuper</th>`;
  thead.appendChild(encabezado);
  tabla.appendChild(thead);

  const totales = {};
  supermercados.forEach(s => totales[s] = 0);

  dataComparativo.forEach(item => {
    Object.entries(item.precios).forEach(([supermercado, precio]) => {
      const valor = parseFloat(precio.replace('$', ''));
      if (!isNaN(valor)) totales[supermercado] += valor;
    });
  });

  const tbody = document.createElement('tbody');

  const filaTotales = document.createElement('tr');
  filaTotales.innerHTML = `<td class="fw-bold text-end">Suma total</td>`;
  supermercados.forEach(supermercado => {
    filaTotales.innerHTML += `<td class="fw-bold text-success text-center">$${totales[supermercado].toFixed(2)}</td>`;
  });

  celdaScrapingsuperTotal = document.createElement('td');
  celdaScrapingsuperTotal.className = 'fw-bold text-success text-center';
  filaTotales.appendChild(celdaScrapingsuperTotal);
  tbody.appendChild(filaTotales);

  // 🛒 Botones
  const filaComprar = document.createElement('tr');
  filaComprar.innerHTML = `<td class="fw-bold text-end">Acción</td>`;
  supermercados.forEach(supermercado => {
    filaComprar.innerHTML += `<td class="text-center"><button class="btn btn-sm btn-outline-primary">Comprar</button></td>`;
  });
  filaComprar.innerHTML += `<td class="text-center"><button class="btn btn-sm btn-success">Comprar</button></td>`;
  tbody.appendChild(filaComprar);

  // 🧮 Distribución de compra
  const filaDistribucion = document.createElement('tr');
  filaDistribucion.innerHTML = `<td class="fw-bold text-end">Vas a comprar</td>`;
  supermercados.forEach(() => {
    filaDistribucion.innerHTML += `<td></td>`;
  });

  celdaDistribucionTexto = document.createElement('td');
  celdaDistribucionTexto.className = 'text-center text-muted';
  filaDistribucion.appendChild(celdaDistribucionTexto);
  tbody.appendChild(filaDistribucion);

  tabla.appendChild(tbody);
  document.getElementById('resultados').appendChild(tabla);

  actualizarTotalesReactivos();
}
