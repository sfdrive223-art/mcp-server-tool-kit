"""Minimal bearer-token auth — a fixed allow-list, no OAuth, no expiry.

Matches the shared-secret `bearer_token` that AAF's McpRuntimeAdapter binding
configuration already sends per request.
"""

from __future__ import annotations

from fastmcp.server.auth import AccessToken, TokenVerifier


class StaticBearerTokenVerifier(TokenVerifier):
    def __init__(self, allowed_tokens: set[str]) -> None:
        super().__init__()
        self._allowed = allowed_tokens

    async def verify_token(self, token: str) -> AccessToken | None:
        if token not in self._allowed:
            return None
        return AccessToken(token=token, client_id="aaf-consumer", scopes=[])
