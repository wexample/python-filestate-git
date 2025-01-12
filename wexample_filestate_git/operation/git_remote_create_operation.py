from __future__ import annotations

from pathlib import PosixPath
from typing import TYPE_CHECKING, cast, List, Type, Any, Optional

from wexample_filestate.operation.abstract_operation import AbstractOperation
from wexample_filestate.operation.mixin.file_manipulation_operation_mixin import FileManipulationOperationMixin
from wexample_filestate_git.operation.abstract_git_operation import AbstractGitOperation
from wexample_filestate_git.remote.abstract_remote import AbstractRemote
from wexample_filestate_git.remote.github_remote import GithubRemote
from wexample_filestate_git.remote.gitlab_remote import GitlabRemote
from wexample_prompt.mixins.with_required_io_manager import WithRequiredIoManager

if TYPE_CHECKING:
    from wexample_filestate.item.item_target_directory import TargetFileOrDirectoryType
    from wexample_config.config_option.abstract_config_option import AbstractConfigOption

class GitRemoteCreateOperation(WithRequiredIoManager, FileManipulationOperationMixin, AbstractGitOperation):
    @staticmethod
    def get_remote_types() -> List[Type[AbstractRemote]]:
        return [GithubRemote, GitlabRemote]

    def dependencies(self) -> List[Type["AbstractOperation"]]:
        from wexample_filestate_git.operation.git_remote_add_operation import GitRemoteAddOperation

        return [GitRemoteAddOperation]

    @staticmethod
    def applicable_option(target: "TargetFileOrDirectoryType", option: "AbstractConfigOption") -> bool:
        from wexample_filestate_git.config_option.git_config_option import GitConfigOption

        if isinstance(option, GitConfigOption):
            value = target.get_option_value(GitConfigOption)
            if (value is not None
                and value.is_dict()
                and value.get_dict().get("remote")):
                # Check if at least one remote has create_remote: true
                for remote in value.get_dict().get("remote"):
                    if remote.get("create_remote") is True:
                        return True

        return False

    def describe_before(self) -> str:
        return 'Remote repository not created on remote platform'

    def describe_after(self) -> str:
        return 'Remote repository created on remote platform'

    def description(self) -> str:
        return 'Create remote repository on platform'

    def _detect_remote_type(self, remote_url: str) -> Optional[Type[AbstractRemote]]:
        """
        Detect the remote type (GitHub, GitLab, etc.) from the URL.
        """
        for remote_type in self.get_remote_types():
            if remote_type.detect_remote_type(remote_url):
                return remote_type
        return None

    def apply(self) -> None:
        from wexample_filestate_git.config_option.git_config_option import GitConfigOption
        from wexample_helpers_git.const.common import GIT_PROVIDER_GITHUB, GIT_PROVIDER_GITLAB

        value = self.target.get_option_value(GitConfigOption)

        if value.is_dict():
            for remote in value.get_dict().get("remote"):
                if ("create_remote" in remote) and remote["create_remote"] is True:
                    remote_url = self._config_parse_file_value(remote["url"])

                    # Auto-detect remote type if not specified
                    if "type" in remote:
                        # Use specified type
                        type_map = {
                            GIT_PROVIDER_GITHUB: GithubRemote,
                            GIT_PROVIDER_GITLAB: GitlabRemote
                        }
                        remote_type = type_map.get(remote["type"].lower())
                    else:
                        # Auto-detect from URL
                        remote_type = self._detect_remote_type(remote_url)

                    if remote_type:
                        remote = remote_type(io_manager=self.io)
                        remote.connect()

                        # Create repository directly from URL
                        remote.create_repository_if_not_exists(remote_url)

    def _config_parse_file_value(self, value: Any) -> str:
        if isinstance(value, str):
            return value
        elif isinstance(value, dict) and "pattern" in value:
            path = cast(PosixPath, self.target.get_path())

            return value["pattern"].format(**{
                'name': path.name,
                'path': str(path)
            })

        return value

    def undo(self) -> None:
        # Note: We don't implement undo for remote repository creation
        # as it could be dangerous to automatically delete repositories
        pass
