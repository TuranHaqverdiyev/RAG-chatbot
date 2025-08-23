# tools.py — Bedrock client helper
import boto3
from config import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION


def get_bedrock_client():
    """Create and return a boto3 Bedrock client using credentials from config."""
    return boto3.client(
        "bedrock-runtime",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION,
    )
