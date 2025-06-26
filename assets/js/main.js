// --- MENÚ HAMBURGUESA ---
document.addEventListener('DOMContentLoaded', () => {
  const hamburgerMenu = document.querySelector('.hamburger-menu');
  const sideMenu = document.querySelector('.side-menu');
  if (hamburgerMenu && sideMenu) {
    hamburgerMenu.addEventListener('click', () => {
      sideMenu.classList.toggle('open');
      hamburgerMenu.classList.toggle('active');
    });
  }
});

// --- MENÚ DE CATEGORÍAS ---
document.addEventListener('DOMContentLoaded', () => {
  const toggleButton = document.getElementById('toggle-genres');
  const genreList = document.querySelector('.genre-visible');
  if (toggleButton && genreList) {
    toggleButton.addEventListener('click', () => {
      genreList.classList.toggle('expanded');
      toggleButton.textContent = genreList.classList.contains('expanded') ? 'Ver menos' : 'Ver más';
    });
  }
});

// --- BOTÓN BUSCAR (recomendador original) ---
// document.addEventListener('DOMContentLoaded', () => {
//   const buscarBtn = document.getElementById('buscarBtn');
//   if (buscarBtn) {
//     buscarBtn.addEventListener('click', () => {
//       const descripcion = document.getElementById('descripcionInput').value;
//       fetch(`/recomendador/?descripcion=${encodeURIComponent(descripcion)}`)
//         .then(response => response.json())
//         .then(data => {
//           if (data.recomendaciones && data.recomendaciones.length > 0) {
//             mostrarRecomendados(data.recomendaciones);
//           } else {
//             document.getElementById('recomendadosGrid').innerHTML = '<p>No se encontraron recomendaciones.</p>';
//           }
//         })
//         .catch(error => console.error('Error al obtener recomendaciones:', error));
//     });
//   }
// });

// --- MODALES DE PREFERENCIAS ---
document.addEventListener('DOMContentLoaded', () => {
  const modal1 = document.getElementById("modal-preferencia-1");
  const modal2 = document.getElementById("modal-preferencia-2");
  const modal3 = document.getElementById("modal-preferencia-3");

  const next1 = document.getElementById("next-1");
  const next2 = document.getElementById("next-2");
  const finish = document.getElementById("finish");

  if (modal1 && next1) {
    next1.addEventListener("click", () => {
      modal1.classList.add("hidden");
      modal2?.classList.remove("hidden");
    });
  }

  if (modal2 && next2) {
    next2.addEventListener("click", () => {
      modal2.classList.add("hidden");
      modal3?.classList.remove("hidden");
    });
  }

  if (modal3 && finish) {
    finish.addEventListener("click", () => {
      modal3.classList.add("hidden");
      alert("Preferencias guardadas. ¡Gracias!");
    });
  }

  if (modal1) {
    modal1.classList.remove("hidden"); // Mostrar modal 1 al cargar
  }
});

// --- FUNCIONES DE RECOMENDADOS ---
function mostrarRecomendados(libros) {
  const contenedor = document.getElementById('recomendadosGrid');
  if (contenedor) {
    contenedor.innerHTML = '';
    libros.forEach(libro => {
      contenedor.innerHTML += `
        <div class="book-item">
          <img src="${libro.portada}" alt="Portada del libro" class="book-placeholder" />
        </div>
      `;
    });
  }
}

// --- LIBRO VS LIBRO MODAL ---
document.addEventListener("DOMContentLoaded", () => {
  const libroVsLibroButton = document.getElementById("libroVsLibroButton");
  const libroVsLibroModal = document.getElementById("compararModal");
  const closeModalButton = document.getElementById("closeModalButton");

  function abrirModal() {
    if (libroVsLibroModal) {
      libroVsLibroModal.classList.remove("hidden");
      libroVsLibroModal.style.display = "flex";
      document.body.style.overflow = "hidden";
    }
  }

  function cerrarModal() {
    if (libroVsLibroModal) {
      libroVsLibroModal.classList.add("hidden");
      libroVsLibroModal.style.display = "none";
      document.body.style.overflow = "auto";
    }
  }

  if (libroVsLibroButton) {
    libroVsLibroButton.addEventListener("click", (e) => {
      e.preventDefault();
      abrirModal();
    });
  }

  if (closeModalButton) {
    closeModalButton.addEventListener("click", (e) => {
      e.preventDefault();
      cerrarModal();
    });
  }

  if (libroVsLibroModal) {
    libroVsLibroModal.addEventListener("click", (event) => {
      if (event.target === libroVsLibroModal) {
        cerrarModal();
      }
    });
  }

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && !libroVsLibroModal.classList.contains("hidden")) {
      cerrarModal();
    }
  });
});

