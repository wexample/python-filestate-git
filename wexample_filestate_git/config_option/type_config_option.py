from typing import Any

from wexample_config.config_option.abstract_config_option import AbstractConfigOption


class TypeConfigOption(AbstractConfigOption):
    @staticmethod
    def get_raw_value_allowed_type() -> Any:
        return str
