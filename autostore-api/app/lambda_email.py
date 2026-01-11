import os
import json
import boto3
from botocore.config import Config

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
LAMBDA_NAME = os.getenv("LAMBDA_NAME", "send-email-lambda")

_lambda_client = boto3.client(
    "lambda",
    region_name=AWS_REGION,
    config=Config(
        connect_timeout=3,
        read_timeout=15,
        retries={"max_attempts": 2},
    ),
)

def invoke_send_email(payload: dict) -> dict:
    resp = _lambda_client.invoke(
        FunctionName=LAMBDA_NAME,
        InvocationType="RequestResponse",
        Payload=json.dumps(payload).encode("utf-8"),
    )

    # Lambda threw an error
    if resp.get("FunctionError"):
        err_payload = resp["Payload"].read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Lambda error: {err_payload}")

    result_raw = resp["Payload"].read().decode("utf-8")
    return json.loads(result_raw)
