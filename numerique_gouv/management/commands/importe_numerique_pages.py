import os
import re
import frontmatter
import pytz
from django.core.management.base import BaseCommand
from slugify import slugify
from wagtail.documents.models import Document
from wagtail.models import Site
from wagtail.rich_text import RichText
from blog.models import BlogEntryPage, BlogIndexPage, Category
from content_manager.models import ContentPage
from content_manager.utils import import_image
from datetime import datetime
from wagtail.images.models import Image


def update_documents_links(text):
    pattern = r"/uploads/(.*\.pdf)"
    # Find all occurrences of the old link in text
    old_links = re.findall(pattern, text)
    # For each old link found
    for old_link in old_links:
        # Extract the document name from the old link
        document_name = old_link.split("/")[-1]
        # Query the Wagtail Document model to get the document id
        document = Document.objects.filter(title=document_name).first()
        if document:
            document_id = document.id
            # Construct the new link
            new_link = f"/documents/{document_id}/{document_name}"
            old_link_ling = f"/uploads/{old_link}"
            # Replace the old link with the new link in text
            text = re.sub(old_link_ling, new_link, text)

    return text


def remove_html_tags(text):
    tags = re.compile("<(/?[bi])>")
    text_without_html = re.sub(tags, "", text)
    text_without_markdown = re.sub(r"\{:(.*?)\}", "", text_without_html)
    return text_without_markdown


def remove_frontmatter(content_with_frontmatter):
    parsed = frontmatter.loads(content_with_frontmatter)
    return parsed.content


def import_tags(new_page, tags):
    for tag in tags:
        new_page.tags.add(tag)
        new_page.save()


def import_page_categories(new_page, categories):
    for category in categories:
        page_category = Category.objects.filter(name=category).first()
        if not page_category:
            page_category = Category.objects.create(name=category, slug=slugify(category))

        new_page.blog_categories.add(page_category)
        new_page.save()


def import_content_images(text):
    pattern = r"/uploads/(.*\.(png|jpeg|jpg))"
    image_links = re.findall(pattern, text)
    for image_link in image_links:
        file_name = image_link[0]
        extension = image_link[1]
        path = "numerique_files/_uploads/" + file_name
        parts = path.split('/')
        file_name_with_extension = parts[-1]
        file_parts = file_name_with_extension.split('.')
        title = file_parts[0]

        image = Image.objects.filter(title=title).first()
        if not image:
            image = import_image(path, title)
        image.tags.add('ancienne version')
        image.save()

        if image:
            old_path = "/uploads/" + file_name
            new_link = f"/medias/images/{image.title}.original.{extension}"
            text = re.sub(old_path, new_link, text)

    return text


class Command(BaseCommand):
    help = "Closes the specified poll for voting"

    def handle(self, *args, **options):
        categories = ["publications", "communiques", "actualites"]
        for category in categories:
            # Get a list of all files in the 'numerique_files' directory
            files = os.listdir("numerique_gouv/numerique_files/_" + category)

            for file_name in files:
                file_path = os.path.join("numerique_gouv/numerique_files/_" + category, file_name)

                with open(file_path, "r") as file:
                    content = file.read()
                    # try to load the file as frontmatter
                    try:
                        headers = frontmatter.loads(content)
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"Error while loading frontmatter of {file_name}: {e}"))
                        continue
                    content_without_frontmatter = remove_frontmatter(content)

                title = headers["title"][:255]
                tags = headers.get("tags", [])
                page_categories = headers.get("categories", [])
                tags.append("DINUM")

                # Pour les apostrophes la versions actuelle de numerique enlève la lettre d'avant aussi, slugify non
                slug = slugify(title)
                body = []

                if "chapeau-text" in headers.keys():
                    body.append(("paragraph", RichText(headers["chapeau-text"])))

                if "date" in headers.keys():
                    created_at = headers["date"]
                else:
                    tz = pytz.timezone("Europe/Paris")
                    created_at = datetime.now(tz)

                if category == "actualites" or category == "communiques":
                    # N'importe pas les actus avant 2020
                    reference_date = datetime(2020, 1, 1)
                    tz = pytz.timezone("Europe/Paris")
                    reference_date = tz.localize(reference_date)
                    try:
                        if isinstance(created_at, str):
                            try:
                                created_at = datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S")
                            except ValueError:
                                print(
                                    "La chaîne de caractères ne correspond pas au format attendu (YYYY-MM-DD HH:MM:SS)")
                        created_at = tz.localize(created_at)
                        if created_at < reference_date:
                            continue
                    except Exception as e:
                        ""

                try:
                    content_without_frontmatter = update_documents_links(content_without_frontmatter)
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error while updating documents links of {file_name}: {e}"))
                    continue

                try:
                    content_without_frontmatter = import_content_images(content_without_frontmatter)
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error while importing images of {file_name}: {e}"))
                    continue

                content_without_frontmatter = remove_html_tags(content_without_frontmatter)

                body.append(("markdown", content_without_frontmatter))

                new_page = self.create_page(
                    slug=slug,
                    title=title,
                    body=body,
                    category=category.capitalize(),
                    created_at=str(created_at),
                    tags=tags,
                    page_categories=page_categories,
                )

                self.import_existing_image(headers, category, new_page, file_name)

    def create_page(self, slug: str, title: str, body: list, category: str, created_at: str, tags: list,
                    page_categories):
        # Don't replace a manually created page
        already_exists = ContentPage.objects.filter(slug=slug).first()
        category = category.lower()
        if already_exists:
            return

        home_page = Site.objects.filter(is_default_site=True).first().root_page

        if category == "actualites" or category == 'communiques':

            category_page = BlogIndexPage.objects.filter(slug=category).first()
            if not category_page:
                category_page = home_page.add_child(
                    instance=BlogIndexPage(title=category, body=[], slug=category, show_in_menus=True)
                )

            new_page = BlogEntryPage.objects.filter(slug=slug).first()
            if not new_page:
                new_page = category_page.add_child(
                    instance=BlogEntryPage(title=title, body=body, slug=slug, show_in_menus=False, date=created_at)
                )

            import_page_categories(new_page, page_categories)

        else:
            # create category page if not exist
            category_page = ContentPage.objects.filter(slug=category).first()
            if not category_page:
                category_page = home_page.add_child(
                    instance=ContentPage(title=category, body=[], slug=category, show_in_menus=True)
                )

            new_page = ContentPage.objects.filter(slug=slug).first()
            if not new_page:
                new_page = category_page.add_child(
                    instance=ContentPage(
                        title=title, body=body, slug=slug, show_in_menus=False, last_published_at=created_at
                    )
                )

        import_tags(new_page, tags)

        self.stdout.write(self.style.SUCCESS(f"Page {slug} created with id {new_page.id}"))
        return new_page

    def import_existing_image(self, headers, category: str, new_page, file_name):
        header_image = headers.get("une-ou-diaporama", [])
        if header_image:
            try:
                path = "numerique_gouv/numerique_files" + header_image[0]["image"]
                path = path.replace("uploads", "_uploads")
                parts = path.split('/')
                file_name_with_extension = parts[-1]
                file_parts = file_name_with_extension.split('.')
                title = file_parts[0]

                image = import_image(path, title)
                image.tags.add(category)
                image.tags.add('ancienne version')
                image.save()
                new_page.header_image = image
                new_page.save()
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error while importing header image of {file_name}: {e}"))
                return
