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
        gitlab_patterns = [
            r"git@gitlab\.com:",
            r"https://gitlab\.com/",
            r"git://gitlab\.com/"
        ]
        return any(re.search(pattern, remote_url) for pattern in gitlab_patterns)