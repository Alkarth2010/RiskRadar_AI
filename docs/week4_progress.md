# Week 4 Progress Report

**Project:** RiskRadar AI - Fraud Transaction Investigation Assistant
**Capstone Theme:** IIT Roorkee AIOps Capstone, Theme 13
**RFP Week:** Week 4, 15 June 2026 to 30 June 2026
**Current Work Date:** 18 June 2026
**Status:** AWS EC2 deployment, S3-backed file storage, and optional Docker containerization completed; final report, PPT, and recording pending
**Primary Goal:** Deploy the Streamlit dashboard on AWS, capture deployment proof, complete optional containerization support, and prepare final submission artifacts.

---

## Executive Summary

The RiskRadar AI Streamlit dashboard has been deployed on AWS EC2 and is accessible through the EC2 public IP on port `8501`. The deployment uses the pushed GitHub repository, a Python virtual environment, S3-backed file storage, local FAISS policy retrieval, deterministic investigation summaries by default, and optional Gemini-assisted summaries behind a feature flag.

Optional Docker containerization has also been added for reproducible local setup. The project can be built as a Docker image and run with two commands, without requiring Docker Compose.

The live deployment flow is:

```text
AWS EC2 instance
      -> GitHub project clone
      -> Python virtual environment
      -> Amazon S3 file/document storage
      -> Streamlit app on port 8501
      -> public browser access
      -> live fraud investigation demo
```

---

## AWS Deployment Summary

### EC2 Configuration

- **Cloud provider:** AWS
- **Service:** EC2
- **Region:** Asia Pacific, Sydney
- **Operating system:** Ubuntu 24.04 LTS
- **Instance type:** `t3.micro`
- **Storage:** 20 GiB gp3 root volume
- **Application port:** `8501`
- **App URL:** `http://3.27.206.137:8501`

### S3 Storage Configuration

- **Service:** Amazon S3
- **Bucket:** `riskradar-ai-storage-alkarth`
- **Prefix:** `riskradar/`
- **IAM role attached to EC2:** `RiskRadarEC2S3Role`
- **IAM policy:** `RiskRadarS3StoragePolicy`
- **Storage mode flag:** `USE_S3_STORAGE=true`

S3 object layout:

```text
s3://riskradar-ai-storage-alkarth/riskradar/data/synthetic/transactions.csv
s3://riskradar-ai-storage-alkarth/riskradar/data/policies/
s3://riskradar-ai-storage-alkarth/riskradar/data/feedback/feedback_log.csv
```

Purpose:

- Store the synthetic transaction dataset outside the EC2 root disk.
- Store fraud policy documents used by the RAG pipeline.
- Persist analyst feedback and decision history as an audit file.

### Security Group Rules

Inbound rules configured for the demo:

| Type | Protocol | Port | Purpose |
| --- | --- | --- | --- |
| SSH | TCP | 22 | Server login and maintenance |
| Custom TCP | TCP | 8501 | Streamlit dashboard access |

The `8501` rule is required because Streamlit serves the dashboard on port `8501`.

---

## Deployment Steps Completed

### 1. EC2 Instance Setup

- Launched an Ubuntu 24.04 LTS EC2 instance.
- Selected `t3.micro` to stay close to free-tier/demo constraints.
- Configured root storage with 20 GiB gp3 to provide enough space for Python dependencies, FAISS, and model cache.
- Created and used an RSA `.pem` key pair for SSH access.

### 2. Server Access

SSH access was configured using the EC2 private key:

```bash
ssh -i /Users/karthikal/RiskRadar_AI/riskradar_key.pem ubuntu@3.27.206.137
```

The private key file was protected locally with:

```bash
chmod 600 /Users/karthikal/RiskRadar_AI/riskradar_key.pem
```

The `.pem` key is ignored by git and must not be committed.

### 3. System Packages

Installed required Ubuntu packages:

```bash
sudo apt-get update
sudo apt-get install -y git python3-venv python3-pip build-essential
```

Purpose:

- `git`: clone the project repository.
- `python3-venv`: create an isolated Python environment.
- `python3-pip`: install Python dependencies.
- `build-essential`: provide compiler tools for packages that need native builds.

### 4. Project Clone

Cloned the GitHub repository onto EC2:

```bash
git clone https://github.com/Alkarth2010/RiskRadar_AI.git
cd RiskRadar_AI
```

### 5. Swap Memory

Added a 2 GiB swap file to support dependency installation on the small `t3.micro` instance:

```bash
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
free -h
```

This helped prevent memory-related installation failures during heavy Python package setup.

### 6. Python Environment

Created and activated the project virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip setuptools wheel
```

### 7. CPU-Only PyTorch Optimization

The first dependency install attempted to download large GPU/CUDA-related PyTorch packages, which are unnecessary for a CPU-only EC2 instance.

To keep deployment lightweight, CPU-only PyTorch was installed first:

```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

Then the project dependencies were installed:

```bash
pip install -r requirements.txt
```

This allowed `sentence-transformers` to reuse the CPU-only PyTorch package instead of pulling GPU packages.

### 8. Environment Configuration

Created `.env` on EC2:

