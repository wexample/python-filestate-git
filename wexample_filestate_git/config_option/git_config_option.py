from typing import Type, Any
from types import UnionType

from wexample_config.config_option.abstract_config_option import AbstractConfigOption
from wexample_config.const.types import DictConfig, DictConfigValue


class GitConfigOption(AbstractConfigOption):
    @staticmethod
    def get_value_allowed_type() -> Any | Type | UnionType:
        return dict | bool

    def should_have_git(self) -> bool:
        value = self.get_value()
        return (value.is_bool() and value.is_true()) or value.is_dict()

    @staticmethod
    def dict_value_should_have_git(value: DictConfigValue) -> bool:
        return (value is True) or isinstance(value, dict)

    @classmethod
    def resolve_config(cls, config: DictConfig) -> DictConfig:
        from wexample_filestate.config_option.should_exist_config_option import ShouldExistConfigOption

        if GitConfigOption.get_name() in config and cls.dict_value_should_have_git(config[GitConfigOption.get_name()]):
            config[ShouldExistConfigOption.get_name()] = True
        return config
