from django.apps import AppConfig


class OverridesConfig(AppConfig):
    """
    Overrides of sites_conformes management commands.

    Listed before the sites_conformes apps in INSTALLED_APPS so that its commands take precedence.
    """

    name = "numerique_gouv.overrides"
    label = "numerique_gouv_overrides"
