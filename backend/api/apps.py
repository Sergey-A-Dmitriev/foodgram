from django.apps import AppConfig


class ApiConfig(AppConfig):
    """Приложение REST API."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'
    verbose_name = 'REST API'
