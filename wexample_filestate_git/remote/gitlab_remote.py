import re
from typing import Dict, List
from pydantic import Field

from .abstract_remote import AbstractRemote


GITLAB_ENV_KEY_TOKEN: str = "GITLAB_API_TOKEN"
GITLAB_DEFAULT_URL: str = "https://gitlab.com/api/v4"


class GitlabRemote(AbstractRemote):
    base_url: str = Field(
        default=GITLAB_DEFAULT_URL,
        description="GitLab API base URL"
    )

    def model_post_init(self, *args, **kwargs):
        super().model_post_init(*args, **kwargs)
        token = self.get_api_key(GITLAB_ENV_KEY_TOKEN)
        self.default_headers.update({
            "PRIVATE-TOKEN": token
        })

    def get_expected_env_keys(self) -> List[str]:
        return [
            GITLAB_ENV_KEY_TOKEN,
        ]

    def create_repository(self, name: str, description: str = "", private: bool = False) -> Dict:
        response = self.make_request(
            method="POST",
            endpoint="projects",
            data={
                "name": name,
                "description": description,
                "visibility": "private" if private else "public",
                "initialize_with_readme": True
            }
        )
        return response.json()

    def check_connection(self) -> bool:
        try:
            # Try to access user information to verify connection
            self.make_request(
                method="GET",
                endpoint="user"
            )
            return True
        except Exception:
            return False

    @classmethod
    def detect_remote_type(cls, remote_url: str) -> bool:
        gitlab_patterns = [
            r"git@gitlab\.com:",
            r"https://gitlab\.com/",
            r"git://gitlab\.com/"
        ]
        return any(re.search(pattern, remote_url) for pattern in gitlab_patterns)