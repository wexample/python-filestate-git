from __future__ import annotations

from typing import TYPE_CHECKING, Any

from wexample_config.config_option.abstract_config_option import AbstractConfigOption
from wexample_filestate.enum.scopes import Scope
from wexample_filestate.option.mixin.option_mixin import OptionMixin
from wexample_helpers.decorator.base_class import base_class

if TYPE_CHECKING:
    from wexample_filestate.const.types_state_items import TargetFileOrDirectoryType
    from wexample_filestate.operation.abstract_operation import AbstractOperation


@base_class
class BranchesOption(OptionMixin, AbstractConfigOption):
    @classmethod
    def get_scopes(cls) -> list[Scope]:
        return [Scope.REMOTE]

    @staticmethod
    def get_raw_value_allowed_type() -> Any:
        return dict

    def create_required_operation(
        self, target: TargetFileOrDirectoryType, scopes: set[Scope]
    ) -> AbstractOperation | None:
        repo = self._get_target_git_repo(target)
        if not repo:
            return None

        existing_branches = {h.name for h in repo.heads}
        value = self.get_value()
        raw = value.get_dict_or_empty()

        for canonical, config in raw.items():
            if not isinstance(config, dict):
                continue

            aliases: list[str] = config.get("aliases", [])
            if not isinstance(aliases, list):
                aliases = []
            on_conflict: str = config.get("on_alias_conflict", "merge")
            canonical_exists = canonical in existing_branches

            for alias in aliases:
                if alias not in existing_branches:
                    continue

                if not canonical_exists:
                    from wexample_filestate_git.operation.git_rename_branch_operation import (
                        GitRenameBranchOperation,
                    )

                    return GitRenameBranchOperation(
                        option=self,
                        target=target,
                        from_branch=alias,
                        to_branch=canonical,
                        description=f"Rename branch '{alias}' → '{canonical}'",
                    )

                # Both exist
                if on_conflict == "merge":
                    from wexample_filestate_git.operation.git_merge_branch_operation import (
                        GitMergeBranchOperation,
                    )

                    return GitMergeBranchOperation(
                        option=self,
                        target=target,
                        from_branch=alias,
                        to_branch=canonical,
                        description=f"Merge '{alias}' into '{canonical}' and remove alias",
                    )

                if on_conflict == "error":
                    raise ValueError(
                        f"Both '{alias}' and '{canonical}' exist — manual resolution required."
                    )

                # skip: nothing to do

        return None

    def _get_target_git_repo(self, target: TargetFileOrDirectoryType):
        try:
            from git import Repo
            from wexample_helpers.const.globals import DIR_GIT

            git_dir = target.get_path() / DIR_GIT
            if git_dir.exists():
                return Repo(str(target.get_path()))
        except Exception:
            pass
        return None
