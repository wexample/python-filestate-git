from typing import Optional

from wexample_config.const.types import DictConfig
from wexample_filestate.const.disk import DiskItemType
from wexample_filestate.test.test_abstract_operation import TestAbstractOperation


class TestGitOperation(TestAbstractOperation):
    def _operation_test_setup_configuration(self) -> Optional[DictConfig]:
        return {
            'children': [
                {
                    'name': "test_git_dir",
                    'should_exist': True,
                    'type': DiskItemType.DIRECTORY,
                }
            ]
        }

    def _operation_get_count(self) -> int:
        return 1

    def _operation_test_assert_initial(self) -> None:
        self._assert_state_manager_target_directory_exists("test_git_dir", positive=False)

    def _operation_test_assert_applied(self) -> None:
        self._assert_state_manager_target_directory_exists("test_git_dir")