# Generated by Django 5.0.8 on 2024-08-30 20:03

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("numerique_gouv", "0035_rename_offercategory_pagetag_alter_pagetag_options"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="pagetag",
            options={"verbose_name": "Page tag"},
        ),
        migrations.AddField(
            model_name="productsentrypage",
            name="image_alt",
            field=models.CharField(blank=True, max_length=255, verbose_name="Image alt"),
        ),
        migrations.AlterField(
            model_name="productsentrypage",
            name="target_audience",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="numerique_gouv.producttargetaudience",
                verbose_name="Target Audience",
            ),
        ),
    ]