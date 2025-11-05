from __future__ import annotations

from typing import TYPE_CHECKING, Any, Union

from wexample_config.config_option.abstract_list_config_option import (
    AbstractListConfigOption,
)

from wexample_filestate.enum.scopes import Scope
from wexample_filestate.option.mixin.option_mixin import OptionMixin
from wexample_helpers.decorator.base_class import base_class

if TYPE_CHECKING:
    from types import UnionType

    from wexample_filestate.const.types_state_items import TargetFileOrDirectoryType
    from wexample_filestate.operation.abstract_operation import AbstractOperation


@base_class
class RemoteOption(OptionMixin, AbstractListConfigOption):
    @staticmethod
    def get_raw_value_allowed_type() -> Any:
        return Union[list, dict]

    def create_required_operation(
        self, target: TargetFileOrDirectoryType, scopes: set[Scope]
    ) -> AbstractOperation | None:
        """Create GitRemoteCreateOperation or GitRemoteAddOperation as needed."""
        from wexample_filestate_git.option._git.create_remote_option import (
            CreateRemoteOption,
        )
        from wexample_filestate_git.option._git.url_option import UrlOption

        # First priority: Check if any remote repository needs to be created
        for remote_item_option in self.children:
            # Check if creation is enabled
            create_remote_option = remote_item_option.get_option(CreateRemoteOption)
            create_enabled = (
                create_remote_option is not None
                and create_remote_option.get_value().is_true()
            )

            if create_enabled:
                # Check if we have URL
                url_option = remote_item_option.get_option(UrlOption)
                if url_option:
                    # Resolve type and url
                    resolved = self._resolve_remote_type_and_url(
                        remote_item_option, target
                    )
                    if resolved:
                        remote_type, remote_url = resolved
                        # Check if remote repository exists
                        remote = self._build_remote_instance(
                            remote_type=remote_type,
                            remote_url=remote_url,
                            target=target,
                        )
                        if remote:
                            remote.connect()
                            repo_info = remote.parse_repository_url(remote_url)
                            if not remote.check_repository_exists(
                                repo_info["name"], repo_info["namespace"]
                            ):
                                # Create operation with all necessary parameters
                                from wexample_filestate_git.operation.git_remote_create_operation import (
                                    GitRemoteCreateOperation,
                                )

                                api_token_env_key = f"{remote_type.get_snake_short_class_name().upper()}_API_TOKEN"
                                api_token = target.get_env_parameter_or_suite_fallback(
                                    api_token_env_key
                                )

                                if not api_token:
                                    from wexample_filestate.exception.missing_env_variable_exception import (
                                        MissingEnvVariableException,
                                    )

                                    raise MissingEnvVariableException(
                                        message=f"Missing required environment variable: {api_token_env_key}",
                                        env_key=api_token_env_key,
                                    )

                                return GitRemoteCreateOperation(
                                    option=self,
                                    description=f"The remote should exist: {remote_url}",
                                    target=target,
                                    remote_type=remote_type,
                                    remote_url=remote_url,
                                    api_token=api_token,
                                )

        # Second priority: Check if any remote needs to be added locally
        if self._is_remote_missing_or_mismatched(target):
            from wexample_filestate_git.operation.git_remote_add_operation import (
                GitRemoteAddOperation,
            )

            # Collect all remotes that need to be added
            remotes_to_add = []
            for remote_item_option in self.children:
                url_option = remote_item_option.get_option(UrlOption)
                if url_option:
                    remote_url = url_option.get_url(target=target)
                    # For remote add, we need a name - use "origin" as default or derive from URL
                    remote_name = self._get_remote_name(remote_item_option)
                    if remote_name and remote_url:
                        remotes_to_add.append({"name": remote_name, "url": remote_url})

            if remotes_to_add:
                return GitRemoteAddOperation(
                    option=self, target=target, remotes=remotes_to_add
                )

        return None

    def get_item_class_type(self) -> type | UnionType:
        from wexample_filestate_git.option._git.remote_item_option import (
            RemoteItemOption,
        )

        return RemoteItemOption

    def _build_remote_instance(self, remote_type, remote_url: str, target):
        """Build remote instance with proper configuration."""
        api_token_env_key = (
            f"{remote_type.get_snake_short_class_name().upper()}_API_TOKEN"
        )
        api_token = target.get_env_parameter_or_suite_fallback(api_token_env_key)

        if not api_token:
            from wexample_filestate.exception.missing_env_variable_exception import (
                MissingEnvVariableException,
            )

            raise MissingEnvVariableException(
                message=f"Missing required environment variable: {api_token_env_key}",
                env_key=api_token_env_key,
            )

        return remote_type(
            io=target.io,
            api_token=api_token,
            base_url=remote_type.build_remote_api_url_from_repo(remote_url),
        )

    def _detect_remote_type(self, remote_url: str):
        """Detect the remote type (GitHub, GitLab, etc.) from the URL."""
        from wexample_filestate_git.remote.github_remote import GithubRemote
        from wexample_filestate_git.remote.gitlab_remote import GitlabRemote

        remote_types = [GithubRemote, GitlabRemote]

        for remote_type in remote_types:
            if remote_type.detect_remote_type(remote_url):
                return remote_type
        return None

    def _get_remote_name(self, remote_item_option) -> str:
        """Get remote name from option or default to 'origin'."""
        from wexample_filestate.option.name_option import NameOption

        name_option = remote_item_option.get_option(NameOption)
        if name_option and name_option.get_value().is_str():
            return name_option.get_value().get_str()

        # Default to "origin" if no name specified
        return "origin"

    def _get_target_git_repo(self, target):
        """Get Git repository for the target."""
        try:
            from git import Repo
            from wexample_helpers.const.globals import DIR_GIT

            git_dir = target.get_path() / DIR_GIT
            if git_dir.exists():
                return Repo(str(target.get_path()))
        except Exception:
            pass
        return None

    def _has_remotes_configured(self) -> bool:
        """Check if there are any remotes configured."""
        from wexample_filestate_git.option._git.url_option import UrlOption

        for remote_item_option in self.children:
            url_option = remote_item_option.get_option(UrlOption)
            if url_option:
                return True

        return False

    def _is_remote_missing_or_mismatched(self, target) -> bool:
        """Check if any configured remote is missing locally or has different URL."""
        from wexample_filestate_git.option._git.url_option import UrlOption

        # Check if Git repo exists
        repo = self._get_target_git_repo(target)
        if not repo:
            # If no Git repo but remotes are configured, they need to be added later
            return self._has_remotes_configured()

        # Git repo exists, check if remotes match
        # Get existing remotes by name
        existing_by_name = {r.name: r for r in repo.remotes}

        for remote_item_option in self.children:
            url_option = remote_item_option.get_option(UrlOption)
            if not url_option:
                continue

            desired_name = self._get_remote_name(remote_item_option)
            desired_url = url_option.get_url(target=target)

            if not desired_name or not desired_url:
                continue

            existing = existing_by_name.get(desired_name)
            if existing is None:
                return True  # Remote missing

            # Check if URL matches
            existing_urls = {u for u in existing.urls}
            if desired_url not in existing_urls:
                return True  # URL mismatch

        return False

    def _resolve_remote_type_and_url(
        self, remote_item_option, target: TargetFileOrDirectoryType
    ):
        """Resolve remote type and URL from remote item option."""
        from wexample_helpers_git.const.common import (
            GIT_PROVIDER_GITHUB,
            GIT_PROVIDER_GITLAB,
        )

        from wexample_filestate_git.option._git.type_option import TypeOption
        from wexample_filestate_git.option._git.url_option import UrlOption
        from wexample_filestate_git.remote.github_remote import GithubRemote
        from wexample_filestate_git.remote.gitlab_remote import GitlabRemote

        url_option = remote_item_option.get_option(UrlOption)
        type_option = remote_item_option.get_option(TypeOption)

        if not url_option:
            return None

        remote_url = url_option.get_url(target=target)

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
