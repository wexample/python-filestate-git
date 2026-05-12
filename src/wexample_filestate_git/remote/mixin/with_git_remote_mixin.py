from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from wexample_filestate_git.remote.abstract_remote import AbstractRemote


class WithGitRemoteMixin:
    @staticmethod
    def _detect_remote_type(remote_url: str):
        from wexample_filestate_git.remote.github_remote import GithubRemote
        from wexample_filestate_git.remote.gitlab_remote import GitlabRemote

        for remote_type in [GithubRemote, GitlabRemote]:
            if remote_type.detect_remote_type(remote_url):
                return remote_type
        return None

    @staticmethod
    def _get_api_token(remote_type, target) -> str:
        api_token_env_key = f"{remote_type.get_snake_short_class_name().upper()}_API_TOKEN"
        api_token = target.get_env_parameter_or_suite_fallback(api_token_env_key)

        if not api_token:
            from wexample_filestate.exception.missing_env_variable_exception import (
                MissingEnvVariableException,
            )

            raise MissingEnvVariableException(
                message=f"Missing required environment variable: {api_token_env_key}",
                env_key=api_token_env_key,
            )

        return api_token

    @staticmethod
    def _build_remote_instance(remote_type, remote_url: str, target) -> AbstractRemote | None:
        api_token = WithGitRemoteMixin._get_api_token(remote_type, target)

        return remote_type(
            io=target.io,
            api_token=api_token,
            base_url=remote_type.build_remote_api_url_from_repo(remote_url),
        )
