from __future__ import annotations

from typing import TYPE_CHECKING

from wexample_filestate_git.testing.abstract_git_test_option import AbstractGitTestOption

if TYPE_CHECKING:
    from wexample_config.const.types import DictConfig


class TestRemoteOptionAddSimple(AbstractGitTestOption):
    """Test RemoteOption for adding a simple remote locally."""
    test_dir_name: str = "test_git_dir"  # Use existing test directory

    def _operation_get_count(self) -> int:
        return 2  # Git init + Remote add operation

    def _operation_test_assert_applied(self) -> None:
        from git import Repo
        from wexample_helpers.const.globals import DIR_GIT
        
        # Verify Git repo exists
        dir_path = self._get_absolute_path_from_state_manager(self.test_dir_name)
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
        # Verify directory exists
        dir_path = self._get_absolute_path_from_state_manager(self.test_dir_name)
        self._assert_file_exists(file_path=dir_path, positive=True)
        
        # Ensure NO Git repo exists initially - clean slate
        self._ensure_no_git(dir_path)

    def _operation_test_setup_configuration(self) -> DictConfig | None:
        from wexample_filestate.const.disk import DiskItemType

        return {
            "children": [
                {
                    "name": self.test_dir_name,
                    "should_exist": True,
                    "type": DiskItemType.DIRECTORY,
                    "git": {
                        "active": True,  # Git should be initialized
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

    def _ensure_no_git(self, dir_path) -> None:
        """Ensure no Git repository exists in the given directory."""
        from wexample_helpers.const.globals import DIR_GIT
        import shutil
        
        git_dir = dir_path / DIR_GIT
        if git_dir.exists():
            shutil.rmtree(git_dir)
        self._assert_file_exists(file_path=git_dir, positive=False)
