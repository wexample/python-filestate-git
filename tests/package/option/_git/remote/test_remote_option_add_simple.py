from __future__ import annotations

from typing import TYPE_CHECKING

from wexample_filestate_git.testing.abstract_git_test_option import AbstractGitTestOption

if TYPE_CHECKING:
    from wexample_config.const.types import DictConfig


class TestRemoteOptionAddSimple(AbstractGitTestOption):
    """Test RemoteOption for adding a simple remote locally."""
    test_dir_name: str = "test-git-remote-add-simple"

    def _operation_get_count(self) -> int:
        return 1  # Only remote add operation

    def _operation_test_assert_applied(self) -> None:
        from git import Repo
        
        # Verify remote was added
        dir_path = self._get_absolute_path_from_state_manager(self.test_dir_name)
        repo = Repo(str(dir_path))
        remote_names = [r.name for r in repo.remotes]
        assert "origin" in remote_names, f"Remote 'origin' not found in {remote_names}"
        
        # Verify remote URL
        origin_remote = repo.remote("origin")
        remote_urls = list(origin_remote.urls)
        expected_url = "https://github.com/test/test-repo.git"
        assert expected_url in remote_urls, f"Expected URL {expected_url} not found in {remote_urls}"

    def _operation_test_assert_initial(self) -> None:
        from git import Repo
        
        # Verify remote doesn't exist initially (but Git repo exists)
        dir_path = self._get_absolute_path_from_state_manager(self.test_dir_name)
        repo = Repo(str(dir_path))
        remote_names = [r.name for r in repo.remotes]
        assert "origin" not in remote_names, f"Remote 'origin' should not exist initially"

    def _operation_test_setup_configuration(self) -> DictConfig | None:
        from wexample_filestate.const.disk import DiskItemType

        return {
            "children": [
                {
                    "name": self.test_dir_name,
                    "should_exist": True,
                    "type": DiskItemType.DIRECTORY,
                    "git": {
                        "active": True,  # Git already initialized
                        "remote": [
                            {
                                "name": "origin",
                                "url": "https://github.com/test/test-repo.git",
                                "create_remote": False,  # Don't create remote repository, just add locally
                            }
                        ]
                    },
                }
            ]
        }
