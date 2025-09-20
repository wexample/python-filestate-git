from __future__ import annotations

from typing import TYPE_CHECKING

from wexample_filestate.testing.abstract_test_operation import AbstractTestOperation

if TYPE_CHECKING:
    from wexample_config.const.types import DictConfig


class TestRemoteAddOption(AbstractTestOperation):
    """Test RemoteOption for adding remotes locally."""
    test_dir_name: str = "test-git-remote-add"

    def _operation_get_count(self) -> int:
        return 3  # Directory creation + Git init + Remote add

    def _operation_test_assert_applied(self) -> None:
        from wexample_helpers.const.globals import DIR_GIT
        from git import Repo
        
        # Verify the directory exists
        dir_path = self._get_absolute_path_from_state_manager(self.test_dir_name)
        self._assert_file_exists(file_path=dir_path, positive=True)
        
        # Verify Git repository was initialized
        git_dir = dir_path / DIR_GIT
        self._assert_file_exists(file_path=git_dir, positive=True)
        
        # Verify remote was added
        repo = Repo(str(dir_path))
        remote_names = [r.name for r in repo.remotes]
        assert "origin" in remote_names, f"Remote 'origin' not found in {remote_names}"
        
        # Verify remote URL
        origin_remote = repo.remote("origin")
        remote_urls = list(origin_remote.urls)
        expected_url = "https://github.com/test/test-repo.git"
        assert expected_url in remote_urls, f"Expected URL {expected_url} not found in {remote_urls}"

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
                        "remote": [
                            {
                                "url": "https://github.com/test/test-repo.git",
                                "type": "github",
                                "create_remote": False,  # Don't create remote repository, just add locally
                            }
                        ]
                    },
                }
            ]
        }


class TestRemoteAddMultiple(AbstractTestOperation):
    """Test RemoteOption for adding multiple remotes."""
    test_dir_name: str = "test-git-remote-add-multiple"

    def _operation_get_count(self) -> int:
        return 3  # Directory creation + Git init + Remote add (handles multiple remotes)

    def _operation_test_assert_applied(self) -> None:
        from wexample_helpers.const.globals import DIR_GIT
        from git import Repo
        
        # Verify the directory exists
        dir_path = self._get_absolute_path_from_state_manager(self.test_dir_name)
        self._assert_file_exists(file_path=dir_path, positive=True)
        
        # Verify Git repository was initialized
        git_dir = dir_path / DIR_GIT
        self._assert_file_exists(file_path=git_dir, positive=True)
        
        # Verify remotes were added
        repo = Repo(str(dir_path))
        remote_names = [r.name for r in repo.remotes]
        assert "origin" in remote_names, f"Remote 'origin' not found in {remote_names}"

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
                        "remote": [
                            {
                                "url": "https://github.com/test/repo1.git",
                                "type": "github",
                                "create_remote": False,
                            },
                            {
                                "url": "https://gitlab.com/test/repo2.git", 
                                "type": "gitlab",
                                "create_remote": False,
                            }
                        ]
                    },
                }
            ]
        }


class TestRemoteAddInactive(AbstractTestOperation):
    """Test RemoteOption when remote is inactive."""
    test_dir_name: str = "test-git-remote-add-inactive"

    def _operation_get_count(self) -> int:
        return 2  # Directory creation + Git init (no remote add)

    def _operation_test_assert_applied(self) -> None:
        from wexample_helpers.const.globals import DIR_GIT
        from git import Repo
        
        # Verify the directory exists
        dir_path = self._get_absolute_path_from_state_manager(self.test_dir_name)
        self._assert_file_exists(file_path=dir_path, positive=True)
        
        # Verify Git repository was initialized
        git_dir = dir_path / DIR_GIT
        self._assert_file_exists(file_path=git_dir, positive=True)
        
        # Verify NO remote was added (inactive)
        repo = Repo(str(dir_path))
        remote_names = [r.name for r in repo.remotes]
        assert len(remote_names) == 0, f"Expected no remotes but found {remote_names}"

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
                        "remote": [
                            {
                                "url": "https://github.com/test/test-repo.git",
                                "type": "github",
                                "create_remote": False,
                                "active": False,  # Inactive remote
                            }
                        ]
                    },
                }
            ]
        }
