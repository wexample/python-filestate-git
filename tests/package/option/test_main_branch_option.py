from __future__ import annotations

from typing import TYPE_CHECKING

from wexample_filestate.testing.abstract_test_operation import AbstractTestOperation

if TYPE_CHECKING:
    from wexample_config.const.types import DictConfig


class TestMainBranchOptionString(AbstractTestOperation):
    """Test MainBranchOption with string value."""
    test_dir_name: str = "test-git-branch-string"

    def _operation_get_count(self) -> int:
        return 3  # Directory creation + Git init + Branch creation

    def _operation_test_assert_applied(self) -> None:
        from wexample_helpers.const.globals import DIR_GIT
        from git import Repo
        
        # Verify the directory exists
        dir_path = self._get_absolute_path_from_state_manager(self.test_dir_name)
        self._assert_file_exists(file_path=dir_path, positive=True)
        
        # Verify Git repository was initialized
        git_dir = dir_path / DIR_GIT
        self._assert_file_exists(file_path=git_dir, positive=True)
        
        # Verify branch was created
        repo = Repo(str(dir_path))
        branch_names = [h.name for h in repo.heads]
        assert "develop" in branch_names, f"Branch 'develop' not found in {branch_names}"

    def _operation_test_assert_initial(self) -> None:
        from wexample_helpers.const.globals import DIR_GIT
        
        # Verify the directory doesn't exist initially
        dir_path = self._get_absolute_path_from_state_manager(self.test_dir_name)
        self._assert_file_exists(file_path=dir_path, positive=False)
        
        # Verify Git repository doesn't exist initially
        git_dir = dir_path / DIR_GIT
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
                        "main_branch": "develop"
                    },
                }
            ]
        }


class TestMainBranchOptionList(AbstractTestOperation):
    """Test MainBranchOption with list value."""
    test_dir_name: str = "test-git-branch-list"

    def _operation_get_count(self) -> int:
        return 3  # Directory creation + Git init + Branch creation

    def _operation_test_assert_applied(self) -> None:
        from wexample_helpers.const.globals import DIR_GIT
        from git import Repo
        
        # Verify the directory exists
        dir_path = self._get_absolute_path_from_state_manager(self.test_dir_name)
        self._assert_file_exists(file_path=dir_path, positive=True)
        
        # Verify Git repository was initialized
        git_dir = dir_path / DIR_GIT
        self._assert_file_exists(file_path=git_dir, positive=True)
        
        # Verify branch was created (first item from list)
        repo = Repo(str(dir_path))
        branch_names = [h.name for h in repo.heads]
        assert "feature" in branch_names, f"Branch 'feature' not found in {branch_names}"

    def _operation_test_assert_initial(self) -> None:
        from wexample_helpers.const.globals import DIR_GIT
        
        # Verify the directory doesn't exist initially
        dir_path = self._get_absolute_path_from_state_manager(self.test_dir_name)
        self._assert_file_exists(file_path=dir_path, positive=False)
        
        # Verify Git repository doesn't exist initially
        git_dir = dir_path / DIR_GIT
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
                        "main_branch": ["feature", "backup"]
                    },
                }
            ]
        }


class TestMainBranchOptionDefault(AbstractTestOperation):
    """Test MainBranchOption with default 'main' branch."""
    test_dir_name: str = "test-git-branch-default"

    def _operation_get_count(self) -> int:
        return 3  # Directory creation + Git init + Branch creation

    def _operation_test_assert_applied(self) -> None:
        from wexample_helpers.const.globals import DIR_GIT
        from git import Repo
        
        # Verify the directory exists
        dir_path = self._get_absolute_path_from_state_manager(self.test_dir_name)
        self._assert_file_exists(file_path=dir_path, positive=True)
        
        # Verify Git repository was initialized
        git_dir = dir_path / DIR_GIT
        self._assert_file_exists(file_path=git_dir, positive=True)
        
        # Verify default 'main' branch was created
        repo = Repo(str(dir_path))
        branch_names = [h.name for h in repo.heads]
        assert "main" in branch_names, f"Branch 'main' not found in {branch_names}"

    def _operation_test_assert_initial(self) -> None:
        from wexample_helpers.const.globals import DIR_GIT
        
        # Verify the directory doesn't exist initially
        dir_path = self._get_absolute_path_from_state_manager(self.test_dir_name)
        self._assert_file_exists(file_path=dir_path, positive=False)
        
        # Verify Git repository doesn't exist initially
        git_dir = dir_path / DIR_GIT
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
                        "main_branch": []  # Empty list should default to "main"
                    },
                }
            ]
        }
