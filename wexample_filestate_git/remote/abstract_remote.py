from abc import abstractmethod
from typing import Dict, Optional
from wexample_helpers.classes.abstract_gateway import AbstractGateway


class AbstractRemote(AbstractGateway):
    """
    Abstract base class for Git repository hosting services (GitHub, GitLab, etc.).
    Provides a common interface for interacting with remote repositories.
    """

    @abstractmethod
    def create_repository(self, name: str, description: str = "", private: bool = False) -> Dict:
        """
        Create a new repository on the remote service.

        Args:
            name: Repository name
            description: Repository description
            private: Whether the repository should be private

        Returns:
            Dict: Repository information from the API
        """
        pass

    @abstractmethod
    def check_repository_exists(self, name: str, namespace: str = "") -> bool:
        """
        Check if a repository exists on the remote service.

        Args:
            name: Repository name
            namespace: Repository namespace/organization (optional)

        Returns:
            bool: True if the repository exists
        """
        pass

    @classmethod
    @abstractmethod
    def detect_remote_type(cls, remote_url: str) -> bool:
        """
        Detect if a remote URL corresponds to this service.

        Args:
            remote_url: Git remote URL to check

        Returns:
            bool: True if the URL matches this service's pattern
        """
        pass