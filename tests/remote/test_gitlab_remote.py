import pytest
from unittest.mock import patch, MagicMock

from wexample_filestate_git.remote.gitlab_remote import GitlabRemote
from wexample_prompt.common.io_manager import IoManager
from wexample_helpers_api.enums.http import HttpMethod


class TestGitlabRemote:
    @pytest.fixture
    def gitlab_remote(self):
        io_manager = IoManager()
        with patch.dict('os.environ', {'GITLAB_API_TOKEN': 'test_token'}):
            remote = GitlabRemote(io_manager=io_manager)
            return remote

    def test_parse_repository_url_https(self, gitlab_remote):
        url = "https://gitlab.com/test-namespace/test-repo.git"
        info = gitlab_remote.parse_repository_url(url)
        assert info == {
            'name': 'test-repo',
            'namespace': 'test-namespace'
        }

    def test_parse_repository_url_ssh(self, gitlab_remote):
        url = "git@gitlab.com:test-namespace/test-repo.git"
        info = gitlab_remote.parse_repository_url(url)
        assert info == {
            'name': 'test-repo',
            'namespace': 'test-namespace'
        }

    def test_create_repository(self, gitlab_remote):
        with patch('wexample_helpers_api.common.abstract_gateway.AbstractGateway.make_request') as mock_request:
            mock_request.return_value.json.return_value = {'id': 1}
            
            result = gitlab_remote.create_repository(
                name='test-repo',
                namespace='test-namespace',
                description='Test description',
                private=True
            )
            
            mock_request.assert_called_once()
            assert mock_request.call_args[1]['endpoint'] == 'projects'
            assert mock_request.call_args[1]['data']['name'] == 'test-repo'
            assert result == {'id': 1}

    def test_check_repository_exists(self, gitlab_remote):
        with patch('wexample_helpers_api.common.abstract_gateway.AbstractGateway.make_request') as mock_request:
            mock_request.return_value.status_code = 200
            
            exists = gitlab_remote.check_repository_exists('test-repo', 'test-namespace')
            
            mock_request.assert_called_once()
            assert mock_request.call_args[1]['endpoint'] == 'projects/test-namespace%2Ftest-repo'
            assert exists is True

    def test_create_repository_if_not_exists_new(self, gitlab_remote):
        with patch('wexample_helpers_api.common.abstract_gateway.AbstractGateway.make_request') as mock_request:
            # First call to check_repository_exists
            mock_request.return_value.status_code = 404
            
            # Second call to create_repository
            mock_request.return_value.json.return_value = {'id': 1}
            
            result = gitlab_remote.create_repository_if_not_exists(
                'https://gitlab.com/test-namespace/test-repo.git',
                description='Test description',
                private=True
            )
            
            assert mock_request.call_count == 2
            
            # Verify check_repository_exists call
            check_call = mock_request.call_args_list[0]
            assert check_call[1]['endpoint'] == 'projects/test-namespace%2Ftest-repo'
            
            # Verify create_repository call
            create_call = mock_request.call_args_list[1]
            assert create_call[1]['endpoint'] == 'projects'
            assert create_call[1]['data']['name'] == 'test-repo'
            assert result == {'id': 1}

    def test_create_repository_if_not_exists_existing(self, gitlab_remote):
        with patch('wexample_helpers_api.common.abstract_gateway.AbstractGateway.make_request') as mock_request:
            # First call to check_repository_exists
            mock_request.return_value.status_code = 200
            
            result = gitlab_remote.create_repository_if_not_exists(
                'https://gitlab.com/test-namespace/test-repo.git'
            )
            
            assert mock_request.call_count == 1
            
            # Verify check_repository_exists call
            check_call = mock_request.call_args_list[0]
            assert check_call[1]['endpoint'] == 'projects/test-namespace%2Ftest-repo'
            assert result == {}
