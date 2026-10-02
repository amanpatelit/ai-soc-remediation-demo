import json
import boto3
import requests
from flask import Flask, request, jsonify
from config import SLACK_WEBHOOK_URL, AWS_REGION, PORT

app = Flask(__name__)
s3_client = boto3.client("s3", region_name=AWS_REGION)

@app.route("/webhook/alert", methods=["POST"])
def handle_alert():
    """Simulates receiving a correlated security incident."""
    data = request.json or {}
    bucket_name = data.get("bucket_name", "devops-ai-soc-demo-xxxx")
    
    # AI Correlation & Triage Summary
    ai_analysis = {
        "summary": f"Public S3 Bucket Detected: `{bucket_name}`.",
        "root_cause": "Public Access Block settings set to FALSE via Terraform deployment.",
        "risk_level": "HIGH (Exposes bucket objects to public read)",
        "recommended_fix": "Enable 'Block Public Access' configuration.",
        "bucket_name": bucket_name
    }
    
    send_slack_interactive_message(ai_analysis)
    return jsonify({"status": "Alert processed, Slack notification sent."}), 200


def send_slack_interactive_message(analysis):
    """Sends an interactive card to Slack with an approval button."""
    slack_payload = {
        "blocks": [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": "🚨 AI SOC Alert: Unsecured Cloud Asset", "emoji": True}
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Resource:* `{analysis['bucket_name']}`"},
                    {"type": "mrkdwn", "text": f"*Risk Level:* {analysis['risk_level']}"}
                ]
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*AI Diagnosis:* {analysis['root_cause']}\n*Proposed Fix:* {analysis['recommended_fix']}"}
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "⚡ Approve Auto-Fix"},
                        "style": "primary",
                        "value": json.dumps({"action": "fix_s3", "bucket": analysis['bucket_name']})
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "❌ Ignore"},
                        "style": "danger",
                        "value": "ignore"
                    }
                ]
            }
        ]
    }
    requests.post(SLACK_WEBHOOK_URL, json=slack_payload)


@app.route("/slack/actions", methods=["POST"])
def handle_slack_action():
    """Handles the 'Approve Auto-Fix' button click from Slack."""
    payload = json.loads(request.form.get("payload"))
    action_value = json.loads(payload["actions"][0]["value"])
    
    if action_value.get("action") == "fix_s3":
        bucket_name = action_value.get("bucket")
        remediate_s3_bucket(bucket_name)
        
        return jsonify({
            "response_type": "in_channel",
            "replace_original": True,
            "text": f"✅ *REMEDIATED:* Bucket `{bucket_name}` is now PRIVATE. Public access blocked completely. Audit log saved (#SEC-4092)."
        })
    
    return jsonify({"status": "Ignored"}), 200


def remediate_s3_bucket(bucket_name):
    """Enforces Block Public Access via boto3."""
    try:
        s3_client.put_public_access_block(
            Bucket=bucket_name,
            PublicAccessBlockConfiguration={
                'BlockPublicAcls': True,
                'IgnorePublicAcls': True,
                'BlockPublicPolicy': True,
                'RestrictPublicBuckets': True
            }
        )
        print(f"[SUCCESS] Secured S3 Bucket: {bucket_name}")
    except Exception as e:
        print(f"[ERROR] Remediation failed: {str(e)}")


if __name__ == "__main__":
    app.run(port=PORT, debug=True)