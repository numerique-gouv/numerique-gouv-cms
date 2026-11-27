from wagtail.blocks import StreamBlock
from wagtail.fields import StreamField


def extend_stream_field(model, field_name, extra_blocks):
    """
    Add blocks to a StreamField defined by a third-party app (e.g. Sites Conformes).

    The field is a concrete column of the package's model, so it cannot be redefined
    in a multi-table child. Instead, the field's stream block is replaced at runtime by
    one containing the original blocks followed by `extra_blocks` (a block with the same
    name replaces the original one, keeping its position).

    The extra blocks are hidden from `deconstruct()`, so the migration autodetector only
    sees the package's own definition and never tries to write a migration into it.
    """
    field = model._meta.get_field(field_name)
    if getattr(field, "_numerique_extended", False):
        return

    original_block = field.stream_block
    extended_block = StreamBlock(list(original_block.child_blocks.items()) + list(extra_blocks))
    extended_block.set_meta_options(field.block_opts)

    def deconstruct():
        # Temporarily restore the original block so that migrations ignore the extra blocks
        field.stream_block = original_block
        try:
            return StreamField.deconstruct(field)
        finally:
            field.stream_block = extended_block

    field.stream_block = extended_block
    field.deconstruct = deconstruct
    field._numerique_extended = True
