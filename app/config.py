import os
from dotenv import load_dotenv

load_dotenv()

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", "https://hooks.slack.com/services/YOUR/WEBHOOK/URL")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
PORT = int(os.getenv("PORT", 5000))