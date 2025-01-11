from typing import Optional

from wexample_config.const.types import DictConfig
from wexample_filestate.const.disk import DiskItemType
from wexample_filestate.testing.test_abstract_operation import TestAbstractOperation
from wexample_filestate_git.test.mixin.test_git_state_manager_mixin import TestGitFileStateManagerMixin
from wexample_helpers.helpers.directory import directory_remove_tree_if_exists


class TestGitRemoteAddOperation(TestGitFileStateManagerMixin, TestAbstractOperation):
    def _operation_test_setup_configuration(self) -> Optional[DictConfig]:
        directory_remove_tree_if_exists(self._get_absolute_path_from_state_manager('.git'))

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
        return 2

    def _operation_test_assert_initial(self) -> None:
        self._assert_dir_exists(self._get_git_dir_path("test_git_dir"), positive=False)

    def _operation_test_assert_applied(self) -> None:
        self._assert_dir_exists(self._get_git_dir_path("test_git_dir"))
