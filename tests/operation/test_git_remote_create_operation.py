from typing import Optional
from unittest.mock import patch, MagicMock

from wexample_config.const.types import DictConfig
from wexample_filestate.const.disk import DiskItemType
from wexample_filestate.test.test_abstract_operation import TestAbstractOperation
from wexample_filestate_git.test.mixin.test_git_state_manager_mixin import TestGitFileStateManagerMixin
from wexample_filestate_git.remote.github_remote import GithubRemote
from wexample_filestate_git.remote.gitlab_remote import GitlabRemote


class TestGitRemoteCreateOperation(TestGitFileStateManagerMixin, TestAbstractOperation):
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

    def test_apply(self) -> None:
        # Disable default execution method
        assert True

    def _operation_get_count(self) -> int:
        return 0

    def _operation_test_assert_initial(self) -> None:
        assert True

    def _operation_test_assert_applied(self) -> None:
        assert True

    @patch.object(GithubRemote, 'connect')
    @patch.object(GithubRemote, 'check_repository_exists')
    @patch.object(GithubRemote, 'create_repository')
    @patch.object(GitlabRemote, 'connect')
    @patch.object(GitlabRemote, 'check_repository_exists')
    @patch.object(GitlabRemote, 'create_repository')
    def test_create_remote_repositories(
        self,
        mock_gitlab_create: MagicMock,
        mock_gitlab_check: MagicMock,
        mock_gitlab_connect: MagicMock,
        mock_github_create: MagicMock,
        mock_github_check: MagicMock,
        mock_github_connect: MagicMock
    ):
        # Configure mocks
        mock_github_check.return_value = False
        mock_gitlab_check.return_value = False

        # Run the operation
        self._operation_test_setup()
        self._operation_test_apply()

        # Assert GitHub interactions
        mock_github_connect.assert_called_once()
        mock_github_create.assert_called_once_with(
            name="test-repo",
            namespace="test-org"
        )

        # Assert GitHub interactions
        mock_gitlab_connect.assert_called_once()
        mock_gitlab_create.assert_called_once_with(
            name="test-repo",
            namespace="test-org"
        )
