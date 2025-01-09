from __future__ import annotations

from pathlib import PosixPath
from typing import TYPE_CHECKING, cast, Dict, List, Type, Any, Optional
from git import Repo

from wexample_filestate.operation.abstract_operation import AbstractOperation
from wexample_filestate.operation.mixin.file_manipulation_operation_mixin import FileManipulationOperationMixin
from wexample_filestate_git.operation.abstract_git_operation import AbstractGitOperation
from wexample_helpers_git.helpers.git import git_remote_create_once, git_is_init
from wexample_filestate_git.remote.github_remote import GithubRemote, GITHUB_API_TOKEN
from wexample_filestate_git.remote.gitlab_remote import GitlabRemote, GITLAB_API_TOKEN
from wexample_filestate_git.remote.abstract_remote import AbstractRemote

if TYPE_CHECKING:
    from wexample_filestate.const.types_state_items import TargetFileOrDirectoryType


class GitRemoteOperation(FileManipulationOperationMixin, AbstractGitOperation):
    _original_path_str: str
    _created_remote: Dict[str, bool]
    _remote_types: List[Type[AbstractRemote]] = [GithubRemote, GitlabRemote]

    def __init__(self, **data) -> None:
        super().__init__(**data)
        self._created_remote = {}

    def dependencies(self) -> List[Type["AbstractOperation"]]:
        from wexample_filestate_git.operation.git_init_operation import GitInitOperation

        if GitInitOperation.applicable(target=self.target):
            return [
                GitInitOperation
            ]

        return []

    @staticmethod
    def applicable(target: "TargetFileOrDirectoryType") -> bool:
        from wexample_filestate_git.config_option.git_config_option import GitConfigOption
        from wexample_filestate_git.operation.git_init_operation import GitInitOperation

        option = cast(GitConfigOption, target.get_option(GitConfigOption))

        if option is not None and option.should_have_git() and (
            GitInitOperation.applicable(target=target) or git_is_init(target.get_path())):
            value = target.get_option_value(GitConfigOption)

            return (value is not None
                    and value.is_dict()
                    and value.get_dict().get("remote"))

        return False

    def describe_before(self) -> str:
        return 'Remote missing in .git directory'

    def describe_after(self) -> str:
        return 'Remote added in .git directory'

    def description(self) -> str:
        return 'Add remote in .git directory'

    def _detect_remote_type(self, remote_url: str) -> Optional[Type[AbstractRemote]]:
        """
        Detect the remote type (GitHub, GitLab, etc.) from the URL.
        """
        for remote_type in self._remote_types:
            if remote_type.detect_remote_type(remote_url):
                return remote_type
        return None

    def apply(self) -> None:
        from wexample_filestate_git.config_option.git_config_option import GitConfigOption
        value = self.target.get_option_value(GitConfigOption)

        if value.is_dict():
            for remote in value.get_dict().get("remote"):
                repo = self._get_target_git_repo()

                remote_name = self._config_parse_file_value(remote["name"])
                remote_url = self._config_parse_file_value(remote["url"])

                self._created_remote[remote_name] = git_remote_create_once(repo, remote_name, remote_url) is not None

                if ("create_remote" in remote) and remote["create_remote"] is True:
                    from wexample_helpers_git.const.common import GIT_PROVIDER_GITHUB, GIT_PROVIDER_GITLAB

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
                        remote = remote_type()
                        remote.connect()

                        # Parse the repository name and path from the URL
                        # Example URL: ssh://git@gitlab.wexample.com:4567/acme-python/app.git
                        url_parts = remote_url.split('/')
                        repo_full_name = '/'.join(url_parts[-2:])  # Get "acme-python/app.git"
                        repo_name = repo_full_name.split('/')[-1].replace('.git', '')  # Get "app"
                        namespace = repo_full_name.split('/')[0] if '/' in repo_full_name else ""

                        if not remote.check_repository_exists(repo_name, namespace):
                            remote.create_repository(
                                name=repo_name,
                                namespace=namespace
                            )

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

    def _get_target_git_repo(self) -> Repo:
        return Repo(self._get_target_file_path(target=self.target))

    def undo(self) -> None:
        from wexample_filestate_git.config_option.git_config_option import GitConfigOption
        option = cast(GitConfigOption, self.target.get_option(GitConfigOption))

        config = option.get_value().get_dict()
        for remote in config.get("remote"):
            if self._created_remote:
                repo = self._get_target_git_repo()
                remote_name = self._config_parse_file_value(remote["name"])

                if self._created_remote[remote_name] is True:
                    repo.delete_remote(remote=repo.remote(name=remote_name))
