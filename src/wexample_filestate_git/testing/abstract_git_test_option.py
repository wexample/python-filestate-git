from __future__ import annotations

from wexample_config.options_provider.abstract_options_provider import AbstractOptionsProvider
from wexample_filestate.testing.abstract_test_operation import AbstractTestOperation


class AbstractGitTestOption(AbstractTestOperation):
    """Base class for Git option tests."""

    def _get_test_options_providers(
            self,
    ) -> list[type[AbstractOptionsProvider]] | None:
        from wexample_filestate.options_provider.default_options_provider import (
            DefaultOptionsProvider,
        )
        from wexample_filestate_git.options_provider.git_options_provider import (
            GitOptionsProvider,
        )

        return [DefaultOptionsProvider, GitOptionsProvider]
