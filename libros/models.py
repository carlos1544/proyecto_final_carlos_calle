from django.db import models
from django.db import models
from django.utils.timezone import now
from django.db import models


from django.utils.timezone import now
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils.timezone import now
from django.db import models

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils.timezone import now
from django.db import models

class UsuarioManager(BaseUserManager):
    def create_user(self, nombre, email=None, password=None):
        if not nombre:
            raise ValueError('El nombre es obligatorio')
        usuario = self.model(nombre=nombre, email=email)
        usuario.set_password(password)
        usuario.save(using=self._db)
        return usuario

    def create_superuser(self, nombre, email=None, password=None):
        usuario = self.create_user(nombre, email, password)
        usuario.is_staff = True
        usuario.is_superuser = True
        usuario.save(using=self._db)
        return usuario

class Usuario(AbstractBaseUser, PermissionsMixin):
    nombre = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    fecha_creacion = models.DateTimeField(default=now)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    objects = UsuarioManager()

    USERNAME_FIELD = 'nombre'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.nombre
    
class Libro(models.Model):
    titulo = models.CharField(max_length=200)
    autor = models.CharField(max_length=100)
    genero = models.CharField(max_length=255, blank=True, null=True)
    descripcion = models.CharField(max_length=500, blank=True, null=True)
    portada = models.CharField(max_length=500, blank=True, null=True)
    url_para_leer = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.titulo

    class Meta:
        db_table = 'Libro'
        managed = False



class PreferenciaUsuario(models.Model):
    usuario = models.OneToOneField('Usuario', on_delete=models.CASCADE, db_column='usuario_id')
    generos = models.JSONField()
    tipo_final = models.CharField(max_length=50)
    tipo_libro = models.CharField(max_length=50)

    def __str__(self):
        return f"Preferencias de {self.usuario.nombre}"
 



class SeleccionLibro(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    libro = models.ForeignKey(Libro, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False  # Para que Django no intente crearla ni modificarla
        db_table = 'SeleccionLibro'


class Favorito(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    libro = models.ForeignKey('Libro', on_delete=models.CASCADE)
    fecha_agregado = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('usuario', 'libro')  # Para evitar duplicados


class RecomendacionIA(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    libro = models.ForeignKey('Libro', on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario.nombre} - {self.libro.titulo}"
from django.conf import settings
class LibroUsuario(models.Model):
    ESTADOS = [
        ('leido', 'Leído'),
        ('por_leer', 'Por leer'),
    ]
    
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    libro = models.ForeignKey(Libro, on_delete=models.CASCADE)
    estado = models.CharField(max_length=10, choices=[('leido', 'Leído'), ('por_leer', 'Por leer')], null=True, blank=True)
