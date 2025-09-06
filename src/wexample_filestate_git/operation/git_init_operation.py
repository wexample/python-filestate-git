from __future__ import annotations

from typing import TYPE_CHECKING

from wexample_filestate.operation.mixin.file_manipulation_operation_mixin import (
    FileManipulationOperationMixin,
)
from wexample_filestate_git.operation.abstract_git_operation import AbstractGitOperation

if TYPE_CHECKING:
    from wexample_config.config_option.abstract_config_option import (
        AbstractConfigOption,
    )
    from wexample_filestate.operation.abstract_operation import AbstractOperation


class GitInitOperation(FileManipulationOperationMixin, AbstractGitOperation):
    _has_initialized_git: bool = False

    def dependencies(self) -> list[type[AbstractOperation]]:
        from wexample_filestate.operation.file_create_operation import FileCreateOperation
        return [FileCreateOperation]

    def applicable_for_option(self, option: AbstractConfigOption) -> bool:
        from wexample_filestate_git.config_option.git_config_option import GitConfigOption
        from wexample_helpers_git.helpers.git import git_is_init

        if not self._is_active_git_option(option):
            return False

        assert isinstance(option, GitConfigOption)
        return option.should_have_git() and not git_is_init(self.target.get_path())

    def describe_before(self) -> str:
        return "No initialized .git directory"

    def describe_after(self) -> str:
        return "Initialized .git directory"

    def description(self) -> str:
        return "Initialize .git directory"

    def apply(self) -> None:
        from git import Repo
        path = self.target.get_path()
        self._has_initialized_git = True

        repo = Repo.init(path)
        repo.init()

    def undo(self) -> None:
        from wexample_helpers.const.globals import DIR_GIT
        import shutil

        if self._has_initialized_git:
            shutil.rmtree(self.target.get_path() / DIR_GIT)
