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

    def get_branch_pipelines(
        self,
        namespace: str,
        name: str,
        branch: str,
    ) -> list[dict[str, Any]]:
        project = self._project_endpoint(namespace, name)
        response = self.make_request(
            endpoint=f"{project}/pipelines",
            call_origin=__file__,
            expected_status_codes=[200],
            query_params={
                "ref": branch,
                "order_by": "id",
                "sort": "desc",
                "per_page": 5,
            },
            quiet=True,
        )
        return response.json() if response else []

    # ------------------------------------------------------------------
    # CI/CD variables
    # ------------------------------------------------------------------
    def get_ci_variable(self, namespace: str, name: str, key: str) -> dict | None:
        project = self._project_endpoint(namespace, name)
        response = self.make_request(
            endpoint=f"{project}/variables/{key}",
            call_origin=__file__,
            expected_status_codes=[200, 404],
            fatal_if_unexpected=False,
        )
        if response and response.status_code == 200:
            return response.json()
        return None

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
            quiet=True,
        )
        return response.json() if response else {}

    def merge_merge_proposal(
        self,
        namespace: str,
        name: str,
        proposal_id: int,
    ) -> dict[str, Any]:
        from wexample_api.enums.http import HttpMethod

        project = self._project_endpoint(namespace, name)
        # If the MR was already merged out-of-band (e.g. manually via the web
        # UI while we were polling), the PUT /merge endpoint returns 405. Check
        # the state first; if already merged, return the MR payload as success.
        mr_state = self._get_merge_proposal_state(project, proposal_id)
        if mr_state.get("state") == "merged":
            return mr_state
        if mr_state.get("state") == "closed":
            raise RuntimeError(
                f"MR !{proposal_id} is closed without being merged; cannot merge."
            )

        # GitLab needs a few seconds to finish its mergeability check after the
        # MR is created. Calling /merge while it's still in `checking` or
        # `unchecked` returns 405 Method Not Allowed. Poll until the MR is
        # confirmed mergeable (or until we hit a definitively-not-mergeable
        # state) before issuing the PUT.
        self._wait_for_mergeable(project, proposal_id)

        response = self.make_request(
            method=HttpMethod.PUT,
            endpoint=f"{project}/merge_requests/{proposal_id}/merge",
            data={},
            call_origin=__file__,
            expected_status_codes=[200],
            fatal_if_unexpected=True,
            retries=5,
        )
        return response.json()

    def _get_merge_proposal_state(self, project: str, proposal_id: int) -> dict[str, Any]:
        from wexample_api.enums.http import HttpMethod

        response = self.make_request(
            method=HttpMethod.GET,
            endpoint=f"{project}/merge_requests/{proposal_id}",
            call_origin=__file__,
            expected_status_codes=[200],
            quiet=True,
        )
        return response.json() if response else {}

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

    def set_ci_variable(
        self, namespace: str, name: str, key: str, value: str, masked: bool = True
    ) -> bool:
        from wexample_api.enums.http import HttpMethod

        project = self._project_endpoint(namespace, name)
        existing = self.get_ci_variable(namespace, name, key)

        if existing:
            response = self.make_request(
                method=HttpMethod.PUT,
                endpoint=f"{project}/variables/{key}",
                data={"value": value, "masked": masked, "protected": False},
                call_origin=__file__,
                expected_status_codes=[200],
                fatal_if_unexpected=False,
            )
            return response is not None and response.status_code == 200
        else:
            response = self.make_request(
                method=HttpMethod.POST,
                endpoint=f"{project}/variables",
                data={"key": key, "value": value, "masked": masked, "protected": False},
                call_origin=__file__,
                expected_status_codes=[201],
                fatal_if_unexpected=False,
            )
            return response is not None and response.status_code == 201

    def set_default_branch(self, namespace: str, name: str, branch_name: str) -> bool:
        from wexample_api.enums.http import HttpMethod

        project = self._project_endpoint(namespace, name)
        response = self.make_request(
            method=HttpMethod.PUT,
            endpoint=project,
            data={"default_branch": branch_name},
            call_origin=__file__,
            expected_status_codes=[200],
            fatal_if_unexpected=False,
        )
        return response is not None and response.status_code == 200

    # ------------------------------------------------------------------
    # Branch protection
    # ------------------------------------------------------------------
    def unprotect_branch(self, namespace: str, name: str, branch_name: str) -> bool:
        from wexample_api.enums.http import HttpMethod

        project = self._project_endpoint(namespace, name)
        response = self.make_request(
            method=HttpMethod.DELETE,
            endpoint=f"{project}/protected_branches/{branch_name}",
            call_origin=__file__,
            expected_status_codes=[204, 404],
            fatal_if_unexpected=False,
        )
        return response is not None and response.status_code in (204, 404)

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

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _project_endpoint(self, namespace: str, name: str) -> str:
        return f"projects/{namespace}%2F{name}"

    def _wait_for_mergeable(
        self,
        project: str,
        proposal_id: int,
        max_attempts: int = 12,
        delay_seconds: int = 5,
    ) -> None:
        from wexample_api.enums.http import HttpMethod
        from wexample_helpers.helpers.polling_callback_manager import (
            PollingCallbackManager,
        )

        # Terminal states where additional polling won't help; bail out and let
        # the merge call return its real error rather than wait the full budget.
        terminal_not_mergeable = {
            "not_open",
            "blocked_status",
            "broken_status",
            "draft_status",
            "discussions_not_resolved",
            "cannot_be_merged",
        }

        def check_status() -> str | None:
            response = self.make_request(
                method=HttpMethod.GET,
                endpoint=f"{project}/merge_requests/{proposal_id}",
                call_origin=__file__,
                expected_status_codes=[200],
                quiet=True,
            )
            mr = response.json() if response else {}
            # Prefer the newer detailed_merge_status when available; fall back
            # to the legacy merge_status field for older GitLab instances.
            status = mr.get("detailed_merge_status") or mr.get("merge_status")
            if status in ("mergeable", "can_be_merged"):
                return status
            if status in terminal_not_mergeable:
                # Stop polling; surface the real error from the merge call.
                return status
            return None

        try:
            PollingCallbackManager(
                callback=check_status,
                max_attempts=max_attempts,
                delay_seconds_callback=lambda _attempt: delay_seconds,
            ).run()
        except TimeoutError:
            # Fall through: let the merge call attempt anyway. Its own retry
            # may succeed if the check completes in the meantime.
            pass
