from __future__ import annotations

from typing import Any

from wexample_config.config_value.config_value import ConfigValue
from wexample_helpers.classes.field import public_field
from wexample_helpers.decorator.base_class import base_class


@base_class
class BranchDesignConfigValue(ConfigValue):
    aliases: list[str] | None = public_field(
        default=None,
        description="Branch names that should be reconciled into this branch",
    )
    on_alias_conflict: str | None = public_field(
        default="merge",
        description="What to do when both the canonical branch and an alias exist: merge, skip, error",
    )
    raw: Any = public_field(
        default=None, description="Disabled raw value for this config."
    )
