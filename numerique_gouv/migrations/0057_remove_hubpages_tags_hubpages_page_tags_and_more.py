# Generated by Django 5.0.9 on 2024-09-20 09:53

import modelcluster.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("numerique_gouv", "0056_hubpages_introduction_text_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="hubpages",
            old_name="tags",
            new_name="page_tags",
        ),
        migrations.AlterField(
            model_name="hubpages",
            name="content_source",
            field=models.CharField(
                choices=[
                    ("major_areas", "Major Areas of Actions"),
                    ("dinum_tags", "Dinum Tags"),
                    ("page_tags", "Page tags"),
                    ("target_audiences", "Target Audiences"),
                ],
                max_length=20,
                verbose_name="Content Source",
            ),
        ),
    ]