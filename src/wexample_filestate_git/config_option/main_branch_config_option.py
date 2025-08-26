from __future__ import annotations

from types import UnionType

from wexample_config.config_option.abstract_list_config_option import (
    AbstractListConfigOption,
)


class MainBranchConfigOption(AbstractListConfigOption):
    def get_item_class_type(self) -> type | UnionType:
        return str
