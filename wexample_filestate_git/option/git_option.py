from typing import Type
from types import UnionType

from wexample_config.const.types import DictConfig, DictConfigValue
from wexample_filestate.option.abstract_item_option import AbstractItemOption


class GitOption(AbstractItemOption):
    @staticmethod
    def get_value_type() -> Type | UnionType:
        return dict | bool

    def should_have_git(self) -> bool:
        return (self.value.is_bool() and self.value.is_true()) or self.value.is_dict()

    @staticmethod
    def dict_value_should_have_git(value: DictConfigValue) -> bool:
        return (value is True) or isinstance(value, dict)

    @classmethod
    def resolve_config(cls, config: DictConfig) -> DictConfig:
        from wexample_filestate.option.should_exist_option import ShouldExistOption

        if GitOption.get_name() in config and cls.dict_value_should_have_git(config[GitOption.get_name()]):
            config[ShouldExistOption.get_name()] = True
        return config
