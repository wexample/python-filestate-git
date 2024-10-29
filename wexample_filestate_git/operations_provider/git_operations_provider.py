from typing import List, Type, TYPE_CHECKING

from wexample_filestate.operations_provider.abstract_operations_provider import AbstractOperationsProvider

if TYPE_CHECKING:
    from wexample_filestate.operation.abstract_operation import AbstractOperation


class GitOperationsProvider(AbstractOperationsProvider):
    @staticmethod
    def get_operations() -> List[Type["AbstractOperation"]]:
        from wexample_filestate_git.operation.git_init_operation import GitInitOperation
        from wexample_filestate_git.operation.git_remote_add_operation import GitRemoteAddOperation

        return [
            GitInitOperation,
            GitRemoteAddOperation
        ]
