# Generated by Django 5.0.9 on 2024-09-13 08:45

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("numerique_gouv", "0043_alter_numeriquebasepage_body"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="ProductTargetAudience",
            new_name="TargetAudience",
        ),
    ]
