(() => {
  const categoryMenu = document.getElementById('categoryMenu');
  const inputMarca = document.getElementById('marca');

  let csvData = [];
  let dropdown;

  // Cargar CSV desde la ruta correcta
  fetch('Scraping Super/database/productos/jumbo/jumbo_carnes_rotiseria_2025-08-02.csv')
    .then(response => {
      if (!response.ok) throw new Error('No se pudo cargar el CSV');
      return response.text();
    })
    .then(csvText => {
      csvData = Papa.parse(csvText, { header: true }).data;
      console.log('CSV cargado con', csvData.length, 'filas');
    })
    .catch(err => {
      console.error('Error cargando CSV:', err);
      alert('Error cargando datos. Asegúrate que el CSV esté en la ruta correcta y servido por un servidor local.');
    });

  // Crear dropdown flotante debajo del input #marca
  function createDropdown() {
    if (dropdown) return; // Ya creado
    dropdown = document.createElement('ul');
    dropdown.style.position = 'absolute';
    dropdown.style.backgroundColor = 'white';
    dropdown.style.border = '1px solid #ccc';
    dropdown.style.width = inputMarca.offsetWidth + 'px';
    dropdown.style.maxHeight = '200px';
    dropdown.style.overflowY = 'auto';
    dropdown.style.padding = '0';
    dropdown.style.margin = '0';
    dropdown.style.listStyle = 'none';
    dropdown.style.zIndex = '10000';
    dropdown.style.cursor = 'pointer';
    dropdown.style.boxShadow = '0 2px 6px rgba(0,0,0,0.2)';
    dropdown.style.display = 'none';

    document.body.appendChild(dropdown);
  }

  // Posicionar dropdown justo debajo del input
  function positionDropdown() {
    if (!dropdown) return;
    const rect = inputMarca.getBoundingClientRect();
    dropdown.style.left = rect.left + window.pageXOffset + 'px';
    dropdown.style.top = rect.bottom + window.pageYOffset + 'px';
    dropdown.style.width = inputMarca.offsetWidth + 'px';
  }

  // Mostrar opciones en dropdown
  function showDropdown(items) {
    createDropdown();
    dropdown.innerHTML = '';
    if (items.length === 0) {
      const li = document.createElement('li');
      li.textContent = 'No hay productos para esta categoría';
      li.style.padding = '8px';
      li.style.color = '#666';
      dropdown.appendChild(li);
    } else {
      items.forEach(item => {
        const li = document.createElement('li');
        li.textContent = item;
        li.style.padding = '8px';
        li.style.borderBottom = '1px solid #eee';

        li.addEventListener('mouseenter', () => {
          li.style.backgroundColor = '#f0f0f0';
        });
        li.addEventListener('mouseleave', () => {
          li.style.backgroundColor = 'white';
        });

        li.addEventListener('click', () => {
          inputMarca.value = item;
          hideDropdown();
        });

        dropdown.appendChild(li);
      });
    }
    positionDropdown();
    dropdown.style.display = 'block';
  }

  // Ocultar dropdown
  function hideDropdown() {
    if (dropdown) dropdown.style.display = 'none';
  }

  // Actualizar posición dropdown al hacer scroll o resize
  window.addEventListener('scroll', () => {
    if (dropdown && dropdown.style.display === 'block') {
      positionDropdown();
    }
  });
  window.addEventListener('resize', () => {
    if (dropdown && dropdown.style.display === 'block') {
      positionDropdown();
    }
  });

  // Escuchar clicks en el menú de categorías
  categoryMenu.addEventListener('click', (e) => {
    e.preventDefault();
    const target = e.target;

    let tipoSeleccionado = null;
    if (target.tagName === 'A' && target.dataset.tipo) {
      tipoSeleccionado = target.dataset.tipo;
    } else {
      tipoSeleccionado = target.textContent.trim();
    }
    if (!tipoSeleccionado) {
      console.log('No se pudo determinar tipo de producto seleccionado');
      return;
    }
    console.log('Tipo seleccionado:', tipoSeleccionado);

    if (csvData.length === 0) {
      console.log('CSV no cargado aún');
      return;
    }

    const productosFiltrados = csvData
      .filter(row => row['Tipo de Producto'] === tipoSeleccionado)
      .map(row => row['Nombre'])
      .filter(Boolean);

    console.log('Productos filtrados:', productosFiltrados.length);

    showDropdown(productosFiltrados);
  });

  // Ocultar dropdown si se hace click fuera o en input
  document.addEventListener('click', (e) => {
    if (dropdown && !dropdown.contains(e.target) && e.target !== inputMarca) {
      hideDropdown();
    }
  });

  // Ocultar dropdown si el usuario escribe en el input
  inputMarca.addEventListener('input', () => {
    hideDropdown();
  });
})();