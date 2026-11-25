from sites_conformes.core.abstract import SitesFacilesBasePage
from sites_conformes.core.blocks import STREAMFIELD_COMMON_BLOCKS
from wagtail.fields import StreamField

from numerique_gouv.blocks import STREAMFIELD_NUMERIQUE_BLOCKS


class NumeriqueBasePage(SitesFacilesBasePage):
    body = StreamField(
        STREAMFIELD_COMMON_BLOCKS + STREAMFIELD_NUMERIQUE_BLOCKS,
        blank=True,
        use_json_field=True,
    )
