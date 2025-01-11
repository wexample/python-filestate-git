from typing import Optional
from unittest.mock import patch

from wexample_config.const.types import DictConfig
from wexample_filestate.const.disk import DiskItemType
from wexample_filestate.test.test_abstract_operation import TestAbstractOperation
from wexample_filestate_git.test.mixin.test_git_state_manager_mixin import TestGitFileStateManagerMixin
from wexample_filestate_git.remote.github_remote import GithubRemote
from wexample_filestate_git.remote.gitlab_remote import GitlabRemote


class TestGitRemoteCreateOperation(TestGitFileStateManagerMixin, TestAbstractOperation):
    def _operation_test_setup(self) -> None:
        # Setup all mocks
        self.mock_github_connect = patch.object(GithubRemote, 'connect').start()
        self.mock_github_check = patch.object(GithubRemote, 'check_repository_exists').start()
        self.mock_github_create = patch.object(GithubRemote, 'create_repository').start()
        self.mock_gitlab_connect = patch.object(GitlabRemote, 'connect').start()
        self.mock_gitlab_check = patch.object(GitlabRemote, 'check_repository_exists').start()
        self.mock_gitlab_create = patch.object(GitlabRemote, 'create_repository').start()
        
        # Configure default mock behaviors
        self.mock_github_check.return_value = False
        self.mock_gitlab_check.return_value = False

        # Call parent setup after mocks are ready
        super()._operation_test_setup()

    def _operation_test_setup_configuration(self) -> Optional[DictConfig]:
        return {
            'children': [
                {
                    'name': "test_git_dir",
                    'should_exist': True,
                    'type': DiskItemType.DIRECTORY,
                    'git': {
                        "remote": [
                            {
                                "name": "github",
                                "type": "github",
                                "url": "https://github.com/test-org/test-repo.git",
                                "create_remote": True
                            },
                            {
                                "name": "gitlab",
                                "type": "gitlab",
                                "url": "https://gitlab.com/test-org/test-repo.git",
                                "create_remote": True
                            }
                        ]
                    }
                }
            ]
        }

    def _operation_get_count(self) -> int:
        return 4  # Two operations for each remote: local create, and remote create

    def _operation_test_assert_initial(self) -> None:
        # Verify initial state - no repositories should exist
        self.mock_github_check.assert_not_called()
        self.mock_gitlab_check.assert_not_called()

    def _operation_test_assert_applied(self) -> None:
        # Verify that repositories were created
        self.mock_github_connect.assert_called_once()
        self.mock_github_create.assert_called_once_with(
            name="test-repo",
            namespace="test-org"
        )

        self.mock_gitlab_connect.assert_called_once()
        self.mock_gitlab_create.assert_called_once_with(
            name="test-repo",
            namespace="test-org"
        )

    def _operation_test_assert_rollback(self) -> None:
        # Add rollback assertions if needed
        pass
