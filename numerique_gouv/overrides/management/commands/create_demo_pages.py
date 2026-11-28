from django.contrib.staticfiles import finders
from sites_conformes.core.management.commands.create_demo_pages import Command as BaseCommand
from sites_conformes.core.utils import import_image
from wagtail.images import get_image_model


class Command(BaseCommand):
    # Workaround: upstream joins the image path with BASE_DIR, which breaks when sites_conformes
    # is installed as a package. Remove once https://github.com/numerique-gouv/sites-conformes/pull/709
    # is released.
    def get_or_import_image(self, path: str, title: str):
        image = get_image_model().objects.filter(title=title).first()
        if image:
            return image

        full_path = finders.find(path.removeprefix("sites_conformes/static/"))
        if not full_path:
            raise FileNotFoundError(path)
        return import_image(full_path, title)
