from __future__ import annotations

from wexample_helpers.decorator.base_class import base_class

from wexample_filestate_git.operation.abstract_git_operation import AbstractGitOperation
from wexample_filestate_git.remote.mixin.with_git_remote_mixin import WithGitRemoteMixin


@base_class
class GitSyncCiVariablesOperation(WithGitRemoteMixin, AbstractGitOperation):
    def __init__(
        self,
        option,
        target,
        remote_url: str,
        namespace: str,
        repo_name: str,
        remote_type,
        variables: dict[str, str],
        description: str,
    ) -> None:
        super().__init__(option=option, target=target, description=description)
        self.remote_url = remote_url
        self.namespace = namespace
        self.repo_name = repo_name
        self.remote_type = remote_type
        self.variables = variables

    def apply_operation(self) -> None:
        from wexample_filestate_git.option._git.ci_variables_option import (
            _CI_VARIABLES_SYNCED_CACHE,
        )

        api_remote = self._build_remote_instance(
            self.remote_type, self.remote_url, self.target
        )

        for var_name, value in self.variables.items():
            try:
                success = api_remote.set_ci_variable(
                    self.namespace, self.repo_name, var_name, value, masked=True
                )
                if success:
                    _CI_VARIABLES_SYNCED_CACHE.add((self.remote_url, var_name))
                    self.target.log(
                        message=f"CI variable '{var_name}' synced on {self.namespace}/{self.repo_name}"
                    )
                else:
                    self.target.log(
                        message=f"WARNING: could not sync CI variable '{var_name}'"
                    )
            except Exception as e:
                self.target.log(
                    message=f"WARNING: could not sync CI variable '{var_name}': {e}"
                )

    def undo(self) -> None:
        pass
