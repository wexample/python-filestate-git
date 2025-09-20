from __future__ import annotations

from typing import TYPE_CHECKING

from wexample_config.options_provider.abstract_options_provider import (
    AbstractOptionsProvider,
)

if TYPE_CHECKING:
    from wexample_filestate.option.mixin.option_mixin import OptionMixin


class RemoteItemOptionsProvider(AbstractOptionsProvider):
    @classmethod
    def get_options(cls) -> list[type[OptionMixin]]:
        from wexample_filestate.option.active_option import (
            ActiveOption,
        )
        from wexample_filestate.option.type_option import TypeOption
        from wexample_filestate.option.name_option import NameOption
        from wexample_filestate_git.option._git.create_remote_option import CreateRemoteOption
        from wexample_filestate_git.option._git.url_option import UrlOption

        return [
            ActiveOption,
            NameOption,
            UrlOption,
            CreateRemoteOption,
            TypeOption,
        ]
