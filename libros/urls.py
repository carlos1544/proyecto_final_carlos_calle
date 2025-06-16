from django.urls import path
from .views import lista_libros
from . import views
from django.contrib.auth.views import LogoutView


urlpatterns = [
    path('', lista_libros, name='lista_libros'),  
    path('recomendador/', views.recomendar_view, name='recomendador'),
    path('libros/', views.lista_libros, name='lista_libros'),
    path('login/', views.login_view, name='login'),
    path('registro/', views.registro, name='registro'),
    path('perfil/', views.perfil, name='perfil'),
    path('explorar-libros/', views.explorar_libros, name='explorar_libros'),
    path('explorar-IA/', views.explorar_ia, name='explorar_ia'),
    path('historial/', views.historial, name='historial'),
    path('favoritos/', views.favoritos, name='favoritos'), 
    path('configuracion/', views.configuracion, name='configuracion'), 
    path('index/', views.inicio, name='inicio'),
    path('logout/', views.logout_view, name='logout'),

]
