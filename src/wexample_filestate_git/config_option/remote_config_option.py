from __future__ import annotations

from types import UnionType

from wexample_config.config_option.abstract_list_config_option import (
    AbstractListConfigOption,
)


class RemoteConfigOption(AbstractListConfigOption):
    def get_item_class_type(self) -> type | UnionType:
        from wexample_filestate_git.config_option.remote_item_config_option import RemoteItemConfigOption
        return RemoteItemConfigOption
