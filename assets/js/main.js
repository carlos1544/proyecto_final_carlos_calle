//----------------------------------------------------
//                   PREFERENCIAS
//----------------------------------------------------


// Selecciona los modales y botones
const modal1 = document.getElementById("modal-preferencia-1");
const modal2 = document.getElementById("modal-preferencia-2");
const modal3 = document.getElementById("modal-preferencia-3");

const next1 = document.getElementById("next-1");
const next2 = document.getElementById("next-2");
const finish = document.getElementById("finish");

// Función para mostrar un modal
function showModal(modal) {
  modal.classList.remove("hidden");
}

// Función para ocultar un modal
function hideModal(modal) {
  modal.classList.add("hidden");
}

// Evento para ir de la Preferencia 1 a la 2
next1.addEventListener("click", () => {
  hideModal(modal1);
  showModal(modal2);
});

// Evento para ir de la Preferencia 2 a la 3
next2.addEventListener("click", () => {
  hideModal(modal2);
  showModal(modal3);
});

// Evento para finalizar las preferencias
finish.addEventListener("click", () => {
  hideModal(modal3);
  alert("Preferencias guardadas. ¡Gracias!");
});

// Mostrar el primer modal después del registro
window.addEventListener("load", () => {
  showModal(modal1);
});

//----------------------------------------------------
//                     MENU
//----------------------------------------------------

document.addEventListener('DOMContentLoaded', () => {
  const hamburgerMenu = document.querySelector('.hamburger-menu');
  const sideMenu = document.querySelector('.side-menu');

  if (!hamburgerMenu || !sideMenu) {
    console.log('No se encontró el botón hamburguesa o el menú lateral');
    return;
  }

  hamburgerMenu.addEventListener('click', () => {
    console.log('Click en botón hamburguesa detectado');

    // Alternar clases en cada click
    sideMenu.classList.toggle('open');
    hamburgerMenu.classList.toggle('active');

    console.log(
      'Estado del menú:',
      sideMenu.classList.contains('open') ? 'Abierto' : 'Cerrado'
    );
  });
});


//----------------------------------------------------
//             MENU DE CATEGORIAS
//----------------------------------------------------

document.addEventListener('DOMContentLoaded', function () {
  const toggleButton = document.getElementById('toggle-genres');
  const genreList = document.querySelector('.genre-visible');

  if (toggleButton && genreList) {
    toggleButton.addEventListener('click', function () {
      genreList.classList.toggle('expanded');
      toggleButton.textContent = genreList.classList.contains('expanded') ? 'Ver menos' : 'Ver más';
    });
  }
});

document.addEventListener('DOMContentLoaded', () => {
  const btn = document.getElementById('buscarBtn');
  btn.addEventListener('click', () => {
    console.log('Botón buscar clickeado');

    const descripcion = document.getElementById('descripcionInput').value;
    console.log('Descripción:', descripcion);

    fetch(`/recomendador/?descripcion=${encodeURIComponent(descripcion)}`)
      .then(response => response.json())
      .then(data => {
        console.log('Datos recibidos:', data);
        if(data.recomendaciones && data.recomendaciones.length > 0) {
          mostrarRecomendados(data.recomendaciones);
        } else {
          document.getElementById('recomendadosGrid').innerHTML = '<p>No se encontraron recomendaciones.</p>';
        }
      })
      .catch(error => {
        console.error('Error al obtener recomendaciones:', error);
      });
  });
});

function mostrarRecomendados(libros) {
  const contenedor = document.getElementById('recomendadosGrid');
  contenedor.innerHTML = ''; // limpia el contenido

  libros.forEach(libro => {
    const libroHTML = `
      <div class="book-item">
        <h3>${libro.titulo}</h3>
        <p>Autor: ${libro.autor}</p>
        <p>Género: ${libro.genero}</p>
        <p>${libro.descripcion}</p>
      </div>
    `;
    contenedor.innerHTML += libroHTML;
  });
}









