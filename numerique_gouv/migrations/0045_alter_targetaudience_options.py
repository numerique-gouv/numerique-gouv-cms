# Generated by Django 5.0.9 on 2024-09-13 09:04

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("numerique_gouv", "0044_rename_producttargetaudience_to_targetaudience"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="targetaudience",
            options={"verbose_name": "Target Audience"},
        ),
    ]