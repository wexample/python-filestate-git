from __future__ import annotations

from typing import TYPE_CHECKING

from wexample_filestate_git.testing.abstract_git_test_option import AbstractGitTestOption

if TYPE_CHECKING:
    from wexample_config.const.types import DictConfig


class AbstractGitOptionTest(AbstractGitTestOption):
    """Base class for GitOption tests."""
    
    # To be overridden by child classes
    test_dir_name: str = None
    git_config: bool | dict = None
    should_directory_exist_initially: bool = True

    def _operation_get_count(self) -> int:
        return 1  # Only Git init operation

    def _operation_test_assert_applied(self) -> None:
        from wexample_helpers.const.globals import DIR_GIT
        
        # Verify Git repository was created
        dir_path = self._get_absolute_path_from_state_manager(self.test_dir_name)
        git_dir = dir_path / DIR_GIT
        self._assert_file_exists(file_path=git_dir, positive=True)

    def _operation_test_assert_initial(self) -> None:
        from wexample_helpers.const.globals import DIR_GIT
        
        # Verify directory exists (or not) as expected
        dir_path = self._get_absolute_path_from_state_manager(self.test_dir_name)
        self._assert_file_exists(file_path=dir_path, positive=self.should_directory_exist_initially)
        
        # Verify Git is not initialized initially
        if self.should_directory_exist_initially:
            git_dir = dir_path / DIR_GIT
            self._assert_file_exists(file_path=git_dir, positive=False)

    def _operation_test_setup_configuration(self) -> DictConfig | None:
        from wexample_filestate.const.disk import DiskItemType

        config = {
            "children": [
                {
                    "name": self.test_dir_name,
                    "type": DiskItemType.DIRECTORY,
                    "git": self.git_config,
                }
            ]
        }

        return config
