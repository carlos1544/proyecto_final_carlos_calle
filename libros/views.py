# Imports agrupados y ordenados
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib import messages, auth
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
from django.db.models import Q
from django.db import IntegrityError

import json
import random

from .models import (
    Libro,
    Usuario,
    PreferenciaUsuario,
    RecomendacionIA,
    SeleccionLibro,
    Favorito,
    LibroUsuario,
)
from .recomendador import limpiar_texto, vectorizar_datos
from libros.recomendador_cache import vectorizar_datos_cacheado  
from sklearn.metrics.pairwise import cosine_similarity

# -------------------------
# Vistas de autenticación y usuario
# -------------------------

def registro(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        email = request.POST.get('email')
        password = request.POST.get('contraseña')

        if not password:
            return HttpResponse("Error: la contraseña no fue enviada.")

        if Usuario.objects.filter(nombre=nombre).exists():
            messages.error(request, "El nombre ya está en uso.")
            return redirect('registro')

        if Usuario.objects.filter(email=email).exists():
            messages.error(request, "El correo ya está en uso.")
            return redirect('registro')

        usuario = Usuario.objects.create_user(
            nombre=nombre,
            email=email,
            password=password
        )
        login(request, usuario)
        request.session['mostrar_encuesta'] = True
        return redirect('inicio')
    return render(request, "libros/registro.html")

def login_view(request):
    if request.method == 'POST':
        nombre = request.POST.get('usuario')
        password = request.POST.get('password')

        print(f"Intentando login con usuario={nombre} y contraseña={password}")

        try:
            usuario = Usuario.objects.get(nombre=nombre)
            if usuario.check_password(password):
                print("Contraseña correcta manualmente")
            else:
                print("Contraseña incorrecta manualmente")
        except Usuario.DoesNotExist:
            print("Usuario no existe")

        usuario_auth = authenticate(request, nombre=nombre, password=password)

        if usuario_auth is not None:
            print(f"Usuario autenticado: {usuario_auth}")
            login(request, usuario_auth)
            return redirect('inicio')
        else:
            print("Usuario o contraseña incorrectos")
            messages.error(request, 'Usuario o contraseña incorrectos')
            return render(request, 'libros/login.html')

    return render(request, 'libros/login.html')

def logout_view(request):
    request.session.flush() 
    return redirect('inicio') 

# -------------------------
# Vistas principales y exploración
# -------------------------

def inicio(request):
    print(f"[DEBUG] Vista inicio ejecutada. Usuario logueado: {request.user.is_authenticated}")

    logueado = request.user.is_authenticated
    mostrar_encuesta = request.session.get('mostrar_encuesta', False)

    libros_fantasia = Libro.objects.filter(genero__icontains='fantasia')[:5]
    libros_drama = Libro.objects.filter(genero__icontains='drama')[:5]
    libros_romance = Libro.objects.filter(genero__icontains='romance')[:5]
    libros_terror = Libro.objects.filter(genero__icontains='terror')[:5]

    return render(request, 'libros/index.html', {
        'logueado': logueado,
        'mostrar_encuesta': mostrar_encuesta,
        'libros_fantasia': libros_fantasia,
        'libros_drama': libros_drama,
        'libros_romance': libros_romance,
        'libros_terror': libros_terror,
    })

@login_required
def explorar_libros(request):
    libros_fantasia = Libro.objects.filter(genero__icontains='fantasia')[:5]
    libros_drama = Libro.objects.filter(genero__icontains='drama')[:5]
    libros_romance = Libro.objects.filter(genero__icontains='romance')[:5]
    libros_terror = Libro.objects.filter(genero__icontains='terror')[:5]
    return render(request, 'libros/explorar-libros.html', {
        'libros_fantasia': libros_fantasia,
        'libros_drama': libros_drama,
        'libros_romance': libros_romance,
        'libros_terror': libros_terror,
    })

@login_required
def explorar_ia(request):
    if request.method == 'POST':
        texto = request.POST.get('consulta_texto', '').strip()
        if not texto:
            messages.error(request, "Ingrese el texto por favor")
            return render(request, 'explorar_ia.html')
        recomendaciones = funcion_recomendacion(texto)
        return render(request, 'explorar_ia.html', {'recomendaciones': recomendaciones, 'texto': texto})
    else:
        return render(request, 'libros/explorar_ia.html')

@login_required
def detalle_libro(request, libro_id):
    libro = get_object_or_404(Libro, id=libro_id)
    libro_usuario_estado = None
    if request.user.is_authenticated:
        try:
            libro_usuario = LibroUsuario.objects.get(usuario=request.user, libro=libro)
            libro_usuario_estado = libro_usuario.estado
        except LibroUsuario.DoesNotExist:
            pass

    return render(request, 'libros/detalle_libro.html', {
        'libro': libro,
        'libro_usuario_estado': libro_usuario_estado,
    })

@login_required
def lista_libros(request):
    libros = Libro.objects.all()
    return render(request, 'libros/index.html', {'libros': libros})

# -------------------------
# Perfil, configuración y gestión usuario
# -------------------------

@login_required
def perfil(request):
    usuario = request.user
    generos = []
    try:
        preferencias = PreferenciaUsuario.objects.get(usuario=usuario)
        generos = preferencias.generos
    except PreferenciaUsuario.DoesNotExist:
        pass

    return render(request, 'libros/perfil.html', {
        'generos_favoritos': generos,
    }) 

@login_required
def configuracion(request):
    usuario_nombre = request.session.get('usuario_nombre', 'Invitado')
    return render(request, 'libros/configuracion.html', {'usuario_nombre': usuario_nombre})

@login_required
def cambiar_nombre(request):
    if request.method == "POST":
        nuevo_nombre = request.POST.get('nuevo_nombre')
        usuario = request.user
        
        if nuevo_nombre and not Usuario.objects.filter(nombre=nuevo_nombre).exists():
            usuario.nombre = nuevo_nombre
            usuario.save()
            messages.success(request, "Nombre cambiado exitosamente.")
            return redirect('configuracion')
        else:
            messages.error(request, "El nombre ya existe o es inválido.")
    
    return render(request, 'configuracion')  # Ajusta a plantilla correcta si es necesario

@login_required
def cambiar_contrasena(request):
    if request.method == 'POST':
        actual = request.POST.get('password_actual')
        nueva = request.POST.get('nueva_password')
        if request.user.check_password(actual):
            request.user.set_password(nueva)
            request.user.save()
            update_session_auth_hash(request, request.user)
            messages.success(request, 'Contraseña actualizada.')
            return redirect('inicio')
        else:
            messages.error(request, 'Contraseña actual incorrecta.')
            return redirect('configuracion')

@login_required
def eliminar_cuenta(request):
    if request.method == 'POST':
        password = request.POST.get('confirmacion_password')
        if request.user.check_password(password):
            request.user.delete()
            messages.success(request, 'Tu cuenta ha sido eliminada.')
            return redirect('inicio')
        else:
            messages.error(request, 'Contraseña incorrecta.')
            return redirect('configuracion')

# -------------------------
# Favoritos
# -------------------------

@login_required
def favoritos(request):
    favoritos = Favorito.objects.filter(usuario=request.user).select_related('libro')
    libros_favoritos = [f.libro for f in favoritos]

    return render(request, 'libros/favoritos.html', {
        'libros_favoritos': libros_favoritos
    })

@require_POST
@login_required
def agregar_a_favoritos(request):
    try:
        libro_id = request.POST.get('libro_id')
        libro = Libro.objects.get(id=libro_id)

        favorito, creado = Favorito.objects.get_or_create(
            usuario=request.user,
            libro=libro
        )

        if creado:
            return JsonResponse({'mensaje': 'Libro agregado a favoritos'})
        else:
            return JsonResponse({'mensaje': 'Ya estaba en favoritos'})
    except Libro.DoesNotExist:
        return JsonResponse({'error': 'Libro no encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# -------------------------
# Historial
# -------------------------

@login_required
def historial(request):
    usuario = request.user
    libros_leidos = Libro.objects.filter(librousuario__usuario=usuario, librousuario__estado='leido')
    libros_por_leer = Libro.objects.filter(librousuario__usuario=usuario, librousuario__estado='por_leer')
    recomendaciones_ia = RecomendacionIA.objects.filter(usuario=usuario).select_related('libro').order_by('-id')
    context = {
        'libros_leidos': libros_leidos,
        'libros_por_leer': libros_por_leer,
        'recomendaciones_ia': recomendaciones_ia,
    }
    return render(request, 'libros/historial.html', context)

@login_required
@require_POST
def marcar_estado_libro(request):
    libro_id = request.POST.get('libro_id')
    estado = request.POST.get('estado')

    if not libro_id or not libro_id.isdigit():
        return JsonResponse({'error': 'ID de libro inválido'}, status=400)

    if estado not in ['leido', 'por_leer']:
        return JsonResponse({'error': 'Estado inválido'}, status=400)

    try:
        libro = Libro.objects.get(id=libro_id)
        obj, created = LibroUsuario.objects.update_or_create(
            usuario=request.user,
            libro=libro,
            defaults={'estado': estado}
        )
        return JsonResponse({'success': True})
    except Libro.DoesNotExist:
        return JsonResponse({'error': 'Libro no encontrado'}, status=404)

# -------------------------
# Búsquedas y filtros
# -------------------------

@login_required
def buscar_libros(request):
    q = request.GET.get('q', '').strip()
    if not q:
        return JsonResponse({'libros': []})

    libros = Libro.objects.filter(Q(titulo__icontains=q) | Q(genero__icontains=q))[:20]

    libros_data = [
        {
            'id': libro.id,
            'titulo': libro.titulo,
            'portada': libro.portada,
        }
        for libro in libros
    ]

    return JsonResponse({'libros': libros_data})

def libros_por_genero(request, genero):
    libros = Libro.objects.filter(genero__icontains=genero)
    libros_data = [
        {
            'id': libro.id,
            'titulo': libro.titulo,
            'portada': libro.portada,
        } for libro in libros
    ]
    return JsonResponse({'libros': libros_data})

# -------------------------
# Recomendaciones IA
# -------------------------

@login_required
def recomendar_view(request):
    descripcion = request.GET.get('descripcion', '')
    if not descripcion:
        return JsonResponse({'error': 'No se proporcionó descripción'}, status=400)

    descripcion_limpia = limpiar_texto(descripcion)
    if not descripcion_limpia.strip():
        return JsonResponse({'error': 'La descripción está vacía después de limpiar'}, status=400)

    vectores, libros_df, vectorizador = vectorizar_datos_cacheado()
    descripcion_vector = vectorizador.transform([descripcion_limpia])
    similitudes = cosine_similarity(descripcion_vector, vectores).flatten()
    libros_df['similitud'] = similitudes
    libros_ordenados = libros_df.sort_values(by='similitud', ascending=False)

    recomendaciones = libros_ordenados.head(8)[['id', 'portada', 'titulo']].to_dict(orient='records')

    for rec in recomendaciones:
        try:
            libro_obj = Libro.objects.get(id=rec['id'])
            RecomendacionIA.objects.get_or_create(usuario=request.user, libro=libro_obj)
        except Libro.DoesNotExist:
            continue
        except IntegrityError:
            continue

    return JsonResponse({'recomendaciones': recomendaciones})

@login_required
def recomendados_por_genero(request):
    try:
        preferencias = PreferenciaUsuario.objects.get(usuario=request.user)
        generos = preferencias.generos

        libros = Libro.objects.filter(genero__in=generos).order_by('?')[:6]

        libros_data = [
            {
                'portada': libro.portada,
                'id': libro.id,
            } for libro in libros
        ]

        return JsonResponse({'libros': libros_data})

    except PreferenciaUsuario.DoesNotExist:
        return JsonResponse({'libros': []})

# -------------------------
# Guardar preferencias (encuesta)
# -------------------------

@login_required
def guardar_preferencias(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            generos = data.get('generos', [])
            tipo_final = data.get('tipo_final', '')
            tipo_libro = data.get('tipo_libro', '')

            usuario = request.user if request.user.is_authenticated else None

            if usuario is None:
                return JsonResponse({'error': 'Usuario no autenticado'}, status=401)

            preferencias, creado = PreferenciaUsuario.objects.update_or_create(
                usuario=usuario,
                defaults={
                    'generos': generos,
                    'tipo_final': tipo_final,
                    'tipo_libro': tipo_libro,
                }
            )
            request.session['mostrar_encuesta'] = False

            return JsonResponse({'mensaje': 'Preferencias guardadas correctamente'})

        except json.JSONDecodeError:
            return JsonResponse({'error': 'JSON inválido'}, status=400)
        except Exception as e:
            print(f"Error al guardar las preferencias: {e}")
            return JsonResponse({'error': 'Error al guardar las preferencias'}, status=500)

    return JsonResponse({'error': 'Método no permitido'}, status=405)

# -------------------------
# Comparaciones libro vs libro
# -------------------------

@login_required
def obtener_libros_comparacion(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Usuario no autenticado'}, status=401)

    try:
        preferencias = PreferenciaUsuario.objects.get(usuario=request.user)
        generos_preferidos = preferencias.generos
    except PreferenciaUsuario.DoesNotExist:
        return JsonResponse({'error': 'Preferencias no encontradas'}, status=404)

    libros_filtrados = Libro.objects.filter(genero__in=generos_preferidos)

    if libros_filtrados.count() < 10:
        return JsonResponse({'error': 'No hay suficientes libros para comparar'}, status=400)

    libros_aleatorios = random.sample(list(libros_filtrados), 10)

    libros_serializados = [
        {
            'id': libro.id,
            'portada': libro.portada, 
            'descripcion': libro.descripcion,
        } for libro in libros_aleatorios
    ]

    return JsonResponse({'libros': libros_serializados})

@login_required
@require_POST
@csrf_protect
def guardar_seleccion_vs(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'No autenticado'}, status=401)

    try:
        data = json.loads(request.body)
        elegido_id = data.get('elegido')

        if not elegido_id:
            return JsonResponse({'error': 'ID de libro no proporcionado'}, status=400)

        libro = Libro.objects.get(id=elegido_id)

        SeleccionLibro.objects.create(usuario=request.user, libro=libro)

        return JsonResponse({'status': 'ok', 'libro': libro.titulo})
    
    except Libro.DoesNotExist:
        return JsonResponse({'error': 'Libro no encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'error': f'Error interno: {str(e)}'}, status=500)

@login_required
def libro_vs_libro(request):
    usuario = request.user

    try:
        preferencias = PreferenciaUsuario.objects.get(usuario=usuario)
    except PreferenciaUsuario.DoesNotExist:
        return render(request, 'error.html', {'mensaje': 'No has completado la encuesta de preferencias.'})

    generos_preferidos = preferencias.generos
    tipo_libro = preferencias.tipo_libro
    tipo_final = preferencias.tipo_final

    libros_filtrados = Libro.objects.filter(genero__in=generos_preferidos)

    libros_seleccionados = random.sample(list(libros_filtrados), min(5, libros_filtrados.count()))

    libros_json = []
    for libro in libros_seleccionados:
        libros_json.append({
            'titulo': libro.titulo,
            'autor': libro.autor,
            'descripcion': libro.descripcion,
            'portada_url': libro.portada.url
        })

    return render(request, 'libro_vs_libro.html', {
        'libros': libros_json
    })


from django.conf import settings
from django.template.loader import get_template
from django.template.loader import get_template, TemplateDoesNotExist

def leer_libro(request, libro_id):
    # Lista los directorios donde Django busca las plantillas
    print("Directorios de plantillas:")
    for dir_path in settings.TEMPLATES[0]['DIRS']:
        print(f"- {dir_path}")

    try:
        # Verifica si Django puede cargar la plantilla
        template = get_template('leer_libro.html')
        print(f"Plantilla encontrada: {template.origin.name}")
    except Exception as e:
        print(f"Error al buscar la plantilla: {e}")
        return HttpResponse("Error al buscar la plantilla.", status=500)

    libro = get_object_or_404(Libro, id=libro_id)
    return render(request, 'leer-libro.html', {'libro': libro})

