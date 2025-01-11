from typing import Optional

from wexample_config.const.types import DictConfig
from wexample_filestate.const.disk import DiskItemType
from wexample_filestate.testing.test_abstract_operation import TestAbstractOperation
from wexample_filestate_git.test.mixin.test_git_state_manager_mixin import TestGitFileStateManagerMixin


class TestGitOperation(TestGitFileStateManagerMixin, TestAbstractOperation):
    def _operation_test_setup_configuration(self) -> Optional[DictConfig]:
        return {
            'children': [
                {
                    'name': "test_git_dir",
                    'should_exist': True,
                    'type': DiskItemType.DIRECTORY,
                    'git': {
                        "remote": [
                            {
                                "name": "github",
                                "url": {
                                    "pattern": "test-remote-with-{name}"
                                },
                            },
                        ]
                    }
                }
            ]
        }

    def _operation_get_count(self) -> int:
        return 3

    def _operation_test_assert_initial(self) -> None:
        self._assert_state_manager_target_directory_exists("test_git_dir", positive=False)

    def _operation_test_assert_applied(self) -> None:
        self._assert_state_manager_target_directory_exists("test_git_dir")
