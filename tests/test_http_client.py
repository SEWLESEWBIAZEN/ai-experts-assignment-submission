import time

import requests

from app.http_client import Client
from app.tokens import OAuth2Token, token_from_iso


def test_client_uses_requests_session():
    c = Client()
    assert isinstance(c.session, requests.Session)


def test_token_from_iso_uses_dateutil():
    t = token_from_iso("ok", "2099-01-01T00:00:00Z")
    assert isinstance(t, OAuth2Token)
    assert t.access_token == "ok"
    assert not t.expired


def test_api_request_sets_auth_header_when_token_is_valid():
    c = Client()
    c.oauth2_token = OAuth2Token(access_token="ok", expires_at=int(time.time()) + 3600)

    resp = c.request("GET", "/me", api=True)

    assert resp["headers"].get("Authorization") == "Bearer ok"


def test_api_request_refreshes_when_token_is_missing():
    c = Client()
    c.oauth2_token = None

    resp = c.request("GET", "/me", api=True)

    assert resp["headers"].get("Authorization") == "Bearer fresh-token"


def test_api_request_refreshes_when_token_is_dict():
    c = Client()
    c.oauth2_token = {"access_token": "stale", "expires_at": 0}

    resp = c.request("GET", "/me", api=True)

    assert resp["headers"].get("Authorization") == "Bearer fresh-token"


def test_api_request_with_dict_token_includes_authorization_header():
    """
    when oauth2_token is a dict (e.g. from legacy/raw API response),
    the client must refresh and set Authorization. Fails on buggy code that ignores
    non-OAuth2Token types.
    """
    client = Client()
    client.oauth2_token = {"access_token": "raw-dict-token", "expires_at": 999999999}

    response = client.request("POST", "/api/data", api=True)

    assert "Authorization" in response["headers"], (
        "api=True with dict token must refresh and set Authorization header"
    )
    assert response["headers"]["Authorization"] == "Bearer fresh-token"