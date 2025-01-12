from unittest.mock import patch

import pytest

from wexample_prompt.common.io_manager import IoManager


class GitRemoteTest:
    """Base class for Git remote service tests."""

    # Service specific attributes to be overridden by child classes
    ENV_TOKEN_NAME = None
    SERVICE_CLASS = None
    TEST_TOKEN = 'test_token'

    @pytest.fixture
    def remote(self):
        """Create a remote instance with mocked token."""
        io_manager = IoManager()
        with patch.dict('os.environ', {self.ENV_TOKEN_NAME: self.TEST_TOKEN}):
            remote = self.SERVICE_CLASS(io_manager=io_manager)
            return remote

    def test_parse_repository_url_https(self, remote):
        """Test parsing HTTPS repository URL."""
        url = f"https://{remote.domain}/{self.test_namespace}/{self.test_repo_name}.git"
        info = remote.parse_repository_url(url)
        assert info == {
            'name': self.test_repo_name,
            'namespace': self.test_namespace
        }

    def test_parse_repository_url_ssh(self, remote):
        """Test parsing SSH repository URL."""
        url = f"git@{remote.domain}:{self.test_namespace}/{self.test_repo_name}.git"
        info = remote.parse_repository_url(url)
        assert info == {
            'name': self.test_repo_name,
            'namespace': self.test_namespace
        }

    def test_check_repository_exists(self, remote):
        """Test checking if a repository exists."""
        with patch('wexample_helpers_api.common.abstract_gateway.AbstractGateway.make_request') as mock_request:
            mock_request.return_value.status_code = 200

            exists = remote.check_repository_exists(self.test_repo_name, self.test_namespace)

            mock_request.assert_called_once()
            self._assert_check_repository_exists_request(mock_request)
            assert exists is True

    def test_create_repository_if_not_exists_existing(self, remote):
        """Test creating a repository when it already exists."""
        with patch('wexample_helpers_api.common.abstract_gateway.AbstractGateway.make_request') as mock_request:
            mock_request.return_value.status_code = 200

            result = remote.create_repository_if_not_exists(
                f'https://{remote.domain}/{self.test_namespace}/{self.test_repo_name}.git'
            )

            mock_request.assert_called_once()
            self._assert_check_repository_exists_request(mock_request)
            assert result == {}

    def test_create_repository(self, remote):
        """Test creating a new repository."""
        with patch('wexample_helpers_api.common.abstract_gateway.AbstractGateway.make_request') as mock_request:
            mock_request.return_value.json.return_value = {'id': 1}

            result = remote.create_repository(
                name=self.test_repo_name,
                namespace=self.test_namespace,
                description=self.test_description,
                private=True
            )

            mock_request.assert_called_once()
            self._assert_create_repository_request(mock_request)
            assert result == {'id': 1}

    def _assert_check_repository_exists_request(self, mock_request):
        """Assert the request parameters for checking repository existence.
        To be implemented by child classes."""
        raise NotImplementedError()

    def _assert_create_repository_request(self, mock_request):
        """Assert the request parameters for creating a repository.
        To be implemented by child classes."""
        raise NotImplementedError()

    @property
    def test_repo_name(self) -> str:
        """Return the test repository name."""
        return 'test-repo'

    @property
    def test_namespace(self) -> str:
        """Return the test namespace."""
        return 'test-namespace'

    @property
    def test_description(self) -> str:
        """Return the test repository description."""
        return 'Test description'
