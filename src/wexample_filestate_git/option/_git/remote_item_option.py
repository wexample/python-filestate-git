from __future__ import annotations

from typing import TYPE_CHECKING, Any, Union

from wexample_config.config_option.abstract_config_option import AbstractConfigOption
from wexample_config.config_option.abstract_nested_config_option import (
    AbstractNestedConfigOption,
)
from wexample_filestate.option.mixin.option_mixin import OptionMixin
from wexample_helpers.decorator.base_class import base_class

if TYPE_CHECKING:
    from wexample_config.options_provider.abstract_options_provider import (
        AbstractOptionsProvider,
    )
    from wexample_filestate.operation.abstract_operation import AbstractOperation
    from wexample_filestate.const.types_state_items import TargetFileOrDirectoryType


@base_class
class RemoteItemOption(OptionMixin, AbstractNestedConfigOption):
    @staticmethod
    def get_raw_value_allowed_type() -> Any:
        return Union[dict]

    def get_options_providers(self) -> list[type[AbstractOptionsProvider]]:
        from wexample_filestate_git.options_provider.remote_item_options_provider import (
            RemoteItemOptionsProvider,
        )

        return [RemoteItemOptionsProvider]

    def get_allowed_options(self) -> list[type[AbstractConfigOption]]:
        from wexample_filestate_git.option._git.create_remote_option import CreateRemoteOption
        from wexample_filestate_git.option._git.type_option import TypeOption
        from wexample_filestate_git.option._git.url_option import UrlOption
        from wexample_filestate.option.active_option import ActiveOption

        return [
            CreateRemoteOption,
            TypeOption,
            UrlOption,
            ActiveOption,
        ]
