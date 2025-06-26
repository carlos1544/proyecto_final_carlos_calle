from django.apps import AppConfig

class LibrosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'libros'

    def ready(self):
        # Importar aquí dentro para evitar el error
        from django.contrib.auth.models import update_last_login
        from django.contrib.auth.signals import user_logged_in

        # Desconectar la señal que actualiza `last_login`
        user_logged_in.disconnect(update_last_login)