// --- MODAL GENEROS RELACIONADOS ---
document.addEventListener("DOMContentLoaded", () => {
  const libroVsLibroButton = document.getElementById("libroVsLibroButton");
  const libroVsLibroModal = document.getElementById("compararModal");
  const closeModalButton = document.getElementById("closeModalButton");

  const generosButton = document.getElementById("generosRelacionadosButton") || 
                       Array.from(document.querySelectorAll('button')).find(btn => 
                         btn.textContent.trim().toLowerCase().includes('generos relacionados'));

  const generosModal = document.getElementById("generosModal");
  const closeGenerosButton = document.getElementById("closeGenerosButton");
  const generoBtns = document.querySelectorAll('.genero-btn');

  function abrirModal() {
    if (libroVsLibroModal) {
      libroVsLibroModal.classList.remove("hidden");
      libroVsLibroModal.style.display = "flex";
      document.body.style.overflow = "hidden";
    }
  }

  function cerrarModal() {
    if (libroVsLibroModal) {
      libroVsLibroModal.classList.add("hidden");
      libroVsLibroModal.style.display = "none";
      document.body.style.overflow = "auto";
    }
  }

  function abrirGenerosModal() {
    if (generosModal) {
      generosModal.classList.remove("hidden");
      generosModal.style.display = "flex";
      document.body.style.overflow = "hidden";
      cargarGenerosRecomendados();
    }
  }

  function cerrarGenerosModal() {
    if (generosModal) {
      generosModal.classList.add("hidden");
      generosModal.style.display = "none";
      document.body.style.overflow = "auto";
    }
  }

  function mostrarSoloPortadas(libros) {
    const contenedor = document.getElementById('recomendadosGrid');
    if (!contenedor) {
      console.error("No se encontró el contenedor de recomendaciones");
      return;
    }

    contenedor.innerHTML = '';
    libros.forEach(libro => {
      contenedor.innerHTML += `
        <div class="libro">
          <img src="${libro.portada}" alt="Portada de ${libro.titulo}" />
        </div>
      `;
    });
  }

  if (libroVsLibroButton) {
    libroVsLibroButton.addEventListener("click", (e) => {
      e.preventDefault();
      abrirModal();
    });
  }

  if (closeModalButton) {
    closeModalButton.addEventListener("click", (e) => {
      e.preventDefault();
      cerrarModal();
    });
  }

  if (libroVsLibroModal) {
    libroVsLibroModal.addEventListener("click", (event) => {
      if (event.target === libroVsLibroModal) {
        cerrarModal();
      }
    });
  }

  if (generosModal) {
    generosModal.addEventListener("click", (event) => {
      if (event.target === generosModal) {
        cerrarGenerosModal();
      }
    });
  }

  generoBtns.forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      btn.classList.toggle('selected');
      const genero = btn.getAttribute('data-genero');
      console.log('Género seleccionado:', genero);
    });
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      if (!libroVsLibroModal.classList.contains("hidden")) {
        cerrarModal();
      }
      if (generosModal && !generosModal.classList.contains("hidden")) {
        cerrarGenerosModal();
      }
    }
  });

  console.log("Script de modales cargado correctamente");
});

