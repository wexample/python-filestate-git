from typing import Optional, List, Type, TYPE_CHECKING

if TYPE_CHECKING:
    from wexample_config.options_provider.abstract_options_provider import AbstractOptionsProvider
    from wexample_filestate.operations_provider.abstract_operations_provider import AbstractOperationsProvider


class TestGitFileStateManagerMixin:
    def _get_test_operations_providers(self) -> Optional[List[Type["AbstractOperationsProvider"]]]:
        from wexample_filestate.operations_provider.default_operations_provider import DefaultOperationsProvider
        from wexample_filestate_git.operations_provider.git_operations_provider import GitOperationsProvider

        return [
            DefaultOperationsProvider,
            GitOperationsProvider
        ]

    def _get_test_options_providers(self) -> Optional[List[Type["AbstractOptionsProvider"]]]:
        from wexample_filestate.options_provider.default_options_provider import DefaultOptionsProvider
        from wexample_filestate_git.options_provider.git_options_provider import GitOptionsProvider

        return [
            DefaultOptionsProvider,
            GitOptionsProvider
        ]
