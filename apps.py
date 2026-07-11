from django.apps import AppConfig


class ArtistryConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "artistry"
    dpy_package = "artistry.package"
