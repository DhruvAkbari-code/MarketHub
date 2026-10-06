import logging
from email.message import EmailMessage

import aiosmtplib
from core_api.config import settings

log = logging.getLogger(__name__)


def _build_message(to_email: str, username: str, link: str) -> EmailMessage:
    msg = EmailMessage()
    msg["From"] = settings.EMAIL_FROM
    msg["To"] = to_email
    msg["Subject"] = "Verify your MarketHub email"
    msg.set_content(
        f"Hi {username},\n\n"
        f"Confirm your email by opening this link:\n{link}\n\n"
        f"The link expires in {settings.VERIFY_TOKEN_EXPIRE_HOURS} hours.\n"
    )
    msg.add_alternative(
        f"""\
        <p>Hi {username},</p>
        <p>Confirm your email by clicking the link below:</p>
        <p><a href="{link}">Verify my email</a></p>
        <p>The link expires in {settings.VERIFY_TOKEN_EXPIRE_HOURS} hours.</p>
        """,
        subtype="html",
    )
    return msg


async def send_verification_email(to_email: str, username: str, token: str) -> None:
    link = f"{settings.FRONTEND_URL}/verify-email?token={token}"

    msg = _build_message(to_email, username, link)
    try:
        await aiosmtplib.send(
            msg,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USER or None,
            password=settings.SMTP_PASSWORD or None,
            start_tls=settings.SMTP_PORT != 1025,
        )
    except Exception:
        log.exception("Failed to send verification email to %s", to_email)
