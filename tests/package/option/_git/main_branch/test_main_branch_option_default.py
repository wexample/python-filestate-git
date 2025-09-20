from __future__ import annotations

import sys
from pathlib import Path

from tests.common.abstract_main_branch_test import AbstractMainBranchTest


class TestMainBranchOptionDefault(AbstractMainBranchTest):
    """Test MainBranchOption with default 'main' branch."""
    test_dir_name: str = "test-git-branch-default"
    expected_branch_name: str = "main"
    main_branch_config: list = []  # Empty list should default to "main"
