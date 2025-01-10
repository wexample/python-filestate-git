import os
import re
from typing import Dict, List, Optional
from pydantic import Field
import requests

from .abstract_remote import AbstractRemote


GITLAB_API_TOKEN: str = "GITLAB_API_TOKEN"
GITLAB_DEFAULT_URL: str = "GITLAB_DEFAULT_URL"


class GitlabRemote(AbstractRemote):
    base_url: str = Field(
        default="https://gitlab.com/api/v4",
        description="GitLab API base URL"
    )

    def model_post_init(self, *args, **kwargs):
        super().model_post_init(*args, **kwargs)

        self.default_headers.update({
            "PRIVATE-TOKEN": os.getenv(GITLAB_API_TOKEN)
        })

        if os.getenv(GITLAB_DEFAULT_URL) is not None:
            self.base_url = os.getenv(GITLAB_DEFAULT_URL)

    def get_expected_env_keys(self) -> List[str]:
        return [
            GITLAB_API_TOKEN,
        ]

    def create_repository(self, name: str, namespace: str = "", description: str = "", private: bool = False) -> Dict:
        data = {
            "name": name,
            "path": name,
            "description": description,
            "visibility": "private" if private else "public",
            "initialize_with_readme": False
        }
        
        if namespace:
            data["namespace_id"] = self._get_namespace_id(namespace)

        response = self.make_request(
            method="POST",
            endpoint="projects",
            data=data
        )
        return response.json()

    def check_connection(self) -> bool:
        try:
            url = f"{self.base_url.rstrip('/')}/user"

            response = requests.head(
                url,
                headers=self.default_headers,
                timeout=self.timeout
            )

            return response.status_code == 200

        except requests.exceptions.RequestException as e:
            print(f"Connection error: {str(e)}")
            return False

    def check_repository_exists(self, name: str, namespace: str = "") -> bool:
        try:
            if namespace:
                response = requests.get(
                    f"{self.base_url.rstrip('/')}/projects",
                    params={
                        "search": name,
                        "namespace": namespace
                    },
                    headers=self.default_headers,
                    timeout=self.timeout
                )
                if response.status_code == 200:
                    projects = response.json()
                    return any(
                        p["path"] == name and p["namespace"]["path"] == namespace 
                        for p in projects
                    )
            return False
        except requests.exceptions.RequestException:
            return False

    def _get_namespace_id(self, namespace_path: str) -> Optional[int]:
        try:
            response = requests.get(
                f"{self.base_url.rstrip('/')}/namespaces",
                params={"search": namespace_path},
                headers=self.default_headers,
                timeout=self.timeout
            )
            if response.status_code == 200:
                namespaces = response.json()
                for ns in namespaces:
                    if ns["path"] == namespace_path:
                        return ns["id"]
            return None
        except requests.exceptions.RequestException:
            return None

    @classmethod
    def detect_remote_type(cls, remote_url: str) -> bool:
        return bool(re.search(r'gitlab\.com[:/]', remote_url))

    def parse_repository_url(self, remote_url: str) -> Dict[str, str]:
        """
        Parse a GitLab repository URL to extract repository information.
        Supports both HTTPS and SSH URLs:
        - https://gitlab.com/owner/repo.git
        - git@gitlab.com:owner/repo.git
        """
        # Remove protocol and domain
        path = re.sub(r'^(https://gitlab\.com/|git@gitlab\.com:)', '', remote_url)
        # Remove .git suffix if present
        path = path.replace('.git', '')
        
        parts = path.split('/')
        if len(parts) >= 2:
            return {
                'name': parts[-1],
                'namespace': parts[-2]
            }
        return {
            'name': parts[0],
            'namespace': ''
        }