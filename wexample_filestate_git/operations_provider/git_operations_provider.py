from typing import List, Type, TYPE_CHECKING

from wexample_filestate.operations_provider.abstract_operations_provider import AbstractOperationsProvider
from wexample_helpers.helpers.import_helper import import_dummy

if TYPE_CHECKING:
    from wexample_filestate.operation.abstract_operation import AbstractOperation


class GitOperationsProvider(AbstractOperationsProvider):
    @staticmethod
    def get_operations() -> List[Type["AbstractOperation"]]:
        from wexample_filestate_git.operation.git_init_operation import GitInitOperation
        from wexample_filestate_git.operation.git_remote_operation import GitRemoteOperation
        from wexample_filestate.const.state_items import TargetFileOrDirectory

        import_dummy(TargetFileOrDirectory)

        GitRemoteOperation.model_rebuild()

        return [
            GitInitOperation,
            GitRemoteOperation
        ]
