# Generated by Django 5.0.9 on 2024-11-17 09:16

import django.db.models.deletion
import modelcluster.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("blog", "0051_alter_blogentrypage_body"),
        ("numerique_gouv", "0077_remove_numeriqueblogentrypage_dinum_tags_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="hubpages",
            name="dinum_tag",
        ),
        migrations.RemoveField(
            model_name="numeriqueeventpage",
            name="dinum_tags",
        ),
        migrations.AddField(
            model_name="hubpages",
            name="organization",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="blog.organization",
                verbose_name="Organization",
            ),
        ),
        migrations.AddField(
            model_name="numeriqueeventpage",
            name="organizations",
            field=modelcluster.fields.ParentalManyToManyField(
                blank=True, to="blog.organization", verbose_name="Organizations"
            ),
        ),
        migrations.AlterField(
            model_name="hubpages",
            name="content_source",
            field=models.CharField(
                choices=[
                    ("major_area", "Major Areas of Actions"),
                    ("organization", "Organizations"),
                    ("page_tag", "Page tags"),
                    ("target_audience", "Target Audiences"),
                ],
                max_length=20,
                verbose_name="Content Source",
            ),
        ),
        migrations.AlterField(
            model_name="offersentrypage",
            name="major_areas",
            field=modelcluster.fields.ParentalManyToManyField(
                blank=True, to="numerique_gouv.majorarea", verbose_name="Major areas"
            ),
        ),
        migrations.AlterField(
            model_name="productsentrypage",
            name="major_areas",
            field=modelcluster.fields.ParentalManyToManyField(
                blank=True, to="numerique_gouv.majorarea", verbose_name="Major areas"
            ),
        ),
    ]