```env
USE_LLM_SUMMARY=false
GEMINI_MODEL=gemini-2.5-flash
GOOGLE_API_KEY=<configured on EC2 only>
USE_S3_STORAGE=true
AWS_REGION=ap-southeast-2
S3_BUCKET=riskradar-ai-storage-alkarth
S3_PREFIX=riskradar
```

Default mode remains:

```env
USE_LLM_SUMMARY=false
```

This keeps normal demos deterministic and protects free-tier Gemini quota.

### 9. S3 File Storage Setup

Created the S3 bucket:

```bash
aws s3 mb s3://riskradar-ai-storage-alkarth --region ap-southeast-2
```

Uploaded the existing project data files:

```bash
aws s3 cp data/synthetic/transactions.csv \
  s3://riskradar-ai-storage-alkarth/riskradar/data/synthetic/transactions.csv

aws s3 cp data/policies/ \
  s3://riskradar-ai-storage-alkarth/riskradar/data/policies/ \
  --recursive

aws s3 cp data/feedback_log.csv \
  s3://riskradar-ai-storage-alkarth/riskradar/data/feedback/feedback_log.csv
```

Verified uploaded objects:

```text
riskradar/data/feedback/feedback_log.csv
riskradar/data/policies/Device_and_Payment_Instrument_Policy.txt
riskradar/data/policies/Geographic_Anomaly_Policy.txt
riskradar/data/policies/High_Value_Transaction_Policy.txt
riskradar/data/policies/Velocity_and_Burst_Detection_Policy.txt
riskradar/data/synthetic/transactions.csv
```

Attached `RiskRadarEC2S3Role` to the EC2 instance and verified AWS identity:

```text
arn:aws:sts::614935468781:assumed-role/RiskRadarEC2S3Role/i-05bd02b4c98c239bc
```

Installed `boto3` in the project virtual environment and added it to `requirements.txt`.

### 10. S3-Backed Code Updates

Added reusable S3 storage helpers in:

```text
src/utils/s3_storage.py
```

Updated application storage behavior:

- `src/utils/data_loader.py` downloads `transactions.csv` from S3 when `USE_S3_STORAGE=true`.
- `src/rag/rag_pipeline.py` downloads policy `.txt` documents from S3 before building the FAISS index.
- `src/utils/feedback_logger.py` syncs `feedback_log.csv` from S3 before writes and uploads the updated file back to S3.
- `streamlit_app/app.py` refreshes Decision History from the S3-backed feedback log.
- `.cache/` was added to `.gitignore` so downloaded S3 cache files are not committed.

### 11. Streamlit Startup

Started the deployed dashboard with:

```bash
nohup streamlit run streamlit_app/app.py \
  --server.address 0.0.0.0 \
  --server.port 8501 \
  > streamlit.log 2>&1 &
```

Explanation:

- `streamlit run streamlit_app/app.py`: starts the dashboard.
- `--server.address 0.0.0.0`: allows access from outside the EC2 instance.
- `--server.port 8501`: uses the Streamlit app port.
- `nohup`: keeps the app running after the SSH session closes.
- `streamlit.log`: stores app logs for troubleshooting.

---

## Issues Found and Resolved

### Issue 1: Public App Access Blocked

The app initially worked inside EC2 but was not reachable from the browser.

Root cause:

- AWS Security Group did not allow inbound traffic on port `8501`.

Fix:

- Added inbound rule:

```text
Custom TCP | TCP | 8501 | Streamlit app
```

Result:

- Public browser access worked at `http://3.27.206.137:8501`.

### Issue 2: Policy Sources Blank on AWS

The deployed app showed an empty Sources section and the trace displayed:

```text
Policy evidence analyst failed; fallback evidence path used
```

Root cause:

- `RiskRadarRAG.__init__()` required `GOOGLE_API_KEY` even for local FAISS policy retrieval.
- Policy retrieval should not require Gemini because it uses local embeddings, FAISS, and policy text files.

Fix:

- Updated `src/rag/rag_pipeline.py` so FAISS-based policy retrieval works without `GOOGLE_API_KEY`.
- Kept the API key requirement only for LLM policy Q&A.

Result:

- Live AWS investigation now shows policy sources correctly.
- Example source output:
  - `Device_and_Payment_Instrument_Policy.txt`
  - `High_Value_Transaction_Policy.txt`
  - `Geographic_Anomaly_Policy.txt`
  - `Velocity_and_Burst_Detection_Policy.txt`

### Issue 3: Optional Gemini Summary Mode

Gemini-assisted summary mode was tested on EC2.

Result:

- `USE_LLM_SUMMARY=true` worked successfully.
- After verification, the setting was changed back to `USE_LLM_SUMMARY=false`.

Reason:

- Deterministic mode avoids unnecessary free-tier LLM usage during normal demos.
- LLM mode can still be enabled for a final demo if needed.

### Issue 4: EC2 Missing AWS Credentials

The EC2 instance initially returned:

```text
NoCredentials: Unable to locate credentials
```

Root cause:

- The EC2 instance did not have an IAM instance profile attached.

Fix:

