from __future__ import annotations

from typing import Any, Union

from wexample_config.config_option.abstract_config_option import AbstractConfigOption


class UrlConfigOption(AbstractConfigOption):
    @staticmethod
    def get_raw_value_allowed_type() -> Any:
        from wexample_filestate.item.abstract_item_target import AbstractItemTarget
        from collections.abc import Callable

        return Union[str, Callable[[AbstractItemTarget], str]]
