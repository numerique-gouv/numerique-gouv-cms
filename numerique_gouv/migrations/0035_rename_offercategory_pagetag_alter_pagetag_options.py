# Generated by Django 5.0.8 on 2024-08-30 13:04

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("numerique_gouv", "0034_delete_productcategory"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="OfferCategory",
            new_name="PageTag",
        ),
        migrations.AlterModelOptions(
            name="pagetag",
            options={"verbose_name": "Tag"},
        ),
    ]
