from fastapi_mail import ConnectionConfig, FastMail, MessageSchema

from .core.config import get_settings

settings = get_settings()

conf = ConnectionConfig(
    MAIL_USERNAME=settings.mailtrap_user,
    MAIL_PASSWORD=settings.mailtrap_pass,
    MAIL_FROM="noreply@example.com",
    MAIL_PORT=587,
    MAIL_SERVER="smtp.mailtrap.io",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
)


async def send_confirmation_email(email_to: str, name: str) -> None:
    message = MessageSchema(
        subject="Patient Registration Confirmation",
        recipients=[email_to],
        body=f"Hello {name},\n\nYour registration was successful.",
        subtype="plain",
    )
    fm = FastMail(conf)
    await fm.send_message(message)
