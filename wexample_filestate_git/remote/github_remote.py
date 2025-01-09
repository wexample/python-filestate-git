import re
from typing import Dict, List, Optional
from pydantic import Field

from .abstract_remote import AbstractRemote


class GithubRemote(AbstractRemote):
    base_url: str = Field(
        default="https://api.github.com",
        description="GitHub API base URL"
    )

    def model_post_init(self, *args, **kwargs):
        super().model_post_init(*args, **kwargs)
        if self.api_keys.get("token"):
            self.default_headers.update({
                "Authorization": f"token {self.api_keys['token']}",
                "Accept": "application/vnd.github.v3+json"
            })

    def get_expected_env_keys(self) -> List[str]:
        return ["token"]

    def create_repository(self, name: str, description: str = "", private: bool = False) -> Dict:
        response = self.make_request(
            method="POST",
            endpoint="user/repos",
            data={
                "name": name,
                "description": description,
                "private": private
            }
        )
        return response.json()

    @classmethod
    def detect_remote_type(cls, remote_url: str) -> bool:
        github_patterns = [
            r"git@github\.com:",
            r"https://github\.com/",
            r"git://github\.com/",
            r"gitlab"
        ]
        return any(re.search(pattern, remote_url) for pattern in github_patterns)