from __future__ import annotations

from wexample_helpers.decorator.base_class import base_class

from wexample_filestate_git.operation.abstract_git_operation import AbstractGitOperation


@base_class
class GitMergeBranchOperation(AbstractGitOperation):
    def __init__(
        self, option, target, from_branch: str, to_branch: str, description: str
    ) -> None:
        super().__init__(option=option, target=target, description=description)
        self.from_branch = from_branch
        self.to_branch = to_branch

    def apply_operation(self) -> None:
        repo = self._get_target_git_repo()

        to_branch = next((h for h in repo.heads if h.name == self.to_branch), None)
        from_branch = next((h for h in repo.heads if h.name == self.from_branch), None)
        if not to_branch or not from_branch:
            return

        to_branch.checkout()
        repo.git.merge(self.from_branch, "--no-edit")
        repo.delete_head(self.from_branch, force=False)

        self._sync_remote(repo)

    def _sync_remote(self, repo) -> None:
        for remote in repo.remotes:
            try:
                remote.push()
            except Exception as e:
                self.target.log(
                    message=f"WARNING: could not push '{self.to_branch}' to {remote.name}: {e}"
                )

            try:
                remote.push(refspec=f":{self.from_branch}")
            except Exception as e:
                self.target.log(
                    message=f"WARNING: could not delete '{self.from_branch}' on {remote.name}: {e}"
                )

    def undo(self) -> None:
        pass
