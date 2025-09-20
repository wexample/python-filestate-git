from __future__ import annotations

from typing import TYPE_CHECKING

from wexample_filestate_git.testing.abstract_git_test_option import AbstractGitTestOption

if TYPE_CHECKING:
    from wexample_config.const.types import DictConfig


class TestMainBranchOptionDefault(AbstractGitTestOption):
    """Test MainBranchOption with default 'main' branch."""
    test_dir_name: str = "test-git-branch-default"

    def _operation_get_count(self) -> int:
        return 1  # Only branch creation operation

    def _operation_test_assert_applied(self) -> None:
        from git import Repo
        
        # Verify default 'main' branch was created
        dir_path = self._get_absolute_path_from_state_manager(self.test_dir_name)
        repo = Repo(str(dir_path))
        branch_names = [h.name for h in repo.heads]
        assert "main" in branch_names, f"Branch 'main' not found in {branch_names}"

    def _operation_test_assert_initial(self) -> None:
        from git import Repo
        
        # Verify branch doesn't exist initially (but Git repo exists)
        dir_path = self._get_absolute_path_from_state_manager(self.test_dir_name)
        self._ensure_git_initialized(dir_path)
        repo = Repo(str(dir_path))
        branch_names = [h.name for h in repo.heads]
        assert "main" not in branch_names, f"Branch 'main' should not exist initially"

    def _operation_test_setup_configuration(self) -> DictConfig | None:
        from wexample_filestate.const.disk import DiskItemType

        return {
            "children": [
                {
                    "name": self.test_dir_name,
                    "should_exist": True,
                    "type": DiskItemType.DIRECTORY,
                    "git": {
                        "main_branch": []  # Empty list should default to "main"
                    },
                }
            ]
        }
