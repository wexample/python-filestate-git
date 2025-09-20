from __future__ import annotations

from types import UnionType
from typing import TYPE_CHECKING

from wexample_config.config_option.abstract_list_config_option import (
    AbstractListConfigOption,
)
from wexample_helpers.decorator.base_class import base_class

if TYPE_CHECKING:
    from types import UnionType


@base_class
class MainBranchOption(AbstractListConfigOption):
    @staticmethod
    def get_raw_value_allowed_type() -> type | UnionType:
        return str
