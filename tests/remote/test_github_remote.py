import pytest
from unittest.mock import patch, MagicMock

from wexample_filestate_git.remote.github_remote import GithubRemote
from wexample_prompt.common.io_manager import IoManager
from wexample_helpers_api.enums.http import HttpMethod


class TestGithubRemote:
    @pytest.fixture
    def github_remote(self):
        io_manager = IoManager()
        with patch.dict('os.environ', {'GITHUB_API_TOKEN': 'test_token'}):
            remote = GithubRemote(io_manager=io_manager)
            return remote

    def test_parse_repository_url_https(self, github_remote):
        url = "https://github.com/test-namespace/test-repo.git"
        info = github_remote.parse_repository_url(url)
        assert info == {
            'name': 'test-repo',
            'namespace': 'test-namespace'
        }

    def test_parse_repository_url_ssh(self, github_remote):
        url = "git@github.com:test-namespace/test-repo.git"
        info = github_remote.parse_repository_url(url)
        assert info == {
            'name': 'test-repo',
            'namespace': 'test-namespace'
        }

    def test_create_repository(self, github_remote):
        with patch('wexample_helpers_api.common.abstract_gateway.AbstractGateway.make_request') as mock_request:
            mock_request.return_value.json.return_value = {'id': 1}
            
            result = github_remote.create_repository(
                name='test-repo',
                namespace='test-namespace',
                description='Test description',
                private=True
            )
            
            mock_request.assert_called_once()
            assert mock_request.call_args[1]['endpoint'] == 'orgs/test-namespace/repos'
            assert mock_request.call_args[1]['data']['name'] == 'test-repo'
            assert result == {'id': 1}

    def test_check_repository_exists(self, github_remote):
        with patch('wexample_helpers_api.common.abstract_gateway.AbstractGateway.make_request') as mock_request:
            mock_request.return_value.status_code = 200
            
            exists = github_remote.check_repository_exists('test-repo', 'test-namespace')
            
            mock_request.assert_called_once()
            assert mock_request.call_args[1]['endpoint'] == 'repos/test-namespace/test-repo'
            assert exists is True

    def test_create_repository_if_not_exists_existing(self, github_remote):
        with patch('wexample_helpers_api.common.abstract_gateway.AbstractGateway.make_request') as mock_request:
            mock_request.return_value.status_code = 200
            
            result = github_remote.create_repository_if_not_exists(
                'https://github.com/test-namespace/test-repo.git'
            )
            
            mock_request.assert_called_once()
            assert mock_request.call_args[1]['endpoint'] == 'repos/test-namespace/test-repo'
            assert result == {}
