import os
import json
import boto3

ses = boto3.client("ses")

FROM_EMAIL = os.environ["FROM_EMAIL"]

def lambda_handler(event, context):
    if isinstance(event, dict) and "body" in event and isinstance(event["body"], str):
        payload = json.loads(event["body"])
    else:
        payload = event

    to = payload["to"]
    subject = payload["subject"]
    body_text = payload.get("body_text", "")
    body_html = payload.get("body_html")

    if isinstance(to, str):
        to = [to]

    message = {
        "Subject": {"Data": subject, "Charset": "UTF-8"},
        "Body": {}
    }
    if body_text:
        message["Body"]["Text"] = {"Data": body_text, "Charset": "UTF-8"}
    if body_html:
        message["Body"]["Html"] = {"Data": body_html, "Charset": "UTF-8"}

    resp = ses.send_email(
        Source=FROM_EMAIL,
        Destination={"ToAddresses": to},
        Message=message,
    )

    return {
        "ok": True,
        "message_id": resp["MessageId"]
    }
