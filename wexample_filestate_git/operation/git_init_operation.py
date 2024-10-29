from __future__ import annotations

from git import Repo

from wexample_filestate.operation.mixin.file_manipulation_operation_mixin import FileManipulationMixin
from wexample_filestate_git.operation.abstract_git_operation import AbstractGitOperation
from wexample_helpers.const.globals import DIR_GIT


class GitInitOperation(FileManipulationMixin, AbstractGitOperation):
    _original_path_str: str
    _has_initialized_git: bool = False

    def describe_before(self) -> str:
        return 'No initialized .git directory'

    def describe_after(self) -> str:
        return 'Initialized .git directory'

    def description(self) -> str:
        return 'Initialize .git directory'

    def apply(self) -> None:
        path = self._get_target_file_path(target=self.target)
        self._has_initialized_git = True

        repo = Repo.init(path)
        repo.init()

    def undo(self) -> None:
        import shutil

        shutil.rmtree(self._get_target_file_path(target=self.target) + DIR_GIT)
