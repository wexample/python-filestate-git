from __future__ import annotations

from typing import TYPE_CHECKING

from wexample_filestate.testing.abstract_test_operation import AbstractTestOperation

if TYPE_CHECKING:
    from wexample_config.const.types import DictConfig


class TestRemoteOptionCreateGithub(AbstractTestOperation):
    """Test RemoteOption with GitHub remote creation."""
    test_dir_name: str = "test-git-remote-github"

    def _operation_get_count(self) -> int:
        return 3  # Directory creation + Git init + Remote creation

    def _operation_test_assert_applied(self) -> None:
        from wexample_helpers.const.globals import DIR_GIT
        
        # Verify the directory exists
        dir_path = self._get_absolute_path_from_state_manager(self.test_dir_name)
        self._assert_file_exists(file_path=dir_path, positive=True)
        
        # Verify Git repository was initialized
        git_dir = dir_path / DIR_GIT
        self._assert_file_exists(file_path=git_dir, positive=True)

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
                                "create_remote": True,
                            }
                        ]
                    },
                }
            ]
        }


class TestRemoteOptionCreateGitlab(AbstractTestOperation):
    """Test RemoteOption with GitLab remote creation."""
    test_dir_name: str = "test-git-remote-gitlab"

    def _operation_get_count(self) -> int:
        return 3  # Directory creation + Git init + Remote creation

    def _operation_test_assert_applied(self) -> None:
        from wexample_helpers.const.globals import DIR_GIT
        
        # Verify the directory exists
        dir_path = self._get_absolute_path_from_state_manager(self.test_dir_name)
        self._assert_file_exists(file_path=dir_path, positive=True)
        
        # Verify Git repository was initialized
        git_dir = dir_path / DIR_GIT
        self._assert_file_exists(file_path=git_dir, positive=True)

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
                                "url": "https://gitlab.com/test/test-repo.git",
                                "type": "gitlab",
                                "create_remote": True,
                            }
                        ]
                    },
                }
            ]
        }


class TestRemoteOptionNoCreate(AbstractTestOperation):
    """Test RemoteOption when create_remote is false."""
    test_dir_name: str = "test-git-remote-no-create"

    def _operation_get_count(self) -> int:
        return 2  # Directory creation + Git init (no remote creation)

    def _operation_test_assert_applied(self) -> None:
        from wexample_helpers.const.globals import DIR_GIT
        
        # Verify the directory exists
        dir_path = self._get_absolute_path_from_state_manager(self.test_dir_name)
        self._assert_file_exists(file_path=dir_path, positive=True)
        
        # Verify Git repository was initialized
        git_dir = dir_path / DIR_GIT
        self._assert_file_exists(file_path=git_dir, positive=True)

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
                                "create_remote": False,  # No creation
                            }
                        ]
                    },
                }
            ]
        }
