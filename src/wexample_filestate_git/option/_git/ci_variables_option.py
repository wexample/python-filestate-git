from __future__ import annotations

from typing import TYPE_CHECKING, Any

from wexample_config.config_option.abstract_config_option import AbstractConfigOption
from wexample_filestate.enum.scopes import Scope
from wexample_filestate.option.mixin.option_mixin import OptionMixin
from wexample_filestate_git.remote.mixin.with_git_remote_mixin import WithGitRemoteMixin
from wexample_helpers.decorator.base_class import base_class

if TYPE_CHECKING:
    from wexample_filestate.const.types_state_items import TargetFileOrDirectoryType
    from wexample_filestate.operation.abstract_operation import AbstractOperation

# Process-level cache: (remote_url, var_name) pairs confirmed in sync this run.
# Safe to cache permanently — a variable that matches won't un-match during the same run.
_CI_VARIABLES_SYNCED_CACHE: set[tuple[str, str]] = set()


@base_class
class CiVariablesOption(WithGitRemoteMixin, OptionMixin, AbstractConfigOption):
    @classmethod
    def get_scopes(cls) -> list[Scope]:
        return [Scope.REMOTE]

    @staticmethod
    def get_raw_value_allowed_type() -> Any:
        return list

    def create_required_operation(
        self, target: TargetFileOrDirectoryType, scopes: set[Scope]
    ) -> AbstractOperation | None:
        value = self.get_value()
        var_names: list[str] = [v.get_str() for v in value.get_list_or_empty()]
        if not var_names:
            return None

        repo = self._get_target_git_repo(target)
        if not repo or not repo.remotes:
            return None

        remote = repo.remotes[0]
        remote_url = next(iter(remote.urls), None)
        if not remote_url:
            return None

        remote_type = self._detect_remote_type(remote_url)
        if not remote_type:
            return None

        try:
            api_remote = self._build_remote_instance(remote_type, remote_url, target)
            repo_info = api_remote.parse_repository_url(remote_url)
        except Exception as e:
            target.log(message=f"WARNING: could not connect to remote API: {e}")
            return None

        vars_to_sync: dict[str, str] = {}

        for var_name in var_names:
            cache_key = (remote_url, var_name)
            if cache_key in _CI_VARIABLES_SYNCED_CACHE:
                continue

            local_value = target.get_env_parameter_or_suite_fallback(var_name)
            if not local_value:
                target.log(message=f"WARNING: {var_name} not found in local env, skipping")
                continue

            existing = api_remote.get_ci_variable(repo_info["namespace"], repo_info["name"], var_name)
            if existing and existing.get("value") == local_value:
                _CI_VARIABLES_SYNCED_CACHE.add(cache_key)
                continue

            vars_to_sync[var_name] = local_value

        if not vars_to_sync:
            return None

        from wexample_filestate_git.operation.git_sync_ci_variables_operation import (
            GitSyncCiVariablesOperation,
        )

        return GitSyncCiVariablesOperation(
            option=self,
            target=target,
            remote_url=remote_url,
            namespace=repo_info["namespace"],
            repo_name=repo_info["name"],
            remote_type=remote_type,
            variables=vars_to_sync,
            description=f"Sync CI variables: {', '.join(vars_to_sync)}",
        )

    def _get_target_git_repo(self, target: TargetFileOrDirectoryType):
        try:
            from git import Repo
            from wexample_helpers.const.globals import DIR_GIT

            git_dir = target.get_path() / DIR_GIT
            if git_dir.exists():
                return Repo(str(target.get_path()))
        except Exception:
            pass
        return None
