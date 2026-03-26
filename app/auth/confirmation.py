"""Require confirmed email (or phone for phone-only accounts) before treating a user as signed in."""


def supabase_user_may_use_app(user) -> bool:
    """
    True if the Supabase User has a verified primary identity we care about.
    Email/password and OAuth users must have email_confirmed_at when email is set.
    """
    if user is None:
        return False
    email = getattr(user, "email", None)
    if email:
        return getattr(user, "email_confirmed_at", None) is not None
    phone = getattr(user, "phone", None)
    if phone:
        return getattr(user, "phone_confirmed_at", None) is not None
    return True


def auth_user_json_may_use_app(data: dict) -> bool:
    """Same rule for GET /auth/v1/user JSON."""
    if not data:
        return False
    if data.get("email"):
        return bool(data.get("email_confirmed_at"))
    if data.get("phone"):
        return bool(data.get("phone_confirmed_at"))
    return True
