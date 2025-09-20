from __future__ import annotations

from typing import TYPE_CHECKING

from wexample_filestate_git.testing.abstract_git_test_option import AbstractGitTestOption

if TYPE_CHECKING:
    from wexample_config.const.types import DictConfig


class TestMainBranchOptionList(AbstractGitTestOption):
    """Test MainBranchOption with list value."""
    test_dir_name: str = "test-git-branch-list"

    def _operation_get_count(self) -> int:
        return 1  # Only branch creation operation

    def _operation_test_assert_applied(self) -> None:
        from git import Repo
        
        # Verify branch was created (first item from list)
        dir_path = self._get_absolute_path_from_state_manager(self.test_dir_name)
        repo = Repo(str(dir_path))
        branch_names = [h.name for h in repo.heads]
        assert "feature" in branch_names, f"Branch 'feature' not found in {branch_names}"

    def _operation_test_assert_initial(self) -> None:
        from git import Repo
        
        # Verify branch doesn't exist initially (but Git repo exists)
        dir_path = self._get_absolute_path_from_state_manager(self.test_dir_name)

        # Ensure Git is initialized (creates directory + .git if needed)
        self._ensure_git_initialized(dir_path)

        # Verify directory and Git exist
        self._assert_file_exists(file_path=dir_path, positive=True)

        # Verify branch doesn't exist initially
        repo = Repo(str(dir_path))
        branch_names = [h.name for h in repo.heads]
        assert "feature" not in branch_names, f"Branch 'feature' should not exist initially"

    def _operation_test_setup_configuration(self) -> DictConfig | None:
        from wexample_filestate.const.disk import DiskItemType

        return {
            "children": [
                {
                    "name": self.test_dir_name,
                    "type": DiskItemType.DIRECTORY,
                    "git": {
                        "main_branch": ["feature", "backup"]
                    },
                }
            ]
        }
