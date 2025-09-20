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

    def _ensure_no_git(self, dir_path) -> None:
        """Ensure no Git repository exists in the given directory."""
        from wexample_helpers.const.globals import DIR_GIT
        import shutil

        git_dir = dir_path / DIR_GIT
        if git_dir.exists():
            shutil.rmtree(git_dir)
        self._assert_file_exists(file_path=git_dir, positive=False)
