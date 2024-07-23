from fastapi_mail import FastMail,MessageSchema,ConnectionConfig,MessageType
import os
from dotenv import load_dotenv

load_dotenv()

conf = ConnectionConfig(
    MAIL_USERNAME = os.getenv("GMAIL_USERNAME"),
    MAIL_PASSWORD = os.getenv("GMAIL_PASS"),
    MAIL_FROM = os.getenv("GMAIL_USERNAME"),
    MAIL_PORT = 587,
    MAIL_SERVER = "smtp.gmail.com",
    MAIL_FROM_NAME="fiXitAI",
    MAIL_STARTTLS = True,
    MAIL_SSL_TLS = False,
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = True
)

async def send_with_template(token:str,email:str):

    html = f"""<!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333333;
                    background-color: #f7f7f7;
                    margin: 0;
                    padding: 0;
                }}
                .container {{
                    max-width: 600px;
                    margin: 20px auto;
                    background-color: #ffffff;
                    border-radius: 10px;
                    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                    border:1px solid black;
                }}
                .header {{
                    text-align: center;
                    padding: 10px 0;
                    background-color: #000000;
                    color: #ffffff;
                    border-top-left-radius: 10px;
                    border-top-right-radius: 10px;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 24px;
                }}
                .content {{
                    padding: 20px;
                }}
                .content p {{
                    margin: 10px 0;
                }}
                .button {{
                    display: block;
                    width: 200px;
                    margin: 20px auto;
                    padding: 10px;
                    text-align: center;
                    background-color: #000000;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                }}
                .footer {{
                    text-align: center;
                    padding: 10px 0;
                    color: #777777;
                    font-size: 12px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Verify Your Email Address</h1>
                </div>
                <div class="content">
                    <p>Thank you for registering with us. Please verify your email address by clicking the button below:</p>
                    <a style={{color:"white"}} href="http://127.0.0.1:8000/verify?token={ token }" class="button">Verify Account</a>
                    <p>If you did not create an account, no further action is required.</p>
                    <p>Best regards,</p>
                    <p>fiXitAI</p>
                </div>
                <div class="footer">
                    <p>&copy; 2024 Your Company Name. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
    message = MessageSchema(
        subject="Verify your identity",
        recipients=[email],
        body=html,
        subtype=MessageType.html,
        )

    fm = FastMail(conf)
    await fm.send_message(message) 