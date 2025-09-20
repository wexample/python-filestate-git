from __future__ import annotations

from typing import TYPE_CHECKING

from wexample_config.options_provider.abstract_options_provider import (
    AbstractOptionsProvider,
)

if TYPE_CHECKING:
    from wexample_config.config_option.abstract_config_option import (
        AbstractConfigOption,
    )


class GitConfigOptionsProvider(AbstractOptionsProvider):
    @classmethod
    def get_options(cls) -> list[type[AbstractConfigOption]]:
        from wexample_filestate.option.active_option import (
            ActiveOption,
        )
        from wexample_filestate_git.option._git.main_branch_option import (
            MainBranchOption,
        )
        from wexample_filestate_git.option._git.remote_option import (
            RemoteOption,
        )

        return [
            ActiveOption,
            MainBranchOption,
            RemoteOption,
        ]
