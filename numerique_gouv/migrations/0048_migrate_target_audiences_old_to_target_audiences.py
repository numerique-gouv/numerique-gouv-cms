# Generated by Django <version> on <date>
from django.db import migrations


def create_target_audience_if_not_exists(apps, schema_editor):
    OfferTargetAudience = apps.get_model("numerique_gouv", "OfferTargetAudience")
    TargetAudience = apps.get_model("numerique_gouv", "TargetAudience")

    for offer_target_audience in OfferTargetAudience.objects.all():
        if not TargetAudience.objects.filter(slug=offer_target_audience.slug).exists():
            TargetAudience.objects.create(
                name=offer_target_audience.name,
                slug=offer_target_audience.slug,
                color=offer_target_audience.color,
            )


def migrate_target_audiences_old_to_target_audiences(apps, schema_editor):
    TargetAudience = apps.get_model("numerique_gouv", "TargetAudience")
    OffersEntryPage = apps.get_model("numerique_gouv", "OffersEntryPage")

    for offer_page in OffersEntryPage.objects.all():
        for old_audience in offer_page.target_audiences_old.all():
            try:
                new_audience = TargetAudience.objects.get(slug=old_audience.slug)
                if offer_page.target_audiences.filter(slug=new_audience.slug).exists():
                    continue
                offer_page.target_audiences.add(new_audience)
            except TargetAudience.DoesNotExist:
                pass
        offer_page.save()


class Migration(migrations.Migration):
    dependencies = [
        ("numerique_gouv", "0046_rename_target_audiences_offersentrypage_target_audiences_old"),
    ]

    operations = [
        # migrations.RunPython(create_target_audience_if_not_exists),
        # migrations.RunPython(migrate_target_audiences_old_to_target_audiences),
    ]
