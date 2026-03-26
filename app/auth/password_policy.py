"""Shared password rules for email/password auth flows."""
from __future__ import annotations

import re

_MIN_LENGTH = 8
_NON_ALPHANUMERIC = re.compile(r"[^A-Za-z0-9]")

# Shown next to password fields; enforced server-side on login, register, reset.
PASSWORD_POLICY_HINT = (
    "At least 8 characters, including at least one special character "
    "(any symbol that is not a letter or digit)."
)


def password_policy_html_pattern() -> str:
    """HTML5 pattern: minimum length 8 and at least one non-alphanumeric."""
    return r"(?=.*[^A-Za-z0-9]).{8,}"


def password_policy_error(password: str) -> str | None:
    if len(password) < _MIN_LENGTH:
        return f"Password must be at least {_MIN_LENGTH} characters long."
    if not _NON_ALPHANUMERIC.search(password):
        return "Password must include at least one special character."
    return None
