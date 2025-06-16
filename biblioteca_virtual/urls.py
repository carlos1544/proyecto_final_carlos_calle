from django.contrib import admin
from django.urls import path, include
from libros import views 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('libros.urls')),  

]
