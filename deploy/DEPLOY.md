# Niryat AI — AWS Deployment Guide (CloudFormation)

## Architecture

```
User → CloudFront → S3 (frontend static site)
                 → EC2 t3.small (backend API in Docker)
                      → RDS PostgreSQL (free tier)
                      → Bedrock Claude (pay-per-token)
                      → S3 (export docs — already exists)
```

**AWS services used** (6 services for hackathon evaluation):
Amazon Bedrock, Amazon S3, Amazon RDS, Amazon EC2, Amazon CloudFront, AWS CloudFormation

**Estimated cost**: ~$5-15/day during active demo. $0 when EC2 stopped.

---

## Prerequisites

1. AWS CLI configured: `aws configure` (with your access key)
2. An EC2 key pair exists: `aws ec2 describe-key-pairs` (create one in console if not)
3. Bedrock model access enabled (see Step 0)
4. Your S3 bucket `niryat-export-docs` already has export documents
5. Your code is pushed to a Git repo

---

## Step 0: Enable Bedrock Model Access (2 min)

Go to **AWS Console → Bedrock → Model access** → Request access to **Anthropic Claude Sonnet**.

**Verify**:
```bash
aws bedrock list-foundation-models --region us-east-1 \
  --query "modelSummaries[?contains(modelId,'claude')].modelId" --output table
```

---

## Step 1: Deploy CloudFormation Stack (1 command, ~10 min wait)

This single command creates: RDS, EC2, IAM role, security groups, S3 bucket, CloudFront, Elastic IP.

```bash
aws cloudformation create-stack \
  --stack-name niryat-ai \
  --template-body file://deploy/cloudformation.yaml \
  --capabilities CAPABILITY_NAMED_IAM \
  --parameters \
    ParameterKey=DBPassword,ParameterValue=YOUR_STRONG_DB_PASSWORD \
    ParameterKey=KeyPairName,ParameterValue=YOUR_KEY_PAIR_NAME \
    ParameterKey=GitRepoURL,ParameterValue=https://github.com/YOUR_USER/niryatAI.git \
    ParameterKey=S3ExportDocsBucket,ParameterValue=niryat-export-docs
```

**Wait for completion** (~8-10 min, RDS is the bottleneck):
```bash
aws cloudformation wait stack-create-complete --stack-name niryat-ai
echo "Stack ready!"
```

**Get all outputs** (your endpoints, IPs, commands):
```bash
aws cloudformation describe-stacks --stack-name niryat-ai \
  --query 'Stacks[0].Outputs' --output table
```

Save these values — you'll need `BackendURL`, `RDSEndpoint`, `FrontendBucketName`, `CloudFrontURL`.

**Verify backend is running**:
```bash
# Copy the BackendHealthCheck output command, or:
curl http://ELASTIC_IP:8000/health
# Expected: {"status":"ok","service":"niryat-ai"}
```

If the health check fails, the Docker build may still be running (UserData takes ~2-3 min after EC2 boots). SSH in and check:
```bash
ssh -i YOUR_KEY.pem ec2-user@ELASTIC_IP
docker logs niryat-api
```

---

## Step 2: Load Database Schema + Data (~10 min)

```bash
# Load schema (use RDSEndpoint from stack outputs)
psql -h RDS_ENDPOINT -U postgres -d niryatdb -f db-init/01-schema.sql
# Enter the DBPassword you set in Step 1

# Verify tables:
psql -h RDS_ENDPOINT -U postgres -d niryatdb -c "\dt"
# Should show 8 tables
```

**Load market intelligence data** (run your existing ingestion scripts):
```bash
cd backend/export-intel

# Set the connection string for your scripts
export DATABASE_URL="postgresql://postgres:YOUR_DB_PASSWORD@RDS_ENDPOINT:5432/niryatdb"

# Run in order:
python insert_clean_data.py
python compute_intelligence.py
python fetch_country_risk.py
```

**Verify data loaded**:
```bash
psql -h RDS_ENDPOINT -U postgres -d niryatdb \
  -c "SELECT count(*) FROM market_intelligence;"
# Should return your row count (e.g., 2000+)
```

---

## Step 3: Build and Deploy Frontend (~5 min)

