from __future__ import annotations

from types import UnionType
from typing import TYPE_CHECKING, Any

from wexample_config.config_option.abstract_nested_config_option import (
    AbstractNestedConfigOption,
)

if TYPE_CHECKING:
    from types import UnionType

    from wexample_config.const.types import DictConfig, DictConfigValue
    from wexample_config.options_provider.abstract_options_provider import (
        AbstractOptionsProvider,
    )


class GitConfigOption(AbstractNestedConfigOption):
    @classmethod
    def resolve_config(cls, config: DictConfig) -> DictConfig:
        from wexample_filestate.option.should_exist_option import (
            ShouldExistOption,
        )

        if GitConfigOption.get_name() in config and cls.dict_value_should_have_git(
            config[GitConfigOption.get_name()]
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
