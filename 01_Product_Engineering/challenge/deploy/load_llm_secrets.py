"""Copy the LLM gateway settings from the repo-root .env into Secrets Manager.

One secret per variable, named auto-invoicing-demo/<VARIABLE>. Prints names and
ARNs, never values. Run it yourself, from challenge/:

    AWS_PROFILE=<your-profile> AWS_REGION=us-east-2 uv run python deploy/load_llm_secrets.py

teardown.sh deletes these secrets along with the stack.
"""

from pathlib import Path

import boto3
from dotenv import dotenv_values

ENV_FILE = Path(__file__).resolve().parents[3] / ".env"
VARIABLES = ("LLM_API_BASE", "LLM_EXTRA_HEADERS", "OPENAI_API_KEY")
TAGS = [{"Key": "Project", "Value": "fde-course-demo"}]

values = dotenv_values(ENV_FILE)
client = boto3.client("secretsmanager")

for var in VARIABLES:
    value = (values.get(var) or "").strip()
    name = f"auto-invoicing-demo/{var}"
    if not value:
        print(f"{var}: not set in .env, skipped")
        continue
    try:
        arn = client.create_secret(Name=name, SecretString=value, Tags=TAGS)["ARN"]
        print(f"{var}: created {arn}")
    except client.exceptions.ResourceExistsException:
        arn = client.put_secret_value(SecretId=name, SecretString=value)["ARN"]
        print(f"{var}: updated {arn}")
