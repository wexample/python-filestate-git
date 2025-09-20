from __future__ import annotations

from typing import Any

from pydantic import ConfigDict

from wexample_config.config_value.config_value import ConfigValue
from wexample_filestate.option.name_option import NameOption
from wexample_filestate_git.option._git.create_remote_option import CreateRemoteOption
from wexample_filestate_git.option._git.type_option import TypeOption
from wexample_filestate_git.option._git.url_option import UrlOption
from wexample_filestate.option.active_option import ActiveOption
from wexample_helpers.classes.field import public_field
from wexample_helpers.decorator.base_class import base_class


@base_class
class RemoteConfigValue(ConfigValue):
    raw: Any = public_field(
        default=None, description="Disabled raw value for this config."
    )
    name: str | None = public_field(
        default=None,
        description="Name of the remote (e.g., 'origin')",
    )
    url: str | None = public_field(
        default=None,
        description="URL of the remote repository",
    )
    type: str | None = public_field(
        default=None,
        description="Type of remote (github, gitlab, etc.)",
    )
    create_remote: bool | None = public_field(
        default=None,
        description="Whether to create the remote repository if it doesn't exist",
    )
    active: bool | None = public_field(
        default=None,
        description="Whether this remote is active",
    )

    def to_option_raw_value(self) -> ConfigDict:
        return {
            NameOption.get_name(): self.name,
            UrlOption.get_name(): self.url,
            TypeOption.get_name(): self.type,
            CreateRemoteOption.get_name(): self.create_remote,
            ActiveOption.get_name(): self.active,
        }
