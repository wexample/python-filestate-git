from __future__ import annotations

from abc import ABC

from wexample_filestate.enum.scopes import Scope
from wexample_filestate.operation.abstract_operation import AbstractOperation


class AbstractGitOperation(AbstractOperation, ABC):
    @classmethod
    def get_scope(cls) -> Scope:
        return Scope.REMOTE

    # Shared Git helpers
    def _get_target_git_repo(self):
        """Return the GitPython Repo for the target path."""
        from git import Repo

        return Repo(self.target.get_path())
