# BigQuery MCP Data Science Agent

An enterprise-grade, high-speed **Single-Agent Data Science Architect** built on the Google **ADK (Agent Development Kit)** framework. This agent directly utilizes the **GCP Agent Registry** and **BigQuery MCP (Model Context Protocol)** toolsets to query enterprise datasets, execute SQL analytics, and generate beautiful summarized reports.

---

## 🚀 Core Features

*   **Managed MCP Integration**: Utilizes the native GCP Agent Registry to resolve and securely attach enterprise BigQuery MCP toolsets in a single, high-speed flow.
*   **Memory Bank Integration**: Supports `PreloadMemoryTool` and `add_session_to_memory_callback` for continuous, cross-session conversational memory on production Agent Engine environments.
*   **Unified Python Environment**: Packaged and optimized via `uv` for seamless, robust dependency resolution and virtual environment management.
*   **Seamless Production Deployment**: Supported by a production-ready Vertex AI Agent Engine (Reasoning Engine) deployment script ([ap_runtime.py](file:///usr/local/google/home/kiwonlee/workspace/agents/bq_mcp_agent/ap_runtime.py)).

---

## 📁 Repository Directory Layout

```
bq_mcp_agent/
├── README.md               # Developer manual and instructions
├── pyproject.toml          # Python package and dependency configurations
├── uv.lock                 # Locked dependencies
├── .env                    # Local environment variables
├── __init__.py             # Exposes app and root_agent
├── agent.py                # Single-Agent Data Science definition
└── ap_runtime.py           # Production one-click Vertex AI Agent Runtime deployment script
```

---

## ⚙️ Setup & Configuration

### 1. Environment File (`.env`)
Ensure a `.env` file exists in the root of `bq_mcp_agent/` with your GCP project variables and target model:

```ini
# Project configurations
GOOGLE_CLOUD_PROJECT="gcp-sandbox-kwlee"
GOOGLE_CLOUD_LOCATION="global"
GOOGLE_GENAI_USE_VERTEXAI=TRUE

# Disable mTLS to bypass local OpenSSL decoding issues during deployment
GOOGLE_API_USE_CLIENT_CERTIFICATE="false"
GOOGLE_API_USE_MTLS_ENDPOINT="never"
```

### 2. Dependency Resolution
Resolve and lock all ADK, GCP, and MCP dependencies using `uv`:

```bash
uv sync
```

---

## 💻 Execution Commands

Run all command variants directly from the `bq_mcp_agent/` root directory:

### A. Launch Interactive CLI Mode
To boot up a real-time conversational command-line session directly inside your terminal, run:
```bash
uv run adk run .
```

### B. Launch the Developer Web UI
To launch the background FastAPI server and interact via the Web UI interface:
```bash
uv run adk web .
```
Once initialized, navigate your browser to the URL printed in the terminal (usually `http://127.0.0.1:8086/dev-ui/`).

---

## 🚀 Gemini Enterprise Agent Runtime Deployment (Vertex AI Agent Engine)

For serverless, managed API deployments, you can upload this Data Science Orchestrator Agent to **Vertex AI Agent Engine (Reasoning Engine)**.

### 1. Provision the Dedicated Service Account
Create a custom service account and bind the required permissions (BigQuery Data Viewer, BigQuery Job User, Storage Admin, Vertex AI User):

```bash
export PROJECT_ID="gcp-sandbox-kwlee"
export SA_EMAIL="bq-mcp-agent-sa@${PROJECT_ID}.iam.gserviceaccount.com"

# Create the Service Account
gcloud iam service-accounts create bq-mcp-agent-sa \
    --description="Managed Service Account for BigQuery MCP Orchestrator Agent" \
    --display-name="BigQuery MCP Agent SA"

# Grant BigQuery access
gcloud projects add-iam-policy-binding ${PROJECT_ID} --member="serviceAccount:${SA_EMAIL}" --role="roles/bigquery.dataViewer"
gcloud projects add-iam-policy-binding ${PROJECT_ID} --member="serviceAccount:${SA_EMAIL}" --role="roles/bigquery.jobUser"

# Grant Vertex AI & GCS Storage permissions
gcloud projects add-iam-policy-binding ${PROJECT_ID} --member="serviceAccount:${SA_EMAIL}" --role="roles/aiplatform.user"
gcloud projects add-iam-policy-binding ${PROJECT_ID} --member="serviceAccount:${SA_EMAIL}" --role="roles/storage.objectAdmin"

# Grant Service Account User role to your deployer account
gcloud iam service-accounts add-iam-policy-binding ${SA_EMAIL} \
    --member="user:YOUR_GOOGLE_EMAIL@google.com" \
    --role="roles/iam.serviceAccountUser"
```

### 2. Execute the Deployment Script
Once `.env` configurations are finalized, execute the dedicated [ap_runtime.py](file:///usr/local/google/home/kiwonlee/workspace/agents/bq_mcp_agent/ap_runtime.py) script with `uv`:

```bash
uv run python ap_runtime.py
```

Upon successful deployment, the script will print the remote Resource URI that you can use to stream and trigger remote data-science chat sessions:
`projects/{project_number}/locations/us-central1/reasoningEngines/{engine_id}`
