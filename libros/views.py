from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Libro
from .recomendador import limpiar_texto, vectorizar_datos
from django.contrib import messages
from django.http import HttpResponse
from libros.models import Usuario

def perfil(request):
    return render(request, 'libros/perfil.html')

def explorar_libros(request):
    return render(request, 'libros/explorar-libros.html')

def explorar_ia(request):
    return render(request, 'libros/explorar_ia.html')

def historial(request):
    return render(request, 'libros/historial.html')

def favoritos(request):
    return render(request, 'libros/favoritos.html')

def configuracion(request):
    return render(request, 'libros/configuracion.html')

def inicio(request):
    logueado = 'usuario_id' in request.session
    return render(request, 'libros/index.html', {'logueado': logueado})

def logout_view(request):
    request.session.flush() 
    messages.success(request, "Has cerrado sesión correctamente.")
    return redirect('inicio') 

def lista_libros(request):
    libros = Libro.objects.all()
    return render(request, 'libros/index.html', {'libros': libros})


def recomendar_view(request):
    descripcion = request.GET.get('descripcion', '')
    if not descripcion:
        return JsonResponse({'error': 'No se proporcionó descripción'}, status=400)

    
    vectores, libros, vectorizador = vectorizar_datos()

    descripcion_limpia = limpiar_texto(descripcion)
    descripcion_vectorizada = vectorizador.transform([descripcion_limpia])

    from sklearn.metrics.pairwise import cosine_similarity
    similitudes = cosine_similarity(descripcion_vectorizada, vectores).flatten()

    libros['similitud'] = similitudes

    libros_ordenados = libros.sort_values(by='similitud', ascending=False)

    recomendaciones = libros_ordenados.head(8)[['titulo', 'autor', 'genero', 'descripcion','portada']].to_dict(orient='records')

    return JsonResponse({'recomendaciones': recomendaciones})



def registro(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        email = request.POST.get('email')
        contraseña = request.POST.get('contraseña')

        if not contraseña:
            return HttpResponse("Error: la contraseña no fue enviada.")

        if Usuario.objects.filter(nombre=nombre).exists():
            return HttpResponse("El nombre ya está en uso.")

        if Usuario.objects.filter(email=email).exists():
            return HttpResponse("El correo ya está en uso.")

        usuario = Usuario(
            nombre=nombre,
            email=email,
            contraseña=contraseña  
        )
        usuario.save()

        return render(request, "libros/registro.html", {
            'mostrar_encuesta': True,
            'nombre_usuario': nombre,  
        })

    return render(request, "libros/registro.html")




from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from .models import Usuario

def login_view(request):
    print("CSRF token POST:", request.POST.get('csrfmiddlewaretoken'))
    ...


def login_view(request):
    if request.method == 'POST':
        nombre = request.POST.get('usuario')
        contraseña = request.POST.get('password')
        print(f"Intentando login con usuario={nombre} y contraseña={contraseña}")

        try:
            usuario = Usuario.objects.get(nombre=nombre)
            print(f"Usuario encontrado: {usuario}")
        except Usuario.DoesNotExist:
            messages.error(request, 'Usuario o contraseña incorrectos')
            print("Usuario no encontrado")
            return render(request, 'libros/login.html')

        if usuario.contraseña == contraseña:
            print("Contraseña correcta")
            request.session['usuario_id'] = usuario.id
            request.session['usuario_nombre'] = usuario.nombre
            messages.success(request, f"Bienvenido {usuario.nombre}")
            return redirect('inicio')
        else:
            print("Contraseña incorrecta")
            messages.error(request, 'Usuario o contraseña incorrectos')
            return render(request, 'libros/login.html')

    return render(request, 'libros/login.html')