- Created `RiskRadarS3StoragePolicy`.
- Created `RiskRadarEC2S3Role`.
- Attached the role to the running EC2 instance.

Result:

- EC2 can access S3 without storing AWS access keys on the server.

### Issue 5: Exposed Gemini Key Rotated

During deployment work, the existing Gemini key was treated as exposed.

Fix:

- Created a new Gemini API key.
- Updated the EC2 `.env` file.
- Restarted Streamlit.
- Removed the old key from Google Cloud credentials.

Result:

- The deployed app works with the rotated key, and the exposed key is no longer active.

---

## Deployment Verification

### Public URL Check

The public deployed app responded successfully:

```bash
curl -I http://3.27.206.137:8501
```

Expected response:

```text
HTTP/1.1 200 OK
```

### App Workflow Check

Verified on deployed app:

- Alert queue loads.
- Investigation runs.
- Workflow risk and recommendation display.
- Parallel agent trace displays.
- Policy source documents display.
- Decision History remains available.

### S3 Storage Check

Verified S3-backed application behavior:

- `load_transactions()` returns `(200, 14)` from the S3-backed transaction CSV.
- `RiskRadarRAG()` loads four policy documents from S3 and builds the FAISS index successfully.
- `save_feedback()` appends analyst feedback locally and uploads the updated `feedback_log.csv` back to S3.
- The live Streamlit app works after enabling `USE_S3_STORAGE=true`.

### LLM Mode Check

Verified:

- `USE_LLM_SUMMARY=true` can run with Gemini key configured on EC2.
- App was returned to `USE_LLM_SUMMARY=false` after test.

### Docker Containerization Check

Optional Docker support was added and validated locally.

Added files:

- `Dockerfile`
- `.dockerignore`

The Docker flow intentionally uses direct Docker CLI commands rather than
`docker-compose.yml`.

Build command:

```bash
docker build -t riskradar-ai .
```

Run command:

```bash
docker run --rm -p 8501:8501 --env-file .env -v "$PWD/data:/app/data" riskradar-ai
```

Verified:

- Docker image build completed successfully.
- Container started successfully.
- Streamlit app loaded at `http://localhost:8501`.
- `data/` was mounted into the container so analyst feedback can persist on the host machine.
- Docker run instructions were added to `README.md`.

---

## Screenshot Evidence

AWS deployment screenshots are stored in:

```text
docs/screenshots/aws_deployment/
```

Captured evidence:

| Screenshot | Purpose |
| --- | --- |
| `aws_01_ec2_instance_running.png` | EC2 instance running with public IP and instance details |
| `aws_02_security_group_inbound_rules.png` | Security Group rules showing SSH `22` and Streamlit `8501` |
| `aws_03_live_app_home.png` | Live deployed RiskRadar AI dashboard |
| `aws_04_live_investigation_sources.png` | Live deployed investigation result with policy sources |

---

## RFP Alignment

| RFP Requirement | Current Status | Evidence |
| --- | --- | --- |
| AWS deployment | Complete | EC2 instance running and public Streamlit URL |
| S3 document/file storage | Complete | Synthetic data, policy documents, and feedback log stored in S3 |
| Frontend/dashboard | Complete | Streamlit dashboard deployed on EC2 |
| Agent workflow | Complete | Live investigation runs through LangGraph workflow |
| RAG pipeline | Complete | FAISS policy retrieval displays policy sources |
| Human approval step | Complete | Analyst decision controls and Decision History available |
| Optional Docker containerization | Complete | Dockerfile, .dockerignore, README commands, and verified local container run |
| Error handling | Partially complete | Workflow fallback and UI warnings exist; final report should document this |
| Screenshots/demo evidence | In progress | AWS deployment screenshots captured |
| Final report/PPT/recording | Pending | Week 4 remaining work |

---

## Known Notes

- `USE_LLM_SUMMARY=false` is the recommended default for normal development and screenshots.
- Gemini key is configured only on EC2 and must not be committed to GitHub.
- S3 access is provided through the EC2 IAM role, not through stored AWS keys.
- `.env`, `.pem`, `data/feedback_log.csv`, logs, and `.cache/` are ignored by git.
- Docker is optional for the RFP submission and is documented as a two-command build/run flow, without Docker Compose.
- Security Group should be tightened after demo use if public access is no longer needed.
- Current tests are script-style tests, not full pytest-collected tests.
- Streamlit and dependency deprecation warnings appear in logs but do not block the deployed app.

---

## Remaining Week 4 Tasks

1. Prepare final report using Week 1, Week 2, Week 3, and Week 4 progress documents.
2. Add AWS deployment screenshots to the final report.
3. Prepare final PPT with architecture, workflow, RAG, human approval, AWS deployment, optional Docker support, and demo screenshots.
4. Record the final presentation/demo walkthrough.
5. Package submission artifacts:
   - Source code
   - Synthetic dataset
   - Policy documents
   - Final report
   - Final PPT
   - Demo recording
   - AWS deployment proof screenshots
   - Dockerfile and Docker run instructions
6. Keep all artifacts ready by the internal target date of 25 June 2026.
7. Submit before the updated final RFP deadline of 30 June 2026.
