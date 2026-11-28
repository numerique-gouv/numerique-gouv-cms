from django.db import migrations

from numerique_gouv.services.legacy_blocks_cleanup import clean_all


class Migration(migrations.Migration):
    dependencies = [
        ("numerique_gouv", "0099_delete_sitemappage"),
        ("sites_conformes_core", "0085_move_centered_image_alt_to_image_block"),
        ("wagtailcore", "__latest__"),
    ]

    operations = [
        # Legacy block values dropped by the current block definitions would be lost when saving a page
        migrations.RunPython(clean_all, migrations.RunPython.noop),
    ]
