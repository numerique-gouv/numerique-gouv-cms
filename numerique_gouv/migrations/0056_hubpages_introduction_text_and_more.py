# Generated by Django 5.0.9 on 2024-09-20 09:24

import modelcluster.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("numerique_gouv", "0055_rename_tags_productsentrypage_page_tags_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="hubpages",
            name="introduction_text",
            field=models.TextField(blank=True, verbose_name="Introduction text"),
        ),
        migrations.AlterField(
            model_name="offersentrypage",
            name="page_tags",
            field=modelcluster.fields.ParentalManyToManyField(
                blank=True, to="numerique_gouv.pagetag", verbose_name="Page tags"
            ),
        ),
    ]
