from django.db import migrations

from numerique_gouv.content_page_conversion import convert_content_pages


class Migration(migrations.Migration):
    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
        ("content_manager", "0062_catalogindexpage_preview_image_and_more"),
        ("numerique_gouv", "0096_fix_highlight_cards_labels"),
        ("wagtailcore", "0095_groupsitepermission"),
        ("wagtailsearch", "0009_remove_ngram_autocomplete"),
    ]

    operations = [
        # Legacy ContentPage pages become NumeriquePage pages (same ids, URLs and revisions)
        migrations.RunPython(convert_content_pages, migrations.RunPython.noop),
    ]
