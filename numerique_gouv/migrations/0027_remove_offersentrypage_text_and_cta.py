# Generated by Django 5.0.8 on 2024-08-25 21:12

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("numerique_gouv", "0026_remove_offersentrypage_introductory_text_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="offersentrypage",
            name="text_and_cta",
        ),
    ]
