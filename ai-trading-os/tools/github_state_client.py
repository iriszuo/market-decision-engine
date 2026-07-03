"""Minimal GitHub JSON state client.

This helper is intentionally small. It reads and writes JSON files through the
GitHub Contents API so GitHub can remain the source of truth for state.
"""

from __future__ import annotations

import base64
import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class GitHubStateClient:
    owner: str
    repo: str
    branch: str = "main"
    token: str | None = None

    @property
    def _auth_token(self) -> str:
        token = self.token or os.getenv("GITHUB_TOKEN")
        if not token:
            raise RuntimeError("GITHUB_TOKEN is required for GitHub state access")
        return token

    def read_json(self, path: str) -> dict[str, Any]:
        response = self._request("GET", self._contents_url(path, ref=True))
        encoded = response["content"].replace("\n", "")
        data = json.loads(base64.b64decode(encoded).decode("utf-8"))
        if not isinstance(data, dict):
            raise ValueError(f"{path}: expected JSON object")
        return data

    def write_json(self, path: str, data: dict[str, Any], message: str) -> None:
        current = self._request("GET", self._contents_url(path, ref=True), allow_404=True)
        payload: dict[str, Any] = {
            "message": message,
            "branch": self.branch,
            "content": base64.b64encode(
                json.dumps(data, ensure_ascii=True, indent=2, sort_keys=True).encode("utf-8")
            ).decode("ascii"),
        }
        if current:
            payload["sha"] = current["sha"]
        self._request("PUT", self._contents_url(path), payload)

    def _contents_url(self, path: str, ref: bool = False) -> str:
        base_url = f"https://api.github.com/repos/{self.owner}/{self.repo}/contents/{path}"
        if ref:
            return f"{base_url}?ref={self.branch}"
        return base_url

    def _request(
        self,
        method: str,
        url: str,
        payload: dict[str, Any] | None = None,
        allow_404: bool = False,
    ) -> dict[str, Any] | None:
        body = None
        if payload is not None:
            body = json.dumps(payload).encode("utf-8")

        request = urllib.request.Request(
            url,
            data=body,
            method=method,
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {self._auth_token}",
                "Content-Type": "application/json",
                "User-Agent": "ai-trading-os",
            },
        )

        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as error:
            if allow_404 and error.code == 404:
                return None
            raise
