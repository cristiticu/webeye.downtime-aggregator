
from typing import Mapping
import boto3

import settings


def send_email(destinations: list[str], subject: str, body: Mapping):
    ses = boto3.client("ses", region_name=settings.SES_REGION)

    response = ses.send_email(
        Source=settings.SES_SOURCE,
        Destination={
            "ToAddresses": destinations,
        },
        Message={
            "Subject": {
                "Data": subject,
                "Charset": "UTF-8"
            },
            "Body": {
                "Text": {
                    "Data": body.get("text", "No text"),
                    "Charset": "UTF-8"
                },
            }
        }
    )

    return response
