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

    @classmethod
    def detect_remote_type(cls, remote_url: str) -> bool:
        github_patterns = [
            r"git@github\.com:",
            r"https://github\.com/",
            r"git://github\.com/"
        ]
        return any(re.search(pattern, remote_url) for pattern in github_patterns)
