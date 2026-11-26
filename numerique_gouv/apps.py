from django.apps import AppConfig


class NumeriqueGouvConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "numerique_gouv"

    def ready(self):
        from content_manager.models import ContentPage

        # numerique.gouv.fr uses NumeriquePage instead: hide ContentPage from the admin page creation.
        # The starter/demo commands still create ContentPage pages programmatically on new sites.
        ContentPage.is_creatable = False
