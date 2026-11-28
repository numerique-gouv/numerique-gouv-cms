"""
Convert the legacy ContentPage pages into numerique_gouv.NumeriquePage pages.

numerique.gouv.fr swaps the sites_conformes ContentPage for NumeriquePage (SF_CONTENTPAGE_MODEL), so the
ContentPage model has no manager and its migrations do not touch the database anymore. A few legacy pages
(legal notice, accessibility statement…) still live in the old table, renamed into
sites_conformes_core_contentpage by migrate_from_sites_faciles. Both tables share the same columns, so the
conversion keeps the page ids, URLs, revisions and history: only the type-specific rows and the content type
references change.

The legacy tables are read with raw SQL, since no model (current or historical) can query them.
"""

import logging

from django.db import connection, transaction

logger = logging.getLogger(__name__)

LEGACY_APP_LABEL = "sites_conformes_core"
LEGACY_MODEL = "contentpage"
LEGACY_TABLE = "sites_conformes_core_contentpage"
LEGACY_TAG_TABLE = "sites_conformes_core_tagcontentpage"


def _table_columns(cursor, table: str) -> list[str]:
    return [column.name for column in connection.introspection.get_table_description(cursor, table)]


def convert_content_pages(apps, schema_editor=None) -> list[int]:
    """
    Convert every legacy ContentPage into a NumeriquePage and return the converted page ids.

    Works both with the historical models of a migration and with the real app registry.
    Does nothing when the legacy table does not exist (new databases). PostgreSQL only (uses jsonb_set).
    """
    ContentType = apps.get_model("contenttypes", "ContentType")
    NumeriqueBasePage = apps.get_model("numerique_gouv", "NumeriqueBasePage")
    NumeriquePage = apps.get_model("numerique_gouv", "NumeriquePage")

    table_names = connection.introspection.table_names()
    if LEGACY_TABLE not in table_names:
        return []

    old_ct = ContentType.objects.filter(app_label=LEGACY_APP_LABEL, model=LEGACY_MODEL).first()

    with transaction.atomic(), connection.cursor() as cursor:
        cursor.execute(f"SELECT page_ptr_id FROM {LEGACY_TABLE}")
        page_ids = [row[0] for row in cursor.fetchall()]
        if not old_ct or not page_ids:
            return []

        new_ct, _created = ContentType.objects.get_or_create(app_label="numerique_gouv", model="numeriquepage")
        str_ids = [str(page_id) for page_id in page_ids]

        # Type-specific rows: copy the columns both tables share
        target_columns = [field.column for field in NumeriqueBasePage._meta.local_concrete_fields]
        legacy_columns = set(_table_columns(cursor, LEGACY_TABLE))
        missing = [column for column in target_columns if column not in legacy_columns]
        if missing:
            raise RuntimeError(f"{LEGACY_TABLE} lacks the NumeriqueBasePage columns {missing}")
        columns = ", ".join(f'"{column}"' for column in target_columns)

        cursor.execute(
            f"INSERT INTO {NumeriqueBasePage._meta.db_table} ({columns}) "
            f"SELECT {columns} FROM {LEGACY_TABLE} WHERE page_ptr_id = ANY(%s)",
            [page_ids],
        )
        cursor.execute(
            f"INSERT INTO {NumeriquePage._meta.db_table} (numeriquebasepage_ptr_id) "
            f"SELECT page_ptr_id FROM {LEGACY_TABLE} WHERE page_ptr_id = ANY(%s)",
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
        if LEGACY_TAG_TABLE in table_names:
            cursor.execute(f"DELETE FROM {LEGACY_TAG_TABLE} WHERE content_object_id = ANY(%s)", [page_ids])
            if cursor.rowcount:
                logger.warning("Dropped %s ContentPage tag links while converting pages %s", cursor.rowcount, page_ids)

        cursor.execute(f"DELETE FROM {LEGACY_TABLE} WHERE page_ptr_id = ANY(%s)", [page_ids])

    logger.info("Converted ContentPage pages %s into NumeriquePage", page_ids)
    return page_ids
