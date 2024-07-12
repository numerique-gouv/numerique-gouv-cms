import hashlib
import os

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from git import Repo
from wagtail.documents.models import Document


class Command(BaseCommand):
    # def add_arguments(self, parser):
    #     parser.add_argument("files", nargs="+", type=int)

    def handle(self, *args, **options):
        path_to_clone = "numerique_gouv/numerique_files"
        uploads_folder = path_to_clone + "/_uploads"

        if not os.path.isdir(path_to_clone):
            git_url = "https://github.com/numerique-gouv/numerique.gouv.fr"
            Repo.clone_from(git_url, path_to_clone)

        # Get a list of all files in the 'numerique_files' directory
        files = os.listdir(uploads_folder)
        # print(files)
        # Loop through each file
        for file_name in files:
            _, extension = os.path.splitext(file_name)
            if not extension.lower() == ".pdf":
                continue

            file_path = os.path.join(uploads_folder, file_name)

            # search if document title exists

            if not Document.objects.filter(title=file_name).exists():
                file = import_document(
                    full_path=file_path,
                    title=file_name,
                )
                if file:
                    self.stdout.write(self.style.SUCCESS(f"Successfully imported {file_name}"))
                else:
                    self.stdout.write(self.style.ERROR(f"Error while importing {file_name}"))

            else:
                self.stdout.write(self.style.ERROR(f"Error document already exists {file_name}"))


def import_document(full_path: str, title: str) -> Document:
    """
    Import a document to the Wagtail documents based on its full path and return it.
    """
    with open(full_path, "rb") as doc_file:
        file_content = doc_file.read()
        file_size = os.path.getsize(full_path)
        file_hash = hashlib.md5(file_content).hexdigest()
        document = Document(
            file=ContentFile(file_content, name=title),
            title=title,
            file_size=file_size,
            file_hash=file_hash,
        )
        document.save()
        document.tags.add("ancienne version")
        return document
