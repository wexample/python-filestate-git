import re
from typing import Dict, List
from pydantic import Field

from .abstract_remote import AbstractRemote


GITHUB_ENV_KEY_TOKEN: str = "GITHUB_API_TOKEN"
GITHUB_API_VERSION: str = "application/vnd.github.v3+json"
GITHUB_DEFAULT_URL: str = "https://api.github.com"


class GithubRemote(AbstractRemote):
    base_url: str = Field(
        default=GITHUB_DEFAULT_URL,
        description="GitHub API base URL"
    )

    def model_post_init(self, *args, **kwargs):
        super().model_post_init(*args, **kwargs)
        token = self.get_api_key(GITHUB_ENV_KEY_TOKEN)
        self.default_headers.update({
            "Authorization": f"token {token}",
            "Accept": GITHUB_API_VERSION
        })

    def get_expected_env_keys(self) -> List[str]:
        return [
            GITHUB_ENV_KEY_TOKEN,
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