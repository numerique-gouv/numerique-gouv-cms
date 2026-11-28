"""
Clean the legacy StreamField values that the Sites Conformes block definitions no longer know.

Wagtail silently drops unknown struct fields when a page is loaded in the editor, so saving such a page
would lose their content. Two cases remain in the numerique.gouv.fr content:

- the top-level "alt" of the "image" block (CenteredImageBlock): it is moved into the ImageBlock value, in the
  same format as the sites_conformes_core 0085 migration. That migration only detected values having an
  "image_ratio" key, so older values (without it) were skipped.
- the obsolete "cta_label" and "cta_url" fields of the "text_cta" block: they were no longer rendered since every
  affected block has CTA buttons, so they are simply removed.
"""

import json

from django.db.models import Q, TextField
from django.db.models.functions import Cast
from wagtail.fields import StreamField

BATCH_SIZE = 100

# Raw-text markers used to skip, in SQL, the rows that cannot contain a legacy value
ALT_MARKER = '"alt"'
CTA_MARKER = "cta_label"

OBSOLETE_CTA_FIELDS = ("cta_label", "cta_url")


def _clean_image_value(value: dict) -> bool:
    if "alt" not in value:
        return False

    alt = value.pop("alt") or ""
    image = value.get("image")
    if image is None or isinstance(image, int):
        # An empty legacy alt was rendered as alt="", hence decorative
        value["image"] = {"image": image, "decorative": not alt, "alt_text": alt}
    elif alt and isinstance(image, dict) and not image.get("alt_text"):
        image["alt_text"] = alt
        image["decorative"] = False
    return True


def _clean_text_cta_value(value: dict) -> bool:
    updated = False
    for field in OBSOLETE_CTA_FIELDS:
        if field in value:
            del value[field]
            updated = True
    return updated


def clean_legacy_blocks(data, clean_cta: bool = True) -> bool:
    """
    Recursively walk raw StreamField data and clean the legacy values, in place.
    Returns True if data was modified.
    """
    updated = False

    if isinstance(data, list):
        for item in data:
            updated = clean_legacy_blocks(item, clean_cta) or updated

    elif isinstance(data, dict):
        block_type = data.get("type")
        value = data.get("value")
        if "value" in data and isinstance(value, dict):
            if block_type == "image":
                updated = _clean_image_value(value) or updated
            elif block_type == "text_cta" and clean_cta:
                updated = _clean_text_cta_value(value) or updated

        for child in data.values():
            if isinstance(child, (list, dict)):
                updated = clean_legacy_blocks(child, clean_cta) or updated

    return updated


def _clean_revision_content(content: dict, clean_cta: bool) -> bool:
    # Revisions store StreamFields as JSON strings
    updated = False
    for key, value in content.items():
        if not (isinstance(value, str) and value.startswith("[")):
            continue
        try:
            stream_data = json.loads(value)
        except ValueError:
            continue
        if clean_legacy_blocks(stream_data, clean_cta):
            content[key] = json.dumps(stream_data)
            updated = True
    return updated


def clean_pages(apps) -> None:
    for model in apps.get_models():
        if model._meta.proxy:
            continue
        # Only the fields declared on the model itself, so that multi-table parents are processed once
        stream_fields = [f.name for f in model._meta.local_concrete_fields if isinstance(f, StreamField)]
        if not stream_fields:
            continue

        candidates = Q()
        for field_name in stream_fields:
            candidates |= Q(**{f"legacy_search_{field_name}__contains": ALT_MARKER})
            candidates |= Q(**{f"legacy_search_{field_name}__contains": CTA_MARKER})
        queryset = (
            model._base_manager.annotate(
                **{f"legacy_search_{field_name}": Cast(field_name, TextField()) for field_name in stream_fields}
            )
            .filter(candidates)
            .only("pk", *stream_fields)
        )

        for instance in queryset.iterator(chunk_size=BATCH_SIZE):
            updated_fields = []
            for field_name in stream_fields:
                raw_data = list(getattr(instance, field_name).raw_data)
                if clean_legacy_blocks(raw_data):
                    setattr(instance, field_name, raw_data)
                    updated_fields.append(field_name)

            if updated_fields:
                instance.save(update_fields=updated_fields)


def clean_revisions(apps) -> None:
    """
    Move the legacy image alt in every revision, so that restoring an old revision keeps it.
    The obsolete CTA fields are only removed from the latest revisions, which are the ones loaded by the editor:
    rewriting the whole history for fields that are dropped anyway would be useless.
    """
    Page = apps.get_model("wagtailcore", "Page")
    Revision = apps.get_model("wagtailcore", "Revision")

    latest_ids = set(Page.objects.exclude(latest_revision=None).values_list("latest_revision_id", flat=True))

    revisions = (
        Revision.objects.annotate(content_text=Cast("content", TextField()))
        .filter(Q(content_text__contains='\\"alt\\"') | Q(pk__in=latest_ids, content_text__contains=CTA_MARKER))
        .values_list("pk", "content")
    )

    for pk, content in revisions.iterator(chunk_size=BATCH_SIZE):
        if _clean_revision_content(content, clean_cta=pk in latest_ids):
            Revision.objects.filter(pk=pk).update(content=content)


def clean_all(apps, schema_editor=None) -> None:
    clean_pages(apps)
    clean_revisions(apps)
