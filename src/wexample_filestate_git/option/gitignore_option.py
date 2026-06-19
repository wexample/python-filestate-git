from __future__ import annotations

from typing import TYPE_CHECKING

from wexample_filestate.option.abstract_file_content_option import (
    AbstractFileContentOption,
)
from wexample_helpers.decorator.base_class import base_class

if TYPE_CHECKING:
    from wexample_filestate.const.types_state_items import TargetFileOrDirectoryType


@base_class
class GitignoreOption(AbstractFileContentOption):
    """Reorganize a `.gitignore`: dedup + sort within blank-line sections.

    Draft / safe-mode: the rectifier bails (returns content unchanged) on any
    file containing globs (`*`, `?`, `[`) or negations (`!`) since those are
    order-sensitive. The full version covering globs needs section-aware
    ordering rules and is out of scope for v1.
    """

    def get_description(self) -> str:
        return "Reorganize .gitignore: dedup + alphabetical sort within sections (safe-mode: skips files with * or !)."

    def _apply_content_change(self, target: TargetFileOrDirectoryType) -> str:
        from wexample_helpers_git.helper.gitignore import reorganize_gitignore_safe

        src = target.get_local_file().read()
        rewritten = reorganize_gitignore_safe(src)
        return src if rewritten is None else rewritten
