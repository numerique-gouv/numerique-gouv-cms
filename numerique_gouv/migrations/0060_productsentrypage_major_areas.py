# Generated by Django 5.0.9 on 2024-10-04 13:34

import modelcluster.fields
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("numerique_gouv", "0059_rename_major_area_offersentrypage_major_areas"),
    ]

    operations = [
        migrations.AddField(
            model_name="productsentrypage",
            name="major_areas",
            field=modelcluster.fields.ParentalManyToManyField(
                blank=True, to="numerique_gouv.majorarea", verbose_name="Dinum Tags"
            ),
        ),
    ]
