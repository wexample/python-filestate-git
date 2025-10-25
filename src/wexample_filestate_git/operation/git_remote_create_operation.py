from __future__ import annotations

from typing import TYPE_CHECKING

from wexample_filestate.operation.abstract_file_manipulation_operation import (
    AbstractFileManipulationOperation,
)
from wexample_helpers.decorator.base_class import base_class

if TYPE_CHECKING:
    from wexample_filestate_git.remote.abstract_remote import AbstractRemote


@base_class
class GitRemoteCreateOperation(AbstractFileManipulationOperation):
    def __init__(
        self,
        target,
        remote_type: type[AbstractRemote],
        remote_url: str,
        api_token: str | None = None,
    ) -> None:
        super().__init__(target=target)
        self.remote_type = remote_type
        self.remote_url = remote_url
        self.api_token = api_token

    @staticmethod
    def get_remote_types() -> list[type[AbstractRemote]]:
        from wexample_filestate_git.remote.github_remote import GithubRemote
        from wexample_filestate_git.remote.gitlab_remote import GitlabRemote

        return [GithubRemote, GitlabRemote]

    def apply(self) -> None:
        """Create the remote repository using the configured parameters."""
        # Build remote instance with the provided parameters
        remote = self._build_remote_instance()
        if remote:
            remote.connect()
            # Create repository directly from URL
            remote.create_repository_if_not_exists(self.remote_url)

    def undo(self) -> None:
        # Note: We don't implement undo for remote repository creation
        # as it could be dangerous to automatically delete repositories
        pass

    def _build_remote_instance(self) -> AbstractRemote | None:
        """Build remote instance with the configured parameters."""
        # Instantiate the proper remote with required constructor args
        return self.remote_type(
            io=self.target.io,
            api_token=self.api_token,
            base_url=self.remote_type.build_remote_api_url_from_repo(self.remote_url),
        )

    def _create_remotes_description(self) -> str:
        """Generate description for this remote creation operation."""
        from wexample_filestate_git.remote.github_remote import GithubRemote
        from wexample_filestate_git.remote.gitlab_remote import GitlabRemote

        # Determine remote type label
        remote_type_label = "unknown"
        if self.remote_type is GithubRemote:
            remote_type_label = "github"
        elif self.remote_type is GitlabRemote:
            remote_type_label = "gitlab"

        return f"{remote_type_label}: {self.remote_url}"
