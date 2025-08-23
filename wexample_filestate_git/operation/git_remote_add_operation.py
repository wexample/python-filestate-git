from __future__ import annotations

from pathlib import PosixPath
from typing import TYPE_CHECKING, Any, cast

from git import Repo
from wexample_filestate.operation.abstract_operation import AbstractOperation
from wexample_filestate.operation.mixin.file_manipulation_operation_mixin import (
    FileManipulationOperationMixin,
)
from wexample_filestate_git.operation.abstract_git_operation import AbstractGitOperation
from wexample_helpers_git.helpers.git import git_is_init, git_remote_create_once

if TYPE_CHECKING:
    from wexample_config.config_option.abstract_config_option import (
        AbstractConfigOption,
    )
    from wexample_filestate.const.types_state_items import TargetFileOrDirectoryType


class GitRemoteAddOperation(FileManipulationOperationMixin, AbstractGitOperation):
    _original_path_str: str
    _created_remote: dict[str, bool]

    def __init__(self, **data) -> None:
        super().__init__(**data)
        self._created_remote = {}

    def dependencies(self) -> list[type[AbstractOperation]]:
        from wexample_filestate_git.operation.git_init_operation import GitInitOperation

        if GitInitOperation.applicable(target=self.target):
            return [GitInitOperation]

        return []

    def applicable_operation(
        self, target: TargetFileOrDirectoryType, option: AbstractConfigOption
    ) -> bool:
        from wexample_filestate_git.config_option.git_config_option import (
            GitConfigOption,
        )
        from wexample_filestate_git.operation.git_init_operation import GitInitOperation

        if isinstance(option, GitConfigOption):
            if option.should_have_git() and (
                GitInitOperation.applicable_operation(target=target, option=option)
                or git_is_init(target.get_path())
            ):
                value = target.get_option_value(GitConfigOption)
                return value is not None and value.has_key_in_dict("remote")

        return False

    def describe_before(self) -> str:
        return "Remote missing in .git directory"

    def describe_after(self) -> str:
        return "Remote added in .git directory"

    def description(self) -> str:
        return "Add remote in .git directory"

    def apply(self) -> None:
        from wexample_filestate_git.config_option.git_config_option import (
            GitConfigOption,
        )

        value = self.target.get_option_value(GitConfigOption)

        if value.is_dict():
            for remote in value.get_dict().get("remote"):
                repo = self._get_target_git_repo()

                remote_name = self._config_parse_file_value(remote["name"])
                remote_url = self._config_parse_file_value(remote["url"])

                self._created_remote[remote_name] = (
                    git_remote_create_once(repo, remote_name, remote_url) is not None
                )

    def _config_parse_file_value(self, value: Any) -> str:
        if isinstance(value, str):
            return value
        elif isinstance(value, dict) and "pattern" in value:
            path = cast(PosixPath, self.target.get_path())

            return value["pattern"].format(**{"name": path.name, "path": str(path)})

        return value

    def _get_target_git_repo(self) -> Repo:
        return Repo(self._get_target_file_path(target=self.target))

    def undo(self) -> None:
        from wexample_filestate_git.config_option.git_config_option import (
            GitConfigOption,
        )

        option = cast(GitConfigOption, self.target.get_option(GitConfigOption))

        config = option.get_value().get_dict()
        for remote in config.get("remote"):
            if self._created_remote:
                repo = self._get_target_git_repo()
                remote_name = self._config_parse_file_value(remote["name"])

                if self._created_remote[remote_name] is True:
                    repo.delete_remote(remote=repo.remote(name=remote_name))
