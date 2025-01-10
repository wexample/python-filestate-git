import os
import re
from typing import Dict, List
from pydantic import Field
from .abstract_remote import AbstractRemote

GITHUB_API_TOKEN: str = "GITHUB_API_TOKEN"
GITHUB_DEFAULT_URL: str = "GITHUB_DEFAULT_URL"


class GithubRemote(AbstractRemote):
    base_url: str = Field(
        default="https://api.github.com",
        description="GitHub API base URL"
    )

    def model_post_init(self, *args, **kwargs):
        super().model_post_init(*args, **kwargs)

        self.default_headers.update({
            "Authorization": f"token {os.getenv(GITHUB_API_TOKEN)}",
            "Accept": "application/vnd.github.v3+json"
        })

        if os.getenv(GITHUB_DEFAULT_URL) is not None:
            self.base_url = os.getenv(GITHUB_DEFAULT_URL)

    def get_expected_env_keys(self) -> List[str]:
        return [
            GITHUB_API_TOKEN,
        ]

    def create_repository(self, name: str, description: str = "", private: bool = False) -> Dict:
        response = self.make_request(
            method="POST",
            endpoint="user/repos",
            data={
                "name": name,
                "description": description,
                "private": private,
                "auto_init": True
            }
        )
        return response.json()

    def check_repository_exists(self, name: str, namespace: str = "") -> bool:
        try:
            # If namespace is provided, use it, otherwise search in user's repositories
            if namespace:
                endpoint = f"repos/{namespace}/{name}"
            else:
                endpoint = f"user/repos"
                params = {"per_page": 100}  # GitHub's default is 30
                response = self.make_request("GET", endpoint, params=params)
                repos = response.json()
                return any(repo["name"] == name for repo in repos)

            response = self.make_request("GET", endpoint)
            return response.status_code == 200

        except Exception as e:
            print(f"Error checking repository existence: {str(e)}")
            return False

    @classmethod
    def detect_remote_type(cls, remote_url: str) -> bool:
        github_patterns = [
            r"git@github\.com:",
            r"https://github\.com/",
            r"git://github\.com/"
        ]
        return any(re.search(pattern, remote_url) for pattern in github_patterns)
