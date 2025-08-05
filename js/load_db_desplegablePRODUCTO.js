let categoryTree = {};
let filteredTree = {};
let lastFilter = "";

// Cargar categorías desde CSV
async function loadCategoriesFromCSV() {
  try {
    const response = await fetch('./database/menu/db_desplegablePRODUCTO.csv');
    const csvText = await response.text();
    const lines = csvText.trim().split('\n');
    const categories = lines[0].split(',');

    categoryTree = {};
    categories.forEach(categoria => {
      if (categoria && categoria.trim() !== '') {
        categoryTree[categoria.trim()] = [];
      }
    });

    for (let i = 1; i < lines.length; i++) {
      const values = lines[i].split(',');
      for (let j = 0; j < categories.length && j < values.length; j++) {
        const categoria = categories[j].trim();
        const subcategoria = values[j] ? values[j].trim() : '';
        if (categoria && subcategoria && subcategoria !== '') {
          if (!categoryTree[categoria].includes(subcategoria)) {
            categoryTree[categoria].push(subcategoria);
          }
        }
      }
    }
    renderCategoryMenu();
  } catch (error) {
    console.error('Error cargando categorías:', error);
    categoryTree = {
      'Almacén': ['Aceites y vinagres', 'Pastas secas', 'Conservas'],
      'Bebidas': ['Gaseosas', 'Jugos', 'Aguas'],
      'Lácteos': ['Leches', 'Yogures', 'Quesos'],
    };
    renderCategoryMenu();
  }
}

// Renderiza el menú de categorías (filtrado o completo)
function renderCategoryMenu(tree = categoryTree) {
  const menu = document.getElementById('categoryMenu');
  menu.innerHTML = '';

  let found = false;
  for (const categoria in tree) {
    const subcats = tree[categoria];
    if (subcats.length > 0) {
      found = true;
      const catItem = document.createElement('div');
      catItem.className = 'category-item level-0';
      catItem.innerHTML = `<b>${categoria}</b>`;
      menu.appendChild(catItem);

      for (const subcategoria of subcats) {
        const subItem = document.createElement('div');
        subItem.className = 'category-item level-1';
        subItem.innerHTML = subcategoria;
        subItem.onclick = (e) => {
          e.stopPropagation();
          selectCategory(`${categoria} > ${subcategoria}`);
          hideCategoryMenu();
        };
        menu.appendChild(subItem);
      }
    }
  }
  if (!found) {
    menu.innerHTML = '<div class="category-item">No hay coincidencias</div>';
  }
}

// Filtra el árbol según lo que escribe el usuario
function filterCategoryMenu() {
  const input = document.getElementById('producto').value.trim().toLowerCase();
  lastFilter = input;
  if (!input) {
    renderCategoryMenu(categoryTree);
    return;
  }
  filteredTree = {};
  for (const categoria in categoryTree) {
    const subcats = categoryTree[categoria].filter(subcat =>
      subcat.toLowerCase().includes(input)
    );
    if (subcats.length > 0) {
      filteredTree[categoria] = subcats;
    }
  }
  renderCategoryMenu(filteredTree);
}

// Al seleccionar una subcategoría, completa el input SOLO con la subcategoría y dispara actualización
function selectCategory(categoryPath) {
  const subcategoria = categoryPath.split('>').pop().trim();
  const input = document.getElementById('producto');
  input.value = subcategoria;

  // 🔥 Esto dispara el evento 'input' como si el usuario hubiese escrito a mano
  input.dispatchEvent(new Event('input'));
  
  filterCategoryMenu();
}

// Mostrar el menú
function showCategoryMenu() {
  document.getElementById('categoryMenu').classList.add('show');
  filterCategoryMenu(); // Refresca el menú al abrir
}

// Ocultar el menú
function hideCategoryMenu() {
  document.getElementById('categoryMenu').classList.remove('show');
}

// Cerrar el menú al hacer click fuera
document.addEventListener('click', function(event) {
  const dropdown = document.querySelector('.category-dropdown');
  if (!dropdown.contains(event.target)) {
    hideCategoryMenu();
  }
});

// Inicializar el menú al cargar
document.addEventListener('DOMContentLoaded', function() {
  loadCategoriesFromCSV();
});