from __future__ import annotations

from tests.common.abstract_main_branch_test import AbstractMainBranchTest


class TestMainBranchOptionList(AbstractMainBranchTest):
    """Test MainBranchOption with list value."""
    test_dir_name: str = "test-git-branch-list"
    expected_branch_name: str = "feature"  # First item from list
    main_branch_config: list = ["feature", "backup"]
