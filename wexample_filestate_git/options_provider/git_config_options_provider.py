from typing import TYPE_CHECKING, List, Type

from wexample_config.options_provider.abstract_options_provider import \
    AbstractOptionsProvider

if TYPE_CHECKING:
    from wexample_config.config_option.abstract_config_option import \
        AbstractConfigOption


class GitConfigOptionsProvider(AbstractOptionsProvider):
    @classmethod
    def get_options(cls) -> List[Type["AbstractConfigOption"]]:
        from wexample_filestate_git.config_option.remote_config_option import \
            RemoteConfigOption

        return [
            RemoteConfigOption,
        ]
