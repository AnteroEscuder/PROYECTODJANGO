from django.apps import AppConfig


class TiendaConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "tienda"

    def ready(self):
        from .models import crear_grupos
        from django.db.models.signals import post_migrate
        post_migrate.connect(crear_grupos, sender=self)
