from __future__ import annotations

from typing import TYPE_CHECKING, Any

from wexample_config.config_option.abstract_nested_config_option import (
    AbstractNestedConfigOption,
)
from wexample_filestate.option.mixin.option_mixin import OptionMixin
from wexample_helpers.decorator.base_class import base_class

if TYPE_CHECKING:
    from types import UnionType

    from wexample_config.const.types import DictConfig, DictConfigValue
    from wexample_config.options_provider.abstract_options_provider import (
        AbstractOptionsProvider,
    )
    from wexample_filestate.operation.abstract_operation import AbstractOperation
    from wexample_filestate.const.types_state_items import TargetFileOrDirectoryType


@base_class
class GitOption(OptionMixin, AbstractNestedConfigOption):
    @classmethod
    def resolve_config(cls, config: DictConfig) -> DictConfig:
        from wexample_filestate.option.should_exist_option import (
            ShouldExistOption,
        )

        if GitOption.get_name() in config and cls.dict_value_should_have_git(
            config[GitOption.get_name()]
        ):
            config[ShouldExistOption.get_name()] = True
        return config

    @staticmethod
    def dict_value_should_have_git(value: DictConfigValue) -> bool:
        return (value is True) or isinstance(value, dict)

    @staticmethod
    def get_raw_value_allowed_type() -> Any:
        return dict | bool

    @staticmethod
    def get_value_allowed_type() -> Any | type | UnionType:
        return dict | bool

    def get_options_providers(self) -> list[type[AbstractOptionsProvider]]:
        from wexample_filestate_git.options_provider.git_config_options_provider import (
            GitConfigOptionsProvider,
        )

        return [GitConfigOptionsProvider]

    def set_value(self, raw_value: Any) -> None:
        # Support True without config.
        if raw_value is True:
            raw_value = {}

        super().set_value(raw_value=raw_value)

    def should_have_git(self) -> bool:
        value = self.get_value()
        return (value.is_bool() and value.is_true()) or value.is_dict()

    def create_required_operation(self, target: TargetFileOrDirectoryType) -> AbstractOperation | None:
        """Create GitInitOperation if Git is required but not initialized."""
        from wexample_helpers_git.helpers.git import git_is_init
        
        # Check if Git is required
        if not self.should_have_git():
            return None
        
        # Check if target path exists (Git can only be initialized in existing directories)
        target_path = target.get_path()
        if not target_path.exists():
            return None
        
        # Check if Git is already initialized
        if git_is_init(target_path):
            return None
        
        # Create GitInitOperation
        from wexample_filestate_git.operation.git_init_operation import GitInitOperation
        
        return GitInitOperation(
            target=target
        )
