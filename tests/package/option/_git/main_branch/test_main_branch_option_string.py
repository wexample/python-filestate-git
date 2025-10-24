from __future__ import annotations

from wexample_filestate_git.testing.abstract_main_branch_test import (
    AbstractMainBranchTest,
)


class TestMainBranchOptionString(AbstractMainBranchTest):
    """Test MainBranchOption with string value - only tests branch creation."""

    test_dir_name: str = "test-git-branch-string"
    expected_branch_name: str = "develop"
    main_branch_config: str = "develop"
