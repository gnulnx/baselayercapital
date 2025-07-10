import os
import json
from aws_lambda_powertools import Logger
from aws_lambda_powertools.event_handler import APIGatewayRestResolver, CORSConfig

ENV_NAME = os.environ.get("ENV_NAME", "dev")
ENV_TYPE = os.environ.get("ENV_TYPE", "dev")
AWS_REGION = os.environ.get("REGION", "us-east-1")

isProd = ENV_TYPE == "prd" and ENV_NAME == "prd"

logger = Logger(service="userservice", level="INFO")


def get_resolver() -> APIGatewayRestResolver:
    cors_config = CORSConfig(
        allow_origin="https://baselayercapital.com" if isProd else "*",
        allow_headers=["Content-Type", "Authorization"],
        max_age=300,
        expose_headers=["Content-Length"],
        allow_credentials=False,
    )

    def add_csp_header(app, next_middleware):
        # Call the next middleware or route function
        response = next_middleware(app)
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self'; style-src 'self'; object-src 'none'; img-src 'self' data:;"
        )
        return response

    app = APIGatewayRestResolver(
        cors=cors_config,
        serializer=lambda obj: json.dumps(obj, default=str),
    )
    app.use([add_csp_header])

    return app


app: APIGatewayRestResolver = get_resolver()


@app.get("/userservice/ping")
def ping():
    logger.info("Ping request received")
    return {"message": "pong"}


@logger.inject_lambda_context
def main(event, context):
    logger.info("API.main event", extra={"event": event})
    if "detail-type" in event and event["detail-type"] == "Scheduled Event":
        return "ping request"
    return app.resolve(event, context)
