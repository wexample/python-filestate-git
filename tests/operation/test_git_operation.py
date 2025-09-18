from __future__ import annotations

from typing import TYPE_CHECKING

from wexample_config.const.types import DictConfig
from wexample_filestate.testing.abstract_test_operation import AbstractTestOperation
from wexample_filestate_git.test.mixin.test_git_state_manager_mixin import (
    TestGitFileStateManagerMixin,
)

if TYPE_CHECKING:
    from wexample_config.const.types import DictConfig


class TestGitOperation(TestGitFileStateManagerMixin, AbstractTestOperation):
    def _operation_get_count(self) -> int:
        return 1

    def _operation_test_assert_applied(self) -> None:
        self._assert_dir_exists(self._get_git_dir_path("test_git_dir"))

    def _operation_test_assert_initial(self) -> None:
        self._assert_dir_exists(self._get_git_dir_path("test_git_dir"), positive=False)

    def _operation_test_setup_configuration(self) -> DictConfig | None:
        from wexample_filestate.const.disk import DiskItemType

        self._remove_test_git_dir()

        return {
            "children": [
                {
                    "name": "test_git_dir",
                    "should_exist": True,
                    "type": DiskItemType.DIRECTORY,
                    "git": True,
                }
            ]
        }
