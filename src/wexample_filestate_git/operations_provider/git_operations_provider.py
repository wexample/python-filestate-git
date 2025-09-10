from __future__ import annotations

from typing import TYPE_CHECKING

from wexample_filestate.operations_provider.abstract_operations_provider import (
    AbstractOperationsProvider,
)

if TYPE_CHECKING:
    from wexample_filestate.operation.abstract_operation import AbstractOperation


class GitOperationsProvider(AbstractOperationsProvider):
    @staticmethod
    def get_operations() -> list[type[AbstractOperation]]:
        from wexample_filestate_git.operation.git_create_branch_operation import (
            GitCreateBranchOperation,
        )
        from wexample_filestate_git.operation.git_init_operation import GitInitOperation
        from wexample_filestate_git.operation.git_remote_add_operation import (
            GitRemoteAddOperation,
        )
        from wexample_filestate_git.operation.git_remote_create_operation import (
            GitRemoteCreateOperation,
        )

        return [
            # filestate: python-iterable-sort
            GitCreateBranchOperation,
            GitInitOperation,
            GitRemoteAddOperation,
            GitRemoteCreateOperation,
        ]
