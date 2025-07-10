import hashlib
import json
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from functools import lru_cache
from uuid import uuid4

import boto3
from botocore.exceptions import ClientError

ENV_NAME = os.environ.get("ENV_NAME", "dev")


@lru_cache(maxsize=None)
def get_secret(secret_name, to_dict=False, region_name="us-east-1"):
    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(service_name="secretsmanager", region_name=region_name)

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        raise e

    if to_dict:
        return json.loads(get_secret_value_response["SecretString"])
    else:
        return get_secret_value_response["SecretString"]


def hash_password(password, pepper, salt=None):
    if not salt:
        salt = uuid4().hex

    combined = password + salt + pepper
    hashed_password = hashlib.sha512(combined.encode()).hexdigest()
    return salt, hashed_password


def send_email_confirmation_code(
    email, code, source="noreply@baselayercapital.com", env_name="dev"
):
    if email.startswith("test-"):
        return {
            "Testing": True,
            "Subject": {"Data": "Your Confirmation Code"},
            "Body": {"Text": {"Data": f"Your confirmation code is {code}"}},
        }

    ses = boto3.client("ses")

    # Prepare the HTML content (no image included)
    html = f"""
    <html>
      <head></head>
      <body style="font-family: sans-serif;">
        <h2 style="color:#ff5c39;">Welcome to Base Layer Capital</h2>
        <p>Your confirmation code is:</p>
        <h1 style="font-size: 2rem;">{code}</h1>
        <hr/>
        <p style="font-size: 0.9rem; color: #888;">This code will expire in 10 minutes.</p>
      </body>
    </html>
    """

    # Build the email as a multipart/alternative message
    outer = MIMEMultipart("alternative")
    outer["Subject"] = "Your Confirmation Code"
    outer["From"] = source
    outer["To"] = email

    # Attach plain-text fallback
    text_part = MIMEText(f"Your confirmation code is {code}", "plain")
    outer.attach(text_part)

    # Attach HTML part
    html_part = MIMEText(html, "html")
    outer.attach(html_part)

    # Send the email using SES's raw email method
    ses.send_raw_email(
        Source=source,
        Destinations=[email],
        RawMessage={"Data": outer.as_string()},
    )


# def send_sms_confirmation_code(phone_number, code):
#     if phone_number.startswith("test-"):
#         return {
#             "Testing": True,
#             "Subject": {"Data": "Your Confirmation Code"},
#             "Body": {"Text": {"Data": f"Your confirmation code is {code}"}},
#         }

#     sns_client = boto3.client("sns")
#     response = sns_client.publish(PhoneNumber=phone_number, Message=f"Your confirmation code is {code}")
#     return response
