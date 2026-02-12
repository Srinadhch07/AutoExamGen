import os
import smtplib
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from datetime import datetime


load_dotenv()

SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")



async def send_otp_email(user: dict, otp: str) -> bool:

    subject = "Your OTP Verification Code"
    html_content = f"""
<!DOCTYPE html>
<html>

<head>
  <meta charset="UTF-8" />
  <title>Lifelet OTP Verification</title>
</head>

<body style="margin:0; padding:0; background-color:#f5f7fa; font-family:Arial, sans-serif;">

  <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#f5f7fa; padding:40px 0;">
    <tr>
      <td align="center">

        <table width="100%" cellpadding="0" cellspacing="0" style="max-width:480px; background:white; padding:30px; border-radius:12px; box-shadow:0 4px 12px rgba(0,0,0,0.08);">

          <!-- Logo / Title -->
          <tr>
            <td align="center" style="padding-bottom:20px;">
              <h2 style="margin:0; font-size:28px; color:#2B6CB0; font-weight:700;">Lifelet</h2>
            </td>
          </tr>

          <!-- Header -->
          <tr>
            <td style="text-align:center; padding:10px 20px;">
              <h3 style="margin:0; font-size:22px; color:#2D3748; font-weight:600;">OTP Verification</h3>
            </td>
          </tr>

          <!-- Greeting -->
          <tr>
            <td style="padding:10px 20px; text-align:center;">
              <p style="font-size:16px; color:#4A5568; margin:0;">
                Hi <strong>{user["name"]}</strong>,
              </p>
              <p style="font-size:16px; color:#4A5568; margin-top:8px;">
                Use the verification code below to complete your sign-in.
              </p>
            </td>
          </tr>

          <!-- OTP Box -->
          <tr>
            <td align="center" style="padding:25px 0;">
              <div style="display:inline-block; background:#EDF2F7; padding:18px 30px; border-radius:10px; border:1px solid #CBD5E0;">
                <span style="font-size:32px; color:#2F855A; font-weight:700; letter-spacing:4px;">{otp}</span>
              </div>
            </td>
          </tr>

          <!-- Info -->
          <tr>
            <td style="padding:0 20px; text-align:center;">
              <p style="font-size:14px; color:#718096; margin:0;">
                This OTP is valid for <strong>5 minutes</strong>.
              </p>
              <p style="font-size:14px; color:#718096; margin-top:6px;">
                If you didn’t request this, please ignore this email.
              </p>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td align="center" style="padding-top:30px;">
              <p style="font-size:13px; color:#A0AEC0;">
                &copy; {datetime.utcnow().year} Lifelet. All rights reserved.
              </p>
            </td>
          </tr>

        </table>

      </td>
    </tr>
  </table>

</body>

</html>
"""

    try:
      
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = SENDER_EMAIL
        message["To"] =  user["email"]
        message.attach(MIMEText(html_content, "html"))

       
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(message)

        print(f"OTP sent successfully to {user["email"]}")
        return True

    except Exception as e:
        print(f"Error sending OTP: {e}")
        return False


async def send_forgot_otp(user:dict, otp: str) -> bool:

    subject = "Your OTP Verification Code"
    html_content = f"""
<!DOCTYPE html>
<html>

<head>
  <meta charset="UTF-8" />
  <title>Lifelet Password Reset</title>
</head>

<body style="margin:0; padding:0; background-color:#f5f7fa; font-family:Arial, sans-serif;">

  <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#f5f7fa; padding:40px 0;">
    <tr>
      <td align="center">

        <table width="100%" cellpadding="0" cellspacing="0" style="max-width:480px; background:white; padding:30px; border-radius:12px; box-shadow:0 4px 12px rgba(0,0,0,0.08);">

          <!-- Logo / Title -->
          <tr>
            <td align="center" style="padding-bottom:20px;">
              <h2 style="margin:0; font-size:28px; color:#2B6CB0; font-weight:700;">Lifelet</h2>
            </td>
          </tr>

          <!-- Header -->
          <tr>
            <td style="text-align:center; padding:10px 20px;">
              <h3 style="margin:0; font-size:22px; color:#2D3748; font-weight:600;">Password Reset Request</h3>
            </td>
          </tr>

          <!-- Greeting -->
          <tr>
            <td style="padding:10px 20px; text-align:center;">
              <p style="font-size:16px; color:#4A5568; margin:0;">
                Hi <strong>{user["name"]}</strong>,
              </p>
              <p style="font-size:16px; color:#4A5568; margin-top:8px;">
                We received a request to reset your password.<br>
                Use the OTP below to continue.
              </p>
            </td>
          </tr>

          <!-- OTP Box -->
          <tr>
            <td align="center" style="padding:25px 0;">
              <div style="display:inline-block; background:#EDF2F7; padding:18px 30px; border-radius:10px; border:1px solid #CBD5E0;">
                <span style="font-size:32px; color:#2F855A; font-weight:700; letter-spacing:4px;">{otp}</span>
              </div>
            </td>
          </tr>

          <!-- Info -->
          <tr>
            <td style="padding:0 20px; text-align:center;">
              <p style="font-size:14px; color:#718096; margin:0;">
                This OTP will expire in <strong>5 minutes</strong>.
              </p>
              <p style="font-size:14px; color:#718096; margin-top:6px;">
                If you didn’t request this, you can safely ignore the email — your account is still secure.
              </p>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td align="center" style="padding-top:30px;">
              <p style="font-size:13px; color:#A0AEC0;">
                &copy; {datetime.utcnow().year} Lifelet. All rights reserved.
              </p>
            </td>
          </tr>

        </table>

      </td>
    </tr>
  </table>

</body>

</html>
"""


    try:
      
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = SENDER_EMAIL
        message["To"] = user["email"]
        message.attach(MIMEText(html_content, "html"))

       
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(message)

        print(f"OTP sent successfully to {user["email"]}")
        return True

    except Exception as e:
        print(f"Error sending OTP: {e}")
        return False
