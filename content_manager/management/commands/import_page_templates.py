from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        """
        Import template pages
        """

        # page_importer = ImportPages()
        # page_importer.import_pages()
