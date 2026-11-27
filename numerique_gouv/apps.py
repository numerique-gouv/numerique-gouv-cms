from django.apps import AppConfig


class NumeriqueGouvConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "numerique_gouv"

    def ready(self):
        from sites_conformes.blog.models import BlogEntryPage, BlogIndexPage
        from sites_conformes.events.models import EventEntryPage, EventsIndexPage

        from numerique_gouv.blocks import STREAMFIELD_NUMERIQUE_BLOCKS
        from numerique_gouv.streamfield import extend_stream_field

        # Make the numerique.gouv.fr blocks available in the Sites Conformes blog and events pages
        for model in [BlogIndexPage, BlogEntryPage, EventsIndexPage, EventEntryPage]:
            extend_stream_field(model, "body", STREAMFIELD_NUMERIQUE_BLOCKS)
