# config.py — Load AWS/Bedrock config from environment variables
import os

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
BEDROCK_KB_ID = os.getenv("BEDROCK_KB_ID")
BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID")
