from typing import Type
from types import UnionType

from wexample_config.const.types import DictConfig
from wexample_filestate.option.abstract_item_option import AbstractItemOption


class GitOption(AbstractItemOption):
    @staticmethod
    def get_value_type() -> Type | UnionType:
        return dict | bool

    def should_have_git(self) -> bool:
        return self.value_should_have_git(self.value)

    @staticmethod
    def value_should_have_git(value) -> bool:
        return (value is True) or isinstance(value, dict)

    @classmethod
    def resolve_config(cls, config: DictConfig) -> DictConfig:
        from wexample_filestate.option.should_exist_option import ShouldExistOption

        if "git" in config and cls.value_should_have_git(config["git"]):
            config[ShouldExistOption.get_name()] = True
        return config
