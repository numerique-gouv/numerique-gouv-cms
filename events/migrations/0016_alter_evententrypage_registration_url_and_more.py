# Generated by Django 5.2.1 on 2025-05-13 11:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("events", "0015_alter_evententrypage_body_alter_eventsindexpage_body"),
    ]

    operations = [
        migrations.AlterField(
            model_name="evententrypage",
            name="registration_url",
            field=models.URLField(
                blank=True,
                help_text="Max length: 2000 characters.",
                max_length=2000,
                null=True,
                verbose_name="Registration URL",
            ),
        ),
        migrations.AlterField(
            model_name="evententrypage",
            name="source_url",
            field=models.URLField(
                blank=True,
                help_text="For imported pages, to allow updates. Max length: 2000 characters.",
                max_length=2000,
                null=True,
                verbose_name="Source URL",
            ),
        ),
        migrations.AlterField(
            model_name="eventsindexpage",
            name="source_url",
            field=models.URLField(
                blank=True,
                help_text="For imported pages, to allow updates. Max length: 2000 characters.",
                max_length=2000,
                null=True,
                verbose_name="Source URL",
            ),
        ),
    ]
