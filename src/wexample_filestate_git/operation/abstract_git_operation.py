from __future__ import annotations

from abc import ABC

from wexample_filestate.enum.scopes import Scope
from wexample_filestate.operation.abstract_operation import AbstractOperation


class AbstractGitOperation(AbstractOperation, ABC):
    @classmethod
    def get_scope(cls) -> Scope:
        return Scope.LOCATION
