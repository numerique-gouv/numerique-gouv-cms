import os
import re
from datetime import datetime

import frontmatter
import pytz
from django.core.management.base import BaseCommand
from slugify import slugify
from wagtail.documents.models import Document
from wagtail.models import Site
from wagtail.rich_text import RichText

from blog.models import BlogEntryPage, BlogIndexPage
from content_manager.models import ContentPage


def update_documents_links(text):
    # Define the regular expression pattern for the old link
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
    return re.sub(tags, "", text)


def remove_frontmatter(content_with_frontmatter):
    parsed = frontmatter.loads(content_with_frontmatter)
    return parsed.content


class Command(BaseCommand):
    help = "Closes the specified poll for voting"

    def handle(self, *args, **options):
        categories = ["publications", "communiques", "actualites"]
        # categories = ["publications"]
        for category in categories:
            # Get a list of all files in the 'numerique_files' directory
            files = os.listdir("numerique_files/_" + category)

            for file_name in files:
                file_path = os.path.join("numerique_files/_" + category, file_name)

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

                try:
                    content_without_frontmatter = update_documents_links(content_without_frontmatter)
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error while updating documents links of {file_name}: {e}"))
                    continue

                content_without_frontmatter = remove_html_tags(content_without_frontmatter)

                body.append(("markdown", content_without_frontmatter))

                self.create_page(
                    slug=slug,
                    title=title,
                    body=body,
                    category=category.capitalize(),
                    created_at=str(created_at),
                    tags=tags,
                )

    def create_page(self, slug: str, title: str, body: list, category: str, created_at: str, tags: list):
        # Don't replace a manually created page
        already_exists = ContentPage.objects.filter(slug=slug).first()
        category = category.lower()
        if already_exists:
            return

        home_page = Site.objects.filter(is_default_site=True).first().root_page

        if category == "actualites":
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

        for tag in tags:
            new_page.tags.add(tag)
            new_page.save()

        self.stdout.write(self.style.SUCCESS(f"Page {slug} created with id {new_page.id}"))
