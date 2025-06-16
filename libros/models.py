from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.hashers import make_password
from django.utils.timezone import now
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.utils.timezone import now
from django.db import models

from django.db import models

class UsuarioManager(models.Manager):
    def create_user(self, nombre, email, contraseña=None):
        usuario = self.model(
            nombre=nombre,
            email=email,
            contraseña=contraseña,  
        )
        usuario.save(using=self._db)
        return usuario

class Usuario(models.Model):
    nombre = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    contraseña = models.CharField(max_length=128)  
    fecha_creacion = models.DateTimeField(default=now)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nombre']

    class Meta:
        db_table = 'Usuario'
        managed = False

    def __str__(self):
        return self.nombre

    def has_perm(self, perm, obj=None):
        """El usuario tiene un permiso específico."""
        return True

    def has_module_perms(self, app_label):
        """El usuario tiene permisos para ver la aplicación especificada."""
        return True

    @property
    def is_staff(self):
        """El usuario es parte del personal administrativo."""
        return False

    @property
    def is_superuser(self):
        """El usuario tiene permisos de superusuario."""
        return False

    @property
    def is_active(self):
        """El usuario está activo."""
        return True

    @property
    def is_authenticated(self):
        """El usuario está autenticado."""
        return True

    @property
    def is_anonymous(self):
        """El usuario no está autenticado."""
        return False

#login
from django.db import models
from django.utils.timezone import now

class UsuarioLogin(models.Model):
    email = models.EmailField(unique=True, verbose_name="Correo Electrónico")
    contraseña = models.CharField(max_length=128, verbose_name="Contraseña")
    fecha_creacion = models.DateTimeField(default=now, verbose_name="Fecha de Creación")

    class Meta:
        db_table = 'Usuario'
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"

    def __str__(self):
        return self.email

    def verificar_contraseña(self, contraseña):
        """Compara la contraseña ingresada con la almacenada."""
        return self.contraseña == contraseña


class Libro(models.Model):
    titulo = models.CharField(max_length=200)
    autor = models.CharField(max_length=100)
    genero = models.CharField(max_length=255, blank=True, null=True)
    descripcion = models.CharField(max_length=500, blank=True, null=True)
    portada = models.CharField(max_length=500, blank=True, null=True) 

    def __str__(self):
        return self.titulo

    class Meta:
        db_table = 'Libro'
        managed = False








