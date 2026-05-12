from __future__ import annotations

from wexample_helpers.decorator.base_class import base_class

from wexample_filestate_git.operation.abstract_git_operation import AbstractGitOperation
from wexample_filestate_git.remote.mixin.with_git_remote_mixin import WithGitRemoteMixin


@base_class
class GitDeleteRemoteBranchOperation(WithGitRemoteMixin, AbstractGitOperation):
    def __init__(
        self, option, target, branch_name: str, canonical_branch: str, description: str
    ) -> None:
        super().__init__(option=option, target=target, description=description)
        self.branch_name = branch_name
        self.canonical_branch = canonical_branch

    def apply_operation(self) -> None:
        repo = self._get_target_git_repo()

        for remote in repo.remotes:
            try:
                remote_heads = {ref.remote_head for ref in remote.refs}
            except Exception:
                continue

            if self.branch_name not in remote_heads:
                continue

            remote_url = next(iter(remote.urls), None)
            if remote_url:
                remote_type = self._detect_remote_type(remote_url)
                if remote_type:
                    try:
                        api_remote = self._build_remote_instance(remote_type, remote_url, self.target)
                        repo_info = api_remote.parse_repository_url(remote_url)
                        api_remote.unprotect_branch(repo_info["namespace"], repo_info["name"], self.branch_name)
                        api_remote.set_default_branch(repo_info["namespace"], repo_info["name"], self.canonical_branch)
                    except Exception as e:
                        self.target.log(
                            message=f"WARNING: could not prepare '{self.branch_name}' for deletion on {remote.name}: {e}"
                        )

            try:
                remote.push(refspec=f":{self.branch_name}")
            except Exception as e:
                self.target.log(
                    message=f"WARNING: could not delete '{self.branch_name}' on {remote.name}: {e}"
                )

    def undo(self) -> None:
        pass
