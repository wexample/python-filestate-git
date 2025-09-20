from __future__ import annotations

from typing import TYPE_CHECKING, cast

from wexample_filestate.operation.mixin.file_manipulation_operation_mixin import (
    FileManipulationOperationMixin,
)
from wexample_filestate_git.operation.abstract_git_operation import AbstractGitOperation

if TYPE_CHECKING:
    from wexample_config.config_option.abstract_config_option import (
        AbstractConfigOption,
    )
    from wexample_filestate.operation.abstract_operation import AbstractOperation
    from wexample_filestate_git.remote.abstract_remote import AbstractRemote


class GitRemoteCreateOperation(FileManipulationOperationMixin, AbstractGitOperation):
    @staticmethod
    def get_remote_types() -> list[type[AbstractRemote]]:
        from wexample_filestate_git.remote.github_remote import GithubRemote
        from wexample_filestate_git.remote.gitlab_remote import GitlabRemote

        return [GithubRemote, GitlabRemote]


    def apply(self) -> None:
        from wexample_filestate_git.option._git.create_remote_option import (
            CreateRemoteOption,
        )
        from wexample_filestate_git.option.git_option import (
            GitOption,
        )
        from wexample_filestate_git.option._git.remote_option import (
            RemoteOption,
        )
        from wexample_filestate_git.option._git.type_option import (
            TypeOption,
        )
        from wexample_filestate_git.option._git.url_option import (
            UrlOption,
        )
        from wexample_filestate_git.remote.github_remote import GithubRemote
        from wexample_filestate_git.remote.gitlab_remote import GitlabRemote
        from wexample_helpers_git.const.common import (
            GIT_PROVIDER_GITHUB,
            GIT_PROVIDER_GITLAB,
        )

        git_option = self.target.get_option(GitOption)
        git_option.get_value()

        if git_option:
            git_option = cast(GitOption, git_option)
            remote_option = cast(
                RemoteOption, git_option.get_option(RemoteOption)
            )

            if remote_option:
                for remote_item_option in remote_option.children:
                    remote_item_option = cast(
                        remote_option.get_item_class_type(), remote_item_option
                    )
                    create_remote_option = remote_item_option.get_option(
                        CreateRemoteOption
                    )
                    url_option = remote_item_option.get_option(UrlOption)
                    type_option = remote_item_option.get_option(TypeOption)

                    if (
                        create_remote_option
                        and create_remote_option.get_value().is_true()
                    ):
                        # Support strings or callables in the UrlConfigOption value
                        remote_url = self._build_str_value(url_option.get_value())

                        # Auto-detect remote type if not specified
                        if type_option:
                            # Use specified type
                            type_map = {
                                GIT_PROVIDER_GITHUB: GithubRemote,
                                GIT_PROVIDER_GITLAB: GitlabRemote,
                            }
                            remote_type = type_map.get(
                                type_option.get_value().get_str().lower()
                            )
                        else:
                            # Auto-detect from URL
                            remote_type = self._detect_remote_type(remote_url)

                        if remote_type:
                            remote_type.build_remote_api_url_from_repo(remote_url)
                            remote = self._build_remote_instance(
                                remote_type=remote_type, remote_url=remote_url
                            )
                            if remote:
                                remote.connect()
                                # Create repository directly from URL
                                remote.create_repository_if_not_exists(remote_url)


    def undo(self) -> None:
        # Note: We don't implement undo for remote repository creation
        # as it could be dangerous to automatically delete repositories
        pass

    def _build_remote_instance(
        self, remote_type: type[AbstractRemote], remote_url: str
    ) -> AbstractRemote | None:
        # Instantiate the proper remote with required constructor args
        # GithubRemote expects an api_token passed explicitly
        # We may find another way to pass tokens, with an option value.
        return remote_type(
            io=self.target.io,
            api_token=self.target.get_env_parameter(
                # GITHUB_API_TOKEN / GITLAB_API_TOKEN
                key=f"{remote_type.get_snake_short_class_name().upper()}_API_TOKEN"
            ),
            base_url=remote_type.build_remote_api_url_from_repo(remote_url),
        )

    def _create_remotes_description(self) -> str:
        from wexample_filestate_git.option._git.create_remote_option import (
            CreateRemoteOption,
        )
        from wexample_filestate_git.option.git_option import (
            GitOption,
        )
        from wexample_filestate_git.option._git.remote_option import (
            RemoteOption,
        )
        from wexample_filestate_git.option._git.type_option import (
            TypeOption,
        )
        from wexample_filestate_git.option._git.url_option import (
            UrlOption,
        )
        from wexample_filestate_git.remote.github_remote import GithubRemote
        from wexample_filestate_git.remote.gitlab_remote import GitlabRemote

        parts: list[str] = []

        git_option = self.target.get_option(GitOption)
        if not git_option:
            return ""
        remote_option = git_option.get_option(RemoteOption)
        if not remote_option:
            return ""

        for remote_item_option in remote_option.children:
            create_remote_option = remote_item_option.get_option(
                CreateRemoteOption
            )
            if not (
                create_remote_option and create_remote_option.get_value().is_true()
            ):
                continue

            url_option = remote_item_option.get_option(UrlOption)
            type_option = remote_item_option.get_option(TypeOption)

            remote_url = None
            remote_type_label = None

            if url_option:
                remote_url = self._build_str_value(url_option.get_value())

            if type_option:
                remote_type_label = type_option.get_value().get_str().lower()
            else:
                if remote_url:
                    detected = self._detect_remote_type(remote_url)
                    if detected is GithubRemote:
                        remote_type_label = "github"
                    elif detected is GitlabRemote:
                        remote_type_label = "gitlab"

            if remote_url and remote_type_label:
                parts.append(f"{remote_type_label}: {remote_url}")
            elif remote_url:
                parts.append(str(remote_url))
            elif remote_type_label:
                parts.append(str(remote_type_label))

        return ", ".join(parts)

    def _detect_remote_type(self, remote_url: str) -> type[AbstractRemote] | None:
        """
        Detect the remote type (GitHub, GitLab, etc.) from the URL.
        """
        for remote_type in self.get_remote_types():
            if remote_type.detect_remote_type(remote_url):
                return remote_type
        return None

    def _resolve_remote_type_and_url(self, remote_item_option):
        from wexample_filestate_git.option._git.type_option import (
            TypeOption,
        )
        from wexample_filestate_git.option._git.url_option import (
            UrlOption,
        )
        from wexample_filestate_git.remote.github_remote import GithubRemote
        from wexample_filestate_git.remote.gitlab_remote import GitlabRemote
        from wexample_helpers_git.const.common import (
            GIT_PROVIDER_GITHUB,
            GIT_PROVIDER_GITLAB,
        )

        url_option = remote_item_option.get_option(UrlOption)
        type_option = remote_item_option.get_option(TypeOption)

        if not url_option:
            return None

        remote_url = self._build_str_value(url_option.get_value())

        if type_option:
            type_map = {
                GIT_PROVIDER_GITHUB: GithubRemote,
                GIT_PROVIDER_GITLAB: GitlabRemote,
            }
            remote_type = type_map.get(type_option.get_value().get_str().lower())
        else:
            remote_type = self._detect_remote_type(remote_url)

        if not remote_type:
            return None

        return remote_type, remote_url
