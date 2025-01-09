import re
from typing import Dict, List, Optional
from pydantic import Field

from .abstract_remote import AbstractRemote


class GitlabRemote(AbstractRemote):
    base_url: str = Field(
        default="https://gitlab.com/api/v4",
        description="GitLab API base URL"
    )

    def model_post_init(self, *args, **kwargs):
        super().model_post_init(*args, **kwargs)
        if self.api_keys.get("token"):
            self.default_headers.update({
                "PRIVATE-TOKEN": self.api_keys["token"]
            })

    def get_expected_env_keys(self) -> List[str]:
        return ["token"]

    def create_repository(self, name: str, description: str = "", private: bool = False) -> Dict:
        response = self.make_request(
            method="POST",
            endpoint="projects",
            data={
                "name": name,
                "description": description,
                "visibility": "private" if private else "public"
            }
        )
        return response.json()

    @classmethod
    def detect_remote_type(cls, remote_url: str) -> bool:
        gitlab_patterns = [
            r"git@gitlab\.com:",
            r"https://gitlab\.com/",
            r"git://gitlab\.com/"
        ]
        return any(re.search(pattern, remote_url) for pattern in gitlab_patterns)