from __future__ import annotations

import time
from typing import Any, Callable

from wexample_api.common.abstract_gateway import AbstractGateway
from wexample_helpers.classes.abstract_method import abstract_method


class AbstractRemote(AbstractGateway):
    """
    Abstract base class for Git repository hosting services (GitHub, GitLab, etc.).
    Provides a common interface for interacting with remote repositories and CI pipelines.
    """

    # ------------------------------------------------------------------
    # Remote detection
    # ------------------------------------------------------------------

    @classmethod
    @abstract_method
    def build_remote_api_url_from_repo(cls, remote_url: str) -> str | None:
        """Derive the REST API base URL from a git remote URL.

        Implementations should support both SSH and HTTPS remotes and custom domains.
        Return None to use the class default base_url.
        """

    @classmethod
    @abstract_method
    def detect_remote_type(cls, remote_url: str) -> bool:
        """Return True if the URL matches this service's pattern."""

    @classmethod
    def get_class_name_suffix(cls) -> str | None:
        return "Remote"

    # ------------------------------------------------------------------
    # Repositories
    # ------------------------------------------------------------------

    @abstract_method
    def check_repository_exists(self, name: str, namespace: str) -> bool:
        """Return True if the repository exists on the remote service."""

    @abstract_method
    def create_repository(
        self, name: str, namespace: str, description: str = "", private: bool = False
    ) -> dict:
        """Create a new repository on the remote service."""

    @abstract_method
    def create_repository_if_not_exists(
        self, remote_url: str, description: str = "", private: bool = False
    ) -> dict:
        """Create a repository from a complete remote URL if it doesn't exist."""

    @abstract_method
    def parse_repository_url(self, remote_url: str) -> dict[str, str]:
        """Parse a repository URL to extract ``name`` and ``namespace``."""

    # ------------------------------------------------------------------
    # Merge proposals (MR on GitLab, PR on GitHub)
    # ------------------------------------------------------------------

    @abstract_method
    def create_merge_proposal(
        self,
        namespace: str,
        name: str,
        source_branch: str,
        target_branch: str,
        title: str,
        remove_source_branch: bool = True,
        squash: bool = False,
    ) -> dict[str, Any]:
        """Create a MR/PR or return the existing open one (idempotent).

        Returns the proposal dict. The provider-specific identifier
        (``iid`` on GitLab, ``number`` on GitHub) is accessible via
        ``get_merge_proposal_id()``.
        """

    @abstract_method
    def get_merge_proposal_pipelines(
        self,
        namespace: str,
        name: str,
        proposal_id: int,
    ) -> list[dict[str, Any]]:
        """Return the pipelines/checks associated with a MR/PR."""

    @abstract_method
    def merge_merge_proposal(
        self,
        namespace: str,
        name: str,
        proposal_id: int,
    ) -> dict[str, Any]:
        """Merge a MR/PR."""

    def get_merge_proposal_id(self, proposal: dict[str, Any]) -> int:
        """Extract the provider-specific numeric identifier from a proposal dict."""
        return proposal.get("iid") or proposal.get("number")

    # ------------------------------------------------------------------
    # Pipelines / workflow runs
    # ------------------------------------------------------------------

    @abstract_method
    def get_pipeline(
        self,
        namespace: str,
        name: str,
        pipeline_id: int,
    ) -> dict[str, Any]:
        """Return the pipeline/workflow-run dict for the given ID."""

    def poll_pipeline(
        self,
        namespace: str,
        name: str,
        pipeline_id: int,
        timeout: int = 600,
        interval: int = 10,
        on_tick: Callable[[str, int], None] | None = None,
    ) -> str:
        """Poll until a terminal status is reached. Returns the final status string."""
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            pipeline = self.get_pipeline(namespace, name, pipeline_id)
            status = self._extract_pipeline_status(pipeline)
            elapsed = int(timeout - (deadline - time.monotonic()))
            if on_tick:
                on_tick(status, elapsed)
            if self._is_pipeline_terminal(pipeline):
                return status
            time.sleep(interval)
        raise TimeoutError(
            f"Pipeline {pipeline_id} did not complete within {timeout}s"
        )

    def _extract_pipeline_status(self, pipeline: dict[str, Any]) -> str:
        """Extract the human-readable status string from a pipeline dict."""
        return pipeline.get("status", "")

    def _is_pipeline_terminal(self, pipeline: dict[str, Any]) -> bool:
        """Return True if the pipeline has reached a terminal state."""
        return self._extract_pipeline_status(pipeline) in {
            "success", "failed", "canceled", "skipped",
        }
