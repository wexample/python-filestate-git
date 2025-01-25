from types import UnionType
from typing import Type, Any, List

# TODO from wexample_config.config_option.abstract_list_config_option import AbstractListConfigOption
from wexample_config.config_option.config_option import ConfigOption


class RemoteConfigOption(ConfigOption):
    @staticmethod
    def get_raw_value_allowed_type() -> Any:
        return List[dict[str, Any]]

    @staticmethod
    def get_allowed_types() -> Type | UnionType:
        return List[dict[str, Any]]