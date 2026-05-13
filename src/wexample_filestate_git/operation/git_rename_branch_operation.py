from __future__ import annotations

from wexample_helpers.decorator.base_class import base_class

from wexample_filestate_git.operation.abstract_git_operation import AbstractGitOperation
from wexample_filestate_git.remote.mixin.with_git_remote_mixin import WithGitRemoteMixin


@base_class
class GitRenameBranchOperation(WithGitRemoteMixin, AbstractGitOperation):
    def __init__(
        self, option, target, from_branch: str, to_branch: str, description: str
    ) -> None:
        super().__init__(option=option, target=target, description=description)
        self.from_branch = from_branch
        self.to_branch = to_branch

    def apply_operation(self) -> None:
        repo = self._get_target_git_repo()

        if any(h.name == self.to_branch for h in repo.heads):
            return  # Already done

        branch = next((h for h in repo.heads if h.name == self.from_branch), None)
        if not branch:
            return

        was_active = repo.active_branch.name == self.from_branch
        branch.rename(self.to_branch)

        if was_active:
            repo.heads[self.to_branch].checkout()

        self._sync_remote(repo)

    def undo(self) -> None:
        pass

    def _sync_remote(self, repo) -> None:
        for remote in repo.remotes:
            try:
                remote.push(refspec=f"{self.to_branch}:{self.to_branch}")
            except Exception as e:
                self.target.log(
                    message=f"WARNING: could not push '{self.to_branch}' to {remote.name}: {e}"
                )
                continue

            remote_url = next(iter(remote.urls), None)
            if remote_url:
                remote_type = self._detect_remote_type(remote_url)
                if remote_type:
                    try:
                        api_remote = self._build_remote_instance(
                            remote_type, remote_url, self.target
                        )
                        repo_info = api_remote.parse_repository_url(remote_url)
                        api_remote.unprotect_branch(
                            repo_info["namespace"], repo_info["name"], self.from_branch
                        )
                        api_remote.set_default_branch(
                            repo_info["namespace"], repo_info["name"], self.to_branch
                        )
                    except Exception as e:
                        self.target.log(
                            message=f"WARNING: could not prepare '{self.from_branch}' for deletion on {remote.name}: {e}"
                        )

            try:
                remote.push(refspec=f":{self.from_branch}")
            except Exception as e:
                self.target.log(
                    message=f"WARNING: could not delete '{self.from_branch}' on {remote.name}: {e}"
                )
