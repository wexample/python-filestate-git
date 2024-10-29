from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING, Union, cast
from wexample_filestate.operation.abstract_operation import AbstractOperation

if TYPE_CHECKING:
    from wexample_filestate.item.file_state_item_directory_target import FileStateItemDirectoryTarget
    from wexample_filestate.item.file_state_item_file_target import FileStateItemFileTarget


class AbstractGitOperation(AbstractOperation, ABC):
    @staticmethod
    def applicable(target: Union["FileStateItemDirectoryTarget", "FileStateItemFileTarget"]) -> bool:
        from wexample_filestate_git.option.git_option import GitOption
        from wexample_helpers.helpers.git_helper import git_is_init

        option = cast(GitOption, target.get_option(GitOption))

        return option and option.should_have_git() and not git_is_init(target.path)
