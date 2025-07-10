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

    response = table.get_item(
        Key={"PK": email, "SK": "PROFILE"},
        ConsistentRead=True,
    )
    item = response.get("Item")
    if item:
        logger.error("Email already exists", extra={"email": email})

    # Hash the password and retrieve the salt
    password_salt, hashed_password = hash_password(password, pepper)

    return {
        "status": "success",
        "password_salt": password_salt,
        "hashed_password": hashed_password,
    }, 200

    # return {
    #     "user_id": user_id,
    #     "username": username,
    # }, 200