// --- CAPTURA DE RESPUESTAS MODALES PREFERENCIAS Y ENVÍO ---
document.addEventListener('DOMContentLoaded', () => {
  const respuestas = {
    generos: [],
    tipo_final: "",
    tipo_libro: ""
  };

  // capturar géneros
  document.querySelectorAll('#modal-preferencia-1 .option').forEach(btn => {
    btn.addEventListener('click', () => {
      if (respuestas.generos.includes(btn.innerText)) {
        respuestas.generos = respuestas.generos.filter(g => g !== btn.innerText);
        btn.classList.remove('selected');
      } else {
        respuestas.generos.push(btn.innerText);
        btn.classList.add('selected');
      }
    });
  });

  // capturar tipo de final
  document.querySelectorAll('#modal-preferencia-2 .option').forEach(btn => {
    btn.addEventListener('click', () => {
      respuestas.tipo_final = btn.innerText;
      document.querySelectorAll('#modal-preferencia-2 .option').forEach(b => b.classList.remove('selected'));
      btn.classList.add('selected');
    });
  });

  // capturar tipo de libro
  document.querySelectorAll('#modal-preferencia-3 .option').forEach(btn => {
    btn.addEventListener('click', () => {
      respuestas.tipo_libro = btn.innerText;
      document.querySelectorAll('#modal-preferencia-3 .option').forEach(b => b.classList.remove('selected'));
      btn.classList.add('selected');
    });
  });

  // Enviar al finalizar
  const btnFinish = document.getElementById('finish');
  if (btnFinish) {
    btnFinish.addEventListener('click', function () {
      fetch('/guardar_preferencias/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify(respuestas)
      })
      .then(response => response.json())
      .then(data => {
        alert(data.mensaje);
        window.location.href = "/index/";
      });
    });
  }

  // Función para obtener token CSRF
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      for (let cookie of document.cookie.split(';')) {
        cookie = cookie.trim();
        if (cookie.startsWith(name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }
});

// --- CARGA AUTOMÁTICA DE RECOMENDADOS POR GÉNERO ---
document.addEventListener('DOMContentLoaded', () => {
  console.log('✅ Script de recomendados iniciado');

  fetch('/recomendados_por_genero/')
    .then(res => res.json())
    .then(data => {
      console.log('📚 Datos recibidos:', data);
      const contenedor = document.getElementById('recomendadosContainer');
      if (!contenedor) {
        console.error('❌ No se encontró el contenedor #recomendadosContainer');
        return;
      }

      contenedor.innerHTML = '';

      if (data.libros && data.libros.length > 0) {
        data.libros.forEach(libro => {
          const link = document.createElement('a');
          link.href = `/detalle_libro/${libro.id}/`;

          const img = document.createElement('img');
          img.src = libro.portada;
          img.alt = 'Portada del libro';
          img.classList.add('book-cover');

          link.appendChild(img);

          const contLibro = document.createElement('div');
          contLibro.classList.add('book-placeholder');
          contLibro.appendChild(link);

          contenedor.appendChild(contLibro);
        });
      } else {
        contenedor.innerHTML = '<p style="color:white;">No se encontraron recomendaciones.</p>';
      }
    })
    .catch(error => {
      console.error('Error al cargar recomendaciones:', error);
    });
});

// --- AGREGAR A FAVORITOS ---
document.addEventListener('DOMContentLoaded', function () {
  const botones = document.querySelectorAll('.dl-btn-favoritos');

  botones.forEach(btn => {
    btn.addEventListener('click', function () {
      const libroId = this.getAttribute('data-libro-id');

      fetch('/agregar_a_favoritos/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          'X-CSRFToken': getCookie('csrftoken'),
        },
        body: `libro_id=${libroId}`
      })
      .then(response => response.json())
      .then(data => {
        alert(data.mensaje || data.error);
      })
      .catch(error => {
        console.error('Error al agregar a favoritos:', error);
      });
    });
  });

  // Función para obtener token CSRF
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }
});

// --- BUSCADOR (buscar por título o género) ---
document.addEventListener("DOMContentLoaded", function () {
  const btnBuscar = document.getElementById("buscarBtn");
  const input = document.getElementById("descripcionInput");
  const contenedor = document.getElementById("recomendacionesContainer"); // o donde quieras mostrar resultados

  btnBuscar.addEventListener("click", () => {
    const textoBusqueda = input.value.trim();
    if (!textoBusqueda) {
      alert("Por favor escribe algo para buscar");
      return;
    }

    fetch(`/buscar_libros/?q=${encodeURIComponent(textoBusqueda)}`)
      .then(response => response.json())
      .then(data => {
        contenedor.innerHTML = "";

        if (data.libros && data.libros.length > 0) {
          data.libros.forEach(libro => {
            const card = document.createElement("div");
            card.classList.add("book-item");

            const img = document.createElement("img");
            img.src = libro.portada;
            img.alt = libro.titulo || "Portada";

            const titulo = document.createElement("p");
            titulo.textContent = libro.titulo;
            titulo.style.marginTop = "0.5rem";
            titulo.style.color = "white";
            titulo.style.fontWeight = "bold";

            card.appendChild(img);
            card.appendChild(titulo);
            contenedor.appendChild(card);
          });
        } else {
          contenedor.innerHTML = "<p style='color: white;'>No se encontraron libros.</p>";
        }
      })
      .catch(error => {
        console.error("Error:", error);
        contenedor.innerHTML = "<p style='color: white;'>Error en la búsqueda.</p>";
      });
  });
});


/*----------validacion registro------- */
function validarFormulario() {
  const contraseña = document.getElementById("contraseña").value;
  const confirmar = document.getElementById("confirm-contraseña").value;

  // Esta parte detiene el formulario si las contraseñas no coinciden
  if (contraseña !== confirmar) {
    document.getElementById("confirm-contraseña").setCustomValidity("Las contraseñas no coinciden");
    return false;
  } else {
    document.getElementById("confirm-contraseña").setCustomValidity("");
  }

  return true; // Si todo está bien, se permite el envío
}