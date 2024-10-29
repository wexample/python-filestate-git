from typing import List, Type, TYPE_CHECKING

from wexample_config.options_provider.abstract_options_provider import AbstractOptionsProvider

if TYPE_CHECKING:
    from wexample_filestate.option.abstract_item_option import AbstractItemOption


class GitOptionsProvider(AbstractOptionsProvider):
    @classmethod
    def get_options(cls) -> List[Type["AbstractItemOption"]]:
        from wexample_filestate_git.option.git_option import GitOption

        return [
            GitOption
        ]

