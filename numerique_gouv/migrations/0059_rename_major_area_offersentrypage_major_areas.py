# Generated by Django 5.0.9 on 2024-10-04 13:32

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("numerique_gouv", "0058_remove_hubpages_dinum_tags_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="offersentrypage",
            old_name="major_area",
            new_name="major_areas",
        ),
    ]