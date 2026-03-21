"""
Transactional email for odl-app. Uses Resend.
"""
import os

try:
    import resend
    _resend_available = True
    if os.getenv("RESEND_API_KEY"):
        resend.api_key = os.getenv("RESEND_API_KEY")
except ImportError:
    resend = None
    _resend_available = False


def _log(msg: str) -> None:
    print(f"[odl-app email] {msg}")


def _is_configured() -> bool:
    if not _resend_available:
        _log("Resend package not available")
        return False
    if not (os.getenv("RESEND_API_KEY") or "").strip():
        _log("RESEND_API_KEY not set")
        return False
    if not (os.getenv("RESEND_FROM") or "").strip():
        _log("RESEND_FROM not set")
        return False
    return True


def send_org_invite(*, invited_email: str, org_name: str, role: str, invite_link: str, invited_by: str = "") -> bool:
    """Send an organisation invite email to the invitee."""
    if not _is_configured():
        return False

    from_email = os.getenv("RESEND_FROM").strip()
    role_label = "Admin" if role == "admin" else "Member"
    invited_by_line = f"<p style='color:#64748B;font-size:13px;margin:0 0 16px;'>Invited by {invited_by}</p>" if invited_by else ""

    html = f"""
    <div style='font-family:Inter,sans-serif;background:#0B1120;padding:40px 0;'>
      <div style='max-width:480px;margin:0 auto;background:#0F1929;border:1px solid rgba(148,163,184,0.12);border-radius:12px;padding:40px;'>
        <p style='font-size:13px;font-weight:700;letter-spacing:0.08em;text-transform:uppercase;color:#29b5e8;margin:0 0 20px;'>OpenData.London</p>
        <h1 style='font-size:22px;font-weight:700;color:#F8FAFC;margin:0 0 10px;letter-spacing:-0.3px;'>You've been invited</h1>
        <p style='color:#94A3B8;font-size:14px;line-height:1.6;margin:0 0 6px;'>
          You've been invited to join <strong style='color:#F8FAFC;'>{org_name}</strong> on OpenData.London as a <strong style='color:#F8FAFC;'>{role_label}</strong>.
        </p>
        {invited_by_line}
        <a href='{invite_link}' style='display:inline-block;background:#29b5e8;color:#020617;font-weight:700;font-size:14px;padding:12px 24px;border-radius:7px;text-decoration:none;margin:8px 0 24px;'>
          Accept invitation
        </a>
        <p style='color:#475569;font-size:12px;line-height:1.6;margin:0;'>
          This link expires after 24 hours. If you did not expect this invitation, you can ignore this email.
        </p>
        <hr style='border:none;border-top:1px solid rgba(148,163,184,0.08);margin:28px 0 20px;'>
        <p style='color:#334155;font-size:12px;margin:0;'>
          OpenData.London &nbsp;·&nbsp; <a href='https://app.opendata.london' style='color:#29b5e8;text-decoration:none;'>app.opendata.london</a>
        </p>
      </div>
    </div>
    """

    text = (
        f"You've been invited to join {org_name} on OpenData.London as a {role_label}.\n\n"
        f"Accept your invitation:\n{invite_link}\n\n"
        "This link expires after 24 hours."
    )

    try:
        resend.Emails.send({
            "from": from_email,
            "to": [invited_email],
            "subject": f"You've been invited to join {org_name} on OpenData.London",
            "html": html,
            "text": text,
        })
        _log(f"Invite email sent to {invited_email}")
        return True
    except Exception as e:
        _log(f"Resend send failed: {type(e).__name__}: {e}")
        return False
