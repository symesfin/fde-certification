#!/usr/bin/env bash
# Delete everything the hosted demo created: the CloudFormation stack (App Runner
# service, ECR repository and its images, IAM roles, password secret) and the
# gateway secrets load_llm_secrets.py made outside the stack.
#
#   AWS_PROFILE=<your-profile> AWS_REGION=us-east-2 ./deploy/teardown.sh
set -euo pipefail
: "${AWS_PROFILE:?set AWS_PROFILE}" "${AWS_REGION:?set AWS_REGION}"

aws cloudformation delete-stack --stack-name auto-invoicing-demo
echo "Deleting stack auto-invoicing-demo (a few minutes)..."
aws cloudformation wait stack-delete-complete --stack-name auto-invoicing-demo

# APP_PASSWORD is in the list because CloudFormation leaves its secret in a
# recovery window; force-deleting it now frees the name for a redeploy.
for var in APP_PASSWORD LLM_API_BASE LLM_EXTRA_HEADERS OPENAI_API_KEY; do
  aws secretsmanager delete-secret --secret-id "auto-invoicing-demo/$var" \
    --force-delete-without-recovery >/dev/null 2>&1 && echo "deleted auto-invoicing-demo/$var" || true
done

echo "Left behind, if anything:"
aws resourcegroupstaggingapi get-resources --tag-filters Key=Project,Values=fde-course-demo \
  --query 'ResourceTagMappingList[].ResourceARN' --output text
