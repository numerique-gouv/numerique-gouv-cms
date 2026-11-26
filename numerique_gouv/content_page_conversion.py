"""
Convert the remaining content_manager.ContentPage pages into numerique_gouv.NumeriquePage pages.

ContentPage cannot be created under the numerique.gouv.fr home page anymore, but a few legacy pages
remain (legal notice, accessibility statement…). Both models share exactly the same columns, so the
conversion keeps the page ids, URLs, revisions and history: only the type-specific rows and the
content type references change.
"""

import logging

from django.db import connection, transaction

logger = logging.getLogger(__name__)


def convert_content_pages(apps, schema_editor=None) -> list[int]:
    """
    Convert every ContentPage into a NumeriquePage and return the converted page ids.

    Works both with the historical models of a migration and with the real app registry.
    PostgreSQL only (uses jsonb_set).
    """
    ContentType = apps.get_model("contenttypes", "ContentType")
    ContentPage = apps.get_model("content_manager", "ContentPage")
    NumeriqueBasePage = apps.get_model("numerique_gouv", "NumeriqueBasePage")
    NumeriquePage = apps.get_model("numerique_gouv", "NumeriquePage")

    old_ct = ContentType.objects.filter(app_label="content_manager", model="contentpage").first()
    page_ids = list(ContentPage.objects.values_list("page_ptr_id", flat=True))
    if not old_ct or not page_ids:
        return []

    new_ct, _created = ContentType.objects.get_or_create(app_label="numerique_gouv", model="numeriquepage")
    str_ids = [str(page_id) for page_id in page_ids]

    columns = ", ".join(f'"{field.column}"' for field in ContentPage._meta.local_concrete_fields)
    content_page_table = ContentPage._meta.db_table
    tag_table = apps.get_model("content_manager", "TagContentPage")._meta.db_table

    with transaction.atomic(), connection.cursor() as cursor:
        # Type-specific rows: same columns in both tables
        cursor.execute(
            f"INSERT INTO {NumeriqueBasePage._meta.db_table} ({columns}) "
            f"SELECT {columns} FROM {content_page_table} WHERE page_ptr_id = ANY(%s)",
            [page_ids],
        )
        cursor.execute(
            f"INSERT INTO {NumeriquePage._meta.db_table} (numeriquebasepage_ptr_id) "
            f"SELECT page_ptr_id FROM {content_page_table} WHERE page_ptr_id = ANY(%s)",
            [page_ids],
        )

        # Content type references
        cursor.execute(
            "UPDATE wagtailcore_page SET content_type_id = %s WHERE id = ANY(%s)",
            [new_ct.id, page_ids],
        )
        cursor.execute(
            "UPDATE wagtailcore_revision "
            "SET content_type_id = %s, content = jsonb_set(content, '{content_type}', to_jsonb(%s)) "
            "WHERE content_type_id = %s AND object_id = ANY(%s)",
            [new_ct.id, new_ct.id, old_ct.id, str_ids],
        )
        cursor.execute(
            "UPDATE wagtailcore_pagelogentry SET content_type_id = %s "
            "WHERE content_type_id = %s AND page_id = ANY(%s)",
            [new_ct.id, old_ct.id, page_ids],
        )
        cursor.execute(
            "UPDATE wagtailcore_referenceindex SET content_type_id = %s "
            "WHERE content_type_id = %s AND object_id = ANY(%s)",
            [new_ct.id, old_ct.id, str_ids],
        )
        cursor.execute(
            "UPDATE wagtailcore_referenceindex SET to_content_type_id = %s "
            "WHERE to_content_type_id = %s AND to_object_id = ANY(%s)",
            [new_ct.id, old_ct.id, str_ids],
        )
        cursor.execute(
            "UPDATE wagtailsearch_indexentry SET content_type_id = %s "
            "WHERE content_type_id = %s AND object_id = ANY(%s)",
            [new_ct.id, old_ct.id, str_ids],
        )
        cursor.execute(
            "UPDATE wagtailcore_workflowstate SET content_type_id = %s "
            "WHERE content_type_id = %s AND object_id = ANY(%s)",
            [new_ct.id, old_ct.id, str_ids],
        )

        # NumeriquePage has no tags: drop the (unused) ContentPage tag links
        cursor.execute(f"DELETE FROM {tag_table} WHERE content_object_id = ANY(%s)", [page_ids])
        if cursor.rowcount:
            logger.warning("Dropped %s ContentPage tag links while converting pages %s", cursor.rowcount, page_ids)

        cursor.execute(f"DELETE FROM {content_page_table} WHERE page_ptr_id = ANY(%s)", [page_ids])

    logger.info("Converted ContentPage pages %s into NumeriquePage", page_ids)
    return page_ids
