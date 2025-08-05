let productosDesdeCSV = [];

// Carga automática del CSV desde path fijo
fetch("/database/productos/jumbo/jumbo_carnes_rotiseria_2025-08-02.csv")
  .then(response => response.text())
  .then(csvText => {
    Papa.parse(csvText, {
      header: true,
      skipEmptyLines: true,
      complete: function (result) {
        productosDesdeCSV = result.data.map(row => ({
          tipo: row["Tipo de Producto"],
          nombre: row["Nombre"]
        }));
        console.log("CSV cargado:", productosDesdeCSV.length, "productos");
      }
    });
  });

function normalizar(texto) {
  return texto.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();
}

function actualizarSelectMarca() {
  const inputProducto = document.getElementById("producto").value.trim();
  const tipoSeleccionado = normalizar(inputProducto);
  const selectMarca = document.getElementById("marca");

  selectMarca.innerHTML = '<option selected disabled>Elegí una opción...</option>';

  const opcionesFiltradas = productosDesdeCSV.filter(p =>
    normalizar(p.tipo) === tipoSeleccionado
  );

  if (opcionesFiltradas.length === 0) {
    const option = document.createElement("option");
    option.textContent = "No se encontraron coincidencias";
    selectMarca.appendChild(option);
    return;
  }

  const nombresUnicos = [...new Set(opcionesFiltradas.map(p => p.nombre))];

  nombresUnicos.forEach(nombre => {
    const option = document.createElement("option");
    option.value = nombre;
    option.textContent = nombre;
    selectMarca.appendChild(option);
  });
}

// Activar el listener cuando el DOM esté listo
document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("producto").addEventListener("input", actualizarSelectMarca);
});