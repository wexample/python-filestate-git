from __future__ import annotations

from typing import TYPE_CHECKING

from wexample_config.options_provider.abstract_options_provider import (
    AbstractOptionsProvider,
)

if TYPE_CHECKING:
    from wexample_config.config_option.abstract_config_option import (
        AbstractConfigOption,
    )


class RemoteItemOptionsProvider(AbstractOptionsProvider):
    @classmethod
    def get_options(cls) -> list[type[AbstractConfigOption]]:
        from wexample_config.config_option.name_config_option import NameConfigOption
        from wexample_filestate.option.active_option import (
            ActiveOption,
        )
        from wexample_filestate.option.type_option import TypeOption
        from wexample_filestate_git.config_option.create_remote_config_option import (
            CreateRemoteConfigOption,
        )
        from wexample_filestate_git.config_option.url_config_option import (
            UrlConfigOption,
        )

        return [
            ActiveOption,
            NameConfigOption,
            UrlConfigOption,
            CreateRemoteConfigOption,
            TypeOption,
        ]
