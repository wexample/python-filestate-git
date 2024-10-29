from __future__ import annotations

from typing import TYPE_CHECKING, Union, cast, Dict
from git import Repo
from wexample_filestate.operation.mixin.file_manipulation_operation_mixin import FileManipulationMixin
from wexample_filestate_git.operation.abstract_git_operation import AbstractGitOperation
from wexample_helpers.helpers.git_helper import git_remote_create_once

if TYPE_CHECKING:
    from wexample_filestate.item.file_state_item_directory_target import FileStateItemDirectoryTarget
    from wexample_filestate.item.file_state_item_file_target import FileStateItemFileTarget


class GitRemoteAddOperation(FileManipulationMixin, AbstractGitOperation):
    _original_path_str: str
    _created_remote: Dict[str, bool]

    def __init__(self, **data) -> None:
        super().__init__(**data)
        self._created_remote = {}

    @staticmethod
    def applicable(target: Union["FileStateItemDirectoryTarget", "FileStateItemFileTarget"]) -> bool:
        if AbstractGitOperation.applicable(target=target):
            from wexample_filestate_git.option.git_option import GitOption
            option = cast(GitOption, target.get_option(GitOption))

            return option and isinstance(option.value, dict) and "remote" in option.value

        return False

    def describe_before(self) -> str:
        return 'Remote missing in .git directory'

    def describe_after(self) -> str:
        return 'Remote added .git directory'

    def description(self) -> str:
        return 'Add remote in .git directory'

    def apply(self) -> None:
        from wexample_filestate_git.option.git_option import GitOption
        option = cast(GitOption, self.target.get_option(GitOption))

        for remote in option.value["remote"]:
            repo = self._get_target_git_repo()

            remote_name = self.target.config_parse_value(remote["name"])
            remote_url = self.target.config_parse_value(remote["url"])

            remote = git_remote_create_once(repo, remote_name, remote_url)
            self._created_remote[remote_name] = remote is not None

    def _get_target_git_repo(self) -> Repo:
        return Repo(self._get_target_file_path(target=self.target))

    def undo(self) -> None:
        from wexample_filestate_git.option.git_option import GitOption
        option = cast(GitOption, self.target.get_option(GitOption))

        for remote in option.value["remote"]:
            if self._created_remote:
                repo = self._get_target_git_repo()
                remote_name = self.target.config_parse_value(remote["name"])

                if self._created_remote[remote_name] is True:
                    repo.delete_remote(remote=repo.remote(name=remote_name))
