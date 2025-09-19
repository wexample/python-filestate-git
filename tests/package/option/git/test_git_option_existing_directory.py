from __future__ import annotations

from typing import TYPE_CHECKING

from wexample_filestate_git.testing.abstract_git_test_option import AbstractGitTestOption

if TYPE_CHECKING:
    from wexample_config.const.types import DictConfig


class TestGitOptionExistingDirectory(AbstractGitTestOption):
    """Test GitOption on existing directory that gets invalid .git during test."""
    test_dir_name: str = "test_git_dir_existing"

    def _operation_get_count(self) -> int:
        return 1  # Git init operation (should initialize invalid .git)

    def _operation_test_assert_applied(self) -> None:
        from wexample_helpers_git.helpers.git import git_is_init
        
        # Verify the directory exists
        dir_path = self._get_absolute_path_from_state_manager(self.test_dir_name)
        self._assert_file_exists(file_path=dir_path, positive=True)
        
        # Verify Git repository is now valid
        assert git_is_init(dir_path), f"Git repository should be valid at {dir_path}"

    def _operation_test_assert_initial(self) -> None:
        from wexample_helpers.const.globals import DIR_GIT
        from wexample_helpers_git.helpers.git import git_is_init
        
        # Verify the directory exists initially (from resources)
        dir_path = self._get_absolute_path_from_state_manager(self.test_dir_name)
        self._assert_file_exists(file_path=dir_path, positive=True)
        
        # Create an invalid .git directory during the test
        git_dir = f"{dir_path}/{DIR_GIT}"
        from pathlib import Path
        Path(git_dir).mkdir(exist_ok=True)
        
        # Verify Git repository is invalid initially
        assert not git_is_init(dir_path), f"Git repository should be invalid at {dir_path}"

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
