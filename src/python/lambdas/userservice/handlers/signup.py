import os
import random
import time
import uuid
from datetime import UTC, datetime
from uuid import uuid4
import boto3

from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEvent
from aws_lambda_powertools.utilities.typing import LambdaContext
from auth_utils import (
    get_secret,
    hash_password,
    send_email_confirmation_code,
)

logger = Logger(service="user.signup")
pepper = get_secret(secret_name="baselayercapital/PEPPER")

ENV_NAME = os.environ["ENV_NAME"]
ENV_TYPE = os.environ["ENV_TYPE"]

table_name = f"{ENV_NAME}-UserService"
table = boto3.resource("dynamodb").Table(table_name)


def main(current_event: APIGatewayProxyEvent, current_context: LambdaContext):
    isProd = ENV_TYPE == "prd" and ENV_NAME == "prd"
    email_source = "noreply@baselayercapital.com"

    logger.info("Received request", extra={"event": dict(current_event)})

    body = current_event.json_body
    email = body.get("email")
    password = body.get("password")

    if not email:
        logger.error("Email is required", extra={"body": body})
        return {
            "error": "Email is required",
        }, 400

    if not password:
        logger.error("Missing password in request")
        return {
            "error": "password is required",
        }, 400

    response = table.query(
        IndexName="email-index",
        KeyConditionExpression=boto3.dynamodb.conditions.Key("email").eq(email),
        Limit=1,
    )
    items = response.get("Items", [])
    if items:
        logger.error("Email already exists", extra={"email": email})
        return {
            "error": "Email already exists",
        }, 400

    # Hash the password and retrieve the salt
    password_salt, hashed_password = hash_password(password, pepper)

    user_id = str(uuid4())
    confirmation_code = "".join([str(random.randint(0, 9)) for _ in range(6)])
    table.put_item(
        Item={
            "PK": user_id,
            "SK": "USER",
            "email": email,
            "password_salt": password_salt,
            "hashed_password": hashed_password,
            "confirmed": False,
            "confirmation_code": confirmation_code,
            "created_at": datetime.now(UTC).isoformat(),
            "updated_at": datetime.now(UTC).isoformat(),
        }
    )

    send_email_confirmation_code(email, confirmation_code, email_source)

    return {
        "message": "Check your email for the confirmation code",
    }, 200
