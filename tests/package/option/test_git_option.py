from __future__ import annotations

from typing import TYPE_CHECKING

from wexample_config.options_provider.abstract_options_provider import AbstractOptionsProvider
from wexample_filestate.testing.abstract_test_operation import AbstractTestOperation

if TYPE_CHECKING:
    from wexample_config.const.types import DictConfig


class AbstractGitTestOption(AbstractTestOperation):
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


class TestGitOptionBoolTrue(AbstractGitTestOption):
    """Test GitOption with boolean True value."""
    test_dir_name: str = "test-git-repo"

    def _operation_get_count(self) -> int:
        return 1  # Directory creation only

    def _operation_test_assert_applied(self) -> None:
        from wexample_helpers.const.globals import DIR_GIT

        # Verify the directory exists
        dir_path = self._get_absolute_path_from_state_manager(self.test_dir_name)

        self._assert_file_exists(file_path=dir_path, positive=True)

        # Verify Git repository was NOT initialized, as we should create the parent directory first with should_exists
        git_dir = f"{dir_path}/{DIR_GIT}"
        self._assert_file_exists(file_path=git_dir, positive=False)

    def _operation_test_assert_initial(self) -> None:
        from wexample_helpers.const.globals import DIR_GIT

        # Verify the directory doesn't exist initially
        dir_path = self._get_absolute_path_from_state_manager(self.test_dir_name)
        self._assert_file_exists(file_path=dir_path, positive=False)

        # Verify Git repository doesn't exist initially
        git_dir = f"{dir_path}/{DIR_GIT}"
        self._assert_file_exists(file_path=git_dir, positive=False)

    def _operation_test_setup_configuration(self) -> DictConfig | None:
        from wexample_filestate.const.disk import DiskItemType

        return {
            "children": [
                {
                    "name": self.test_dir_name,
                    "should_exist": True,
                    "type": DiskItemType.DIRECTORY,
                    "git": True,
                }
            ]
        }


class TestGitOptionDict(AbstractGitTestOption):
    """Test GitOption with dict value on existing directory."""
    test_dir_name: str = "test_git_dir"

    def _operation_get_count(self) -> int:
        return 1  # Only Git init (directory already exists)

    def _operation_test_assert_applied(self) -> None:
        from wexample_helpers.const.globals import DIR_GIT

        # Verify the directory exists
        dir_path = self._get_absolute_path_from_state_manager(self.test_dir_name)
        self._assert_file_exists(file_path=dir_path, positive=True)

        # Verify Git repository was initialized
        git_dir = f"{dir_path}/{DIR_GIT}"
        self._assert_file_exists(file_path=git_dir, positive=True)

    def _operation_test_assert_initial(self) -> None:
        from wexample_helpers.const.globals import DIR_GIT

        # Verify the directory exists initially (from resources)
        dir_path = self._get_absolute_path_from_state_manager(self.test_dir_name)
        self._assert_file_exists(file_path=dir_path, positive=True)

        # Verify Git repository doesn't exist initially
        git_dir = f"{dir_path}/{DIR_GIT}"
        self._assert_file_exists(file_path=git_dir, positive=False)

    def _operation_test_setup_configuration(self) -> DictConfig | None:
        from wexample_filestate.const.disk import DiskItemType

        return {
            "children": [
                {
                    "name": self.test_dir_name,
                    "should_exist": True,
                    "type": DiskItemType.DIRECTORY,
                    "git": {
                        "active": True
                    },
                }
            ]
        }


class TestGitOptionExistingGit(AbstractGitTestOption):
    """Test GitOption with existing Git repository (should create config)."""
    test_dir_name: str = "test_git_dir_with_git"

    def _operation_get_count(self) -> int:
        return 1  # Git init operation (should create config in existing .git)

    def _operation_test_assert_applied(self) -> None:
        from wexample_helpers.const.globals import DIR_GIT
        
        # Verify the directory exists
        dir_path = self._get_absolute_path_from_state_manager(self.test_dir_name)
        self._assert_file_exists(file_path=dir_path, positive=True)
        
        # Verify Git repository still exists
        git_dir = f"{dir_path}/{DIR_GIT}"
        self._assert_file_exists(file_path=git_dir, positive=True)
        
        # Verify Git config file was created
        git_config = f"{git_dir}/config"
        self._assert_file_exists(file_path=git_config, positive=True)

    def _operation_test_assert_initial(self) -> None:
        from wexample_helpers.const.globals import DIR_GIT
        
        # Verify the directory exists initially (from resources)
        dir_path = self._get_absolute_path_from_state_manager(self.test_dir_name)
        self._assert_file_exists(file_path=dir_path, positive=True)
        
        # Verify Git repository exists initially (empty .git folder)
        git_dir = f"{dir_path}/{DIR_GIT}"
        self._assert_file_exists(file_path=git_dir, positive=True)
        
        # Verify Git config file doesn't exist initially
        git_config = f"{dir_path}/config"
        self._assert_file_exists(file_path=git_config, positive=False)

    def _operation_test_setup_configuration(self) -> DictConfig | None:
        from wexample_filestate.const.disk import DiskItemType

        return {
            "children": [
                {
                    "name": self.test_dir_name,
                    "should_exist": True,
                    "type": DiskItemType.DIRECTORY,
                    "git": {
                        "active": True
                    },
                }
            ]
        }