```bash
cd frontend

# Point frontend to backend (use BackendURL from stack outputs)
echo "NEXT_PUBLIC_API_URL=http://ELASTIC_IP:8000/api" > .env.production

# Build static site
npm install
npm run build

# Upload to S3 (use FrontendBucketName from stack outputs)
aws s3 sync out/ s3://FRONTEND_BUCKET_NAME/ --delete
```

**Verify**:
```bash
# Open CloudFrontURL from stack outputs in your browser
# e.g., https://d1234abcdef.cloudfront.net
```

You should see the Niryat AI login page. Register an account and test all features.

> Note: CloudFront takes 5-10 min to fully propagate. If you get errors, try the S3 website URL directly first (from `FrontendWebsiteURL` output).

---

## Step 4: End-to-End Verification

| Test | How | Expected |
|------|-----|----------|
| Health check | `curl http://ELASTIC_IP:8000/health` | `{"status":"ok"}` |
| Register | Sign up on the frontend | Token returned, redirects to dashboard |
| Dashboard | After login | Shows readiness %, next step |
| AI Chat | Ask "Best markets for HS 0901?" | Agent queries DB via Bedrock, returns ranked list |
| Image upload | Upload a document image in chat | Bedrock vision describes the image |
| Market Intelligence | Open markets page | Table with countries, scores |
| Export Readiness | Open readiness tracker | 10 steps with checkboxes |
| Bedrock confirmation | `docker logs niryat-api` on EC2 | Shows `[AGENT] Using Bedrock model:` |

---

## Managing the Stack

**Stop EC2 between demos** (saves ~$0.50/hr):
```bash
# Get instance ID
INSTANCE_ID=$(aws ec2 describe-instances \
  --filters "Name=tag:Name,Values=niryat-backend" \
  --query 'Reservations[0].Instances[0].InstanceId' --output text)

# Stop
aws ec2 stop-instances --instance-ids $INSTANCE_ID

# Restart before demo
aws ec2 start-instances --instance-ids $INSTANCE_ID
# Elastic IP stays the same — no frontend redeploy needed!
```

**Update backend code** (after pushing changes to Git):
```bash
ssh -i YOUR_KEY.pem ec2-user@ELASTIC_IP
cd niryatAI && git pull
cd backend
docker build -t niryat-backend .
docker stop niryat-api && docker rm niryat-api
docker run -d --name niryat-api -p 8000:8000 --env-file .env --restart unless-stopped niryat-backend
```

**Update frontend** (after code changes):
```bash
cd frontend
npm run build
aws s3 sync out/ s3://FRONTEND_BUCKET_NAME/ --delete
# Invalidate CloudFront cache:
aws cloudfront create-invalidation \
  --distribution-id YOUR_DIST_ID --paths "/*"
```

**Tear down everything** (after hackathon):
```bash
# Empty the S3 bucket first (CloudFormation can't delete non-empty buckets)
aws s3 rm s3://FRONTEND_BUCKET_NAME --recursive

aws cloudformation delete-stack --stack-name niryat-ai
aws cloudformation wait stack-delete-complete --stack-name niryat-ai
echo "All resources deleted."
```

---

## Cost Summary

| Service | Cost | Notes |
|---------|------|-------|
| EC2 t3.small | $0.02/hr | **Stop when not demoing** |
| RDS db.t3.micro | Free tier | 750 hrs/month free |
| Bedrock Claude | ~$0.003/1K tokens | Pay only per chat message |
| S3 | ~$0.00 | Negligible |
| CloudFront | Free tier | 1 TB/month free |
| Elastic IP | Free when EC2 running | $0.005/hr when stopped |
| **Active demo day** | **~$2-5** | |
| **Idle (EC2 stopped)** | **~$0.12/day** | Just EIP + RDS |

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Stack creation fails | `aws cloudformation describe-stack-events --stack-name niryat-ai` to see which resource failed |
| Backend health check fails | SSH in, run `docker logs niryat-api`. UserData may still be running (~3 min after boot) |
| Can't connect to RDS locally | Your IP must be allowed — template allows 0.0.0.0/0 on 5432 |
| Bedrock "access denied" | Enable model access in Bedrock console for your region |
| Frontend shows blank page | Check browser console — ensure `NEXT_PUBLIC_API_URL` matches the Elastic IP |
| CloudFront shows old version | `aws cloudfront create-invalidation --distribution-id ID --paths "/*"` |
