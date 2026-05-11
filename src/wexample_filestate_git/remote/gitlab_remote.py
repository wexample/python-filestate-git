from __future__ import annotations

import re
from typing import Any

import requests
from wexample_helpers.classes.field import public_field
from wexample_helpers.decorator.base_class import base_class

from .abstract_remote import AbstractRemote


@base_class
class GitlabRemote(AbstractRemote):
    api_token: str = public_field(description="GitLab API token")
    base_url: str = public_field(
        default="https://gitlab.com/api/v4", description="GitLab API base URL"
    )

    def __attrs_post_init__(self) -> None:
        self.default_headers.update({"PRIVATE-TOKEN": self.api_token})

    # ------------------------------------------------------------------
    # Remote detection
    # ------------------------------------------------------------------

    @classmethod
    def build_remote_api_url_from_repo(cls, remote_url: str) -> str | None:
        """Build API base URL from a GitLab remote URL.

        Supports:
        - https://gitlab.example.com/owner/repo.git → https://gitlab.example.com/api/v4
        - ssh://git@gitlab.example.com:4567/owner/repo.git → https://gitlab.example.com/api/v4
        - git@gitlab.example.com:owner/repo.git → https://gitlab.example.com/api/v4
        """
        host = None
        for pattern in (
            r"^ssh://[^@]+@([^/:]+)",
            r"^git@([^:]+):",
            r"^https?://([^/]+)/",
        ):
            m = re.search(pattern, remote_url)
            if m:
                host = m.group(1)
                break
        return f"https://{host}/api/v4" if host else None

    @classmethod
    def detect_remote_type(cls, remote_url: str) -> bool:
        return bool(re.search(r"gitlab\.[a-zA-Z0-9.-]+[:/]", remote_url))

    # ------------------------------------------------------------------
    # Connectivity
    # ------------------------------------------------------------------

    def check_connection(self) -> bool:
        try:
            url = f"{self.base_url.rstrip('/')}/user"
            response = requests.head(
                url, headers=self.default_headers, timeout=self.timeout
            )
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False

    # ------------------------------------------------------------------
    # Repositories
    # ------------------------------------------------------------------

    def check_repository_exists(self, name: str, namespace: str) -> bool:
        response = self.make_request(
            endpoint=self._project_endpoint(namespace, name),
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
            endpoint="projects",
            data={
                "name": name,
                "path": name,
                "description": description,
                "visibility": "private" if private else "public",
                "initialize_with_readme": False,
                "namespace_id": self._get_namespace_id(namespace),
            },
            call_origin=__file__,
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
        if remote_url.startswith("git@"):
            path = remote_url.split(":", 1)[1]
        else:
            parts = remote_url.split("/", 3)
            path = parts[3] if len(parts) > 3 else ""
        path = path.replace(".git", "")
        url_parts = path.split("/")
        if len(url_parts) >= 2:
            return {"name": url_parts[-1], "namespace": url_parts[-2]}
        return {"name": url_parts[0], "namespace": ""}

    # ------------------------------------------------------------------
    # Merge proposals (GitLab: merge requests)
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

        project = self._project_endpoint(namespace, name)

        response = self.make_request(
            endpoint=f"{project}/merge_requests",
            query_params={
                "source_branch": source_branch,
                "target_branch": target_branch,
                "state": "opened",
            },
            call_origin=__file__,
            expected_status_codes=[200],
        )
        existing = response.json() if response else []
        if existing:
            return existing[0]

        response = self.make_request(
            method=HttpMethod.POST,
            endpoint=f"{project}/merge_requests",
            data={
                "source_branch": source_branch,
                "target_branch": target_branch,
                "title": title,
                "remove_source_branch": remove_source_branch,
                "squash": squash,
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
        project = self._project_endpoint(namespace, name)
        response = self.make_request(
            endpoint=f"{project}/merge_requests/{proposal_id}/pipelines",
            call_origin=__file__,
            expected_status_codes=[200],
        )
        return response.json() if response else []

    def merge_merge_proposal(
        self,
        namespace: str,
        name: str,
        proposal_id: int,
    ) -> dict[str, Any]:
        from wexample_api.enums.http import HttpMethod

        project = self._project_endpoint(namespace, name)
        response = self.make_request(
            method=HttpMethod.PUT,
            endpoint=f"{project}/merge_requests/{proposal_id}/merge",
            data={},
            call_origin=__file__,
            expected_status_codes=[200],
            fatal_if_unexpected=True,
        )
        return response.json()

    # ------------------------------------------------------------------
    # Pipelines
    # ------------------------------------------------------------------

    def get_pipeline(
        self,
        namespace: str,
        name: str,
        pipeline_id: int,
    ) -> dict[str, Any]:
        project = self._project_endpoint(namespace, name)
        response = self.make_request(
            endpoint=f"{project}/pipelines/{pipeline_id}",
            call_origin=__file__,
            expected_status_codes=[200],
        )
        return response.json() if response else {}

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _project_endpoint(self, namespace: str, name: str) -> str:
        return f"projects/{namespace}%2F{name}"

    def _get_namespace_id(self, namespace_path: str) -> int | None:
        try:
            response = requests.get(
                f"{self.base_url.rstrip('/')}/namespaces",
                params={"search": namespace_path},
                headers=self.default_headers,
                timeout=self.timeout,
            )
            if response.status_code == 200:
                for ns in response.json():
                    if ns["path"] == namespace_path:
                        return ns["id"]
            return None
        except requests.exceptions.RequestException:
            return None
