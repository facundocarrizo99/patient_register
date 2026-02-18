import os
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig


MAILTRAP_USER = os.getenv("MAILTRAP_USER", "your_mailtrap_user")
MAILTRAP_PASS = os.getenv("MAILTRAP_PASS", "your_mailtrap_pass")

conf = ConnectionConfig(
    MAIL_USERNAME=MAILTRAP_USER,
    MAIL_PASSWORD=MAILTRAP_PASS,
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
