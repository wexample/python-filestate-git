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
                    'git': True
                }
            ]
        }

    def _operation_get_count(self) -> int:
        return 1

    def _operation_test_assert_initial(self) -> None:
        path = f"{self.state_manager.find_by_name_or_fail('test_git_dir').get_resolved()}.git/"
        self._assert_dir_exists(path, positive=False)

    def _operation_test_assert_applied(self) -> None:
        path = f"{self.state_manager.find_by_name_or_fail('test_git_dir').get_resolved()}.git/"
        self._assert_dir_exists(path)
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
                    'git': True
                }
            ]
        }

    def _operation_get_count(self) -> int:
        return 1

    def _operation_test_assert_initial(self) -> None:
        path = f"{self.state_manager.find_by_name_or_fail('test_git_dir').get_resolved()}.git/"
        self._assert_dir_exists(path, positive=False)

    def _operation_test_assert_applied(self) -> None:
        path = f"{self.state_manager.find_by_name_or_fail('test_git_dir').get_resolved()}.git/"
        self._assert_dir_exists(path)
