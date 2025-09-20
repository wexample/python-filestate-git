from __future__ import annotations

from tests.common.abstract_git_option_test import AbstractGitOptionTest


class TestGitOptionDict(AbstractGitOptionTest):
    """Test GitOption with dict value on existing directory."""
    test_dir_name: str = "test_git_dir"
    git_config: dict = {}  # Empty dict
    should_directory_exist_initially: bool = True  # Directory already exists
