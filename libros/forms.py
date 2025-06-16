# libros/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from libros.models import Usuario

class RegistroForm(UserCreationForm):
    nombre_completo = forms.CharField(max_length=150, required=True, label="Nombre completo")
    email = forms.EmailField(required=True, label="Correo electrónico")

    class Meta:
        model = Usuario
        fields = ['username', 'email', 'nombre_completo', 'password1', 'password2']
