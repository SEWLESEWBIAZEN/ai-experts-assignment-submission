# Explanation

## 1. What was the bug?

When `Client.request(..., api=True)` was called with `oauth2_token` set to a **dict** (e.g. `{"access_token": "stale", "expires_at": 0}`), the client did not refresh the token and did not set the `Authorization` header. The request was sent without credentials.

## 2. Why did it happen?

The refresh condition only handled two cases: no token (`not self.oauth2_token`) or an **OAuth2Token** instance that was expired. A dict is truthy and is not an `OAuth2Token`, so neither branch ran and `refresh_oauth2()` was never called. The code then only sets `Authorization` when `isinstance(self.oauth2_token, OAuth2Token)`, so the dict was ignored and no header was added.

## 3. Why does your fix actually solve it?

The fix adds a third condition: refresh when the token is **not** an `OAuth2Token` instance (`not isinstance(self.oauth2_token, OAuth2Token)`). So for a dict (or any non-`OAuth2Token` value), we now call `refresh_oauth2()`, which sets `self.oauth2_token` to a valid `OAuth2Token`. The existing logic then sets the `Authorization` header from that token.

## 4. What's one realistic case / edge case your tests still don't cover?

**Expired token stored as OAuth2Token with a past `expires_at` in a different timezone.** The tests use `expires_at` as a Unix timestamp or a fixed ISO string; they don't assert behaviour when the token was created from an ISO string in a non-UTC timezone and the local “now” is close to the boundary. A bug in `token_from_iso` or in `expired` for timezone-aware datetimes could slip through.
