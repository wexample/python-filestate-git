from __future__ import annotations

import re
from typing import Any

from wexample_helpers.classes.field import public_field
from wexample_helpers.decorator.base_class import base_class

from .abstract_remote import AbstractRemote


@base_class
class GithubRemote(AbstractRemote):
    api_token: str = public_field(description="GitHub API token")
    base_url: str = public_field(
        default="https://api.github.com", description="GitHub API base URL"
    )

    def __attrs_post_init__(self) -> None:
        self.default_headers.update(
            {
                "Authorization": f"token {self.api_token}",
                "Accept": "application/vnd.github.v3+json",
            }
        )

    # ------------------------------------------------------------------
    # Remote detection
    # ------------------------------------------------------------------

    @classmethod
    def build_remote_api_url_from_repo(cls, remote_url: str) -> str | None:
        """Build API base URL from a GitHub remote URL.

        Returns https://api.github.com for github.com,
        or https://{host}/api/v3 for GitHub Enterprise.
        """
        m = re.search(r"^(?:https://|git@)([^/:]+)", remote_url)
        if not m:
            return None
        host = m.group(1)
        return "https://api.github.com" if host == "github.com" else f"https://{host}/api/v3"

    @classmethod
    def detect_remote_type(cls, remote_url: str) -> bool:
        return bool(re.search(r"github\.com[:/]", remote_url))

    @classmethod
    def is_github_repo(cls, remote_url: str) -> bool:
        return bool(re.search(r"github\.com[:/]", remote_url))

    @classmethod
    def resolve_url_from_repo_url(cls, remote_url: str) -> str | None:
        """Normalize any GitHub remote URL into a clean HTTPS repository URL."""
        if not cls.is_github_repo(remote_url):
            return None
        m = re.search(r"github\.com[:/](.+?)(?:\.git)?$", remote_url)
        return f"https://github.com/{m.group(1)}" if m else None

    # ------------------------------------------------------------------
    # Repositories
    # ------------------------------------------------------------------

    def check_repository_exists(self, name: str, namespace: str) -> bool:
        response = self.make_request(
            endpoint=f"repos/{namespace}/{name}",
            call_origin=__file__,
            expected_status_codes=[200, 404],
            fatal_if_unexpected=True,
        )
        return response.status_code == 200

    def create_repository(
        self, name: str, namespace: str, description: str = "", private: bool = False
    ) -> dict:
        from wexample_api.enums.http import HttpMethod

        response = self.make_request(
            method=HttpMethod.POST,
            endpoint=f"orgs/{namespace}/repos",
            data={
                "name": name,
                "description": description,
                "private": private,
                "auto_init": True,
            },
            call_origin=__file__,
            expected_status_codes=[201],
            fatal_if_unexpected=True,
        )
        return response.json()

    def create_repository_if_not_exists(
        self, remote_url: str, description: str = "", private: bool = False
    ) -> dict:
        repo_info = self.parse_repository_url(remote_url)
        if not self.check_repository_exists(repo_info["name"], repo_info["namespace"]):
            return self.create_repository(
                name=repo_info["name"],
                namespace=repo_info["namespace"],
                description=description,
                private=private,
            )
        return {}

    def parse_repository_url(self, remote_url: str) -> dict[str, str]:
        path = re.sub(r"^(https://github\.com/|git@github\.com:)", "", remote_url)
        path = path.replace(".git", "")
        parts = path.split("/")
        if len(parts) >= 2:
            return {"name": parts[-1], "namespace": parts[-2]}
        return {"name": parts[0], "namespace": ""}

    # ------------------------------------------------------------------
    # Merge proposals (GitHub: pull requests)
    # ------------------------------------------------------------------

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
        from wexample_api.enums.http import HttpMethod

        response = self.make_request(
            endpoint=f"repos/{namespace}/{name}/pulls",
            query_params={"state": "open", "head": f"{namespace}:{source_branch}", "base": target_branch},
            call_origin=__file__,
            expected_status_codes=[200],
        )
        existing = response.json() if response else []
        if existing:
            return existing[0]

        response = self.make_request(
            method=HttpMethod.POST,
            endpoint=f"repos/{namespace}/{name}/pulls",
            data={
                "title": title,
                "head": source_branch,
                "base": target_branch,
            },
            call_origin=__file__,
            expected_status_codes=[201],
            fatal_if_unexpected=True,
        )
        return response.json()

    def get_merge_proposal_pipelines(
        self,
        namespace: str,
        name: str,
        proposal_id: int,
    ) -> list[dict[str, Any]]:
        """Return check runs for the PR head commit."""
        pr = self.make_request(
            endpoint=f"repos/{namespace}/{name}/pulls/{proposal_id}",
            call_origin=__file__,
            expected_status_codes=[200],
        )
        if not pr:
            return []
        head_sha = pr.json().get("head", {}).get("sha", "")
        if not head_sha:
            return []
        response = self.make_request(
            endpoint=f"repos/{namespace}/{name}/commits/{head_sha}/check-runs",
            call_origin=__file__,
            expected_status_codes=[200],
        )
        return response.json().get("check_runs", []) if response else []

    def merge_merge_proposal(
        self,
        namespace: str,
        name: str,
        proposal_id: int,
    ) -> dict[str, Any]:
        from wexample_api.enums.http import HttpMethod

        response = self.make_request(
            method=HttpMethod.PUT,
            endpoint=f"repos/{namespace}/{name}/pulls/{proposal_id}/merge",
            data={},
            call_origin=__file__,
            expected_status_codes=[200],
            fatal_if_unexpected=True,
        )
        return response.json()

    # ------------------------------------------------------------------
    # Pipelines (GitHub: workflow runs)
    # ------------------------------------------------------------------

    def get_pipeline(
        self,
        namespace: str,
        name: str,
        pipeline_id: int,
    ) -> dict[str, Any]:
        response = self.make_request(
            endpoint=f"repos/{namespace}/{name}/actions/runs/{pipeline_id}",
            call_origin=__file__,
            expected_status_codes=[200],
        )
        return response.json() if response else {}

    def _extract_pipeline_status(self, pipeline: dict[str, Any]) -> str:
        """GitHub: return conclusion when completed, otherwise status."""
        if pipeline.get("status") == "completed":
            return pipeline.get("conclusion") or "completed"
        return pipeline.get("status", "")

    def _is_pipeline_terminal(self, pipeline: dict[str, Any]) -> bool:
        return pipeline.get("status") == "completed"
