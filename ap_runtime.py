import os
import sys
os.environ["GOOGLE_API_USE_CLIENT_CERTIFICATE"] = "false"
os.environ["GOOGLE_API_USE_MTLS_ENDPOINT"] = "never"
import vertexai
from dotenv import load_dotenv
from vertexai.agent_engines import AdkApp

# -----------------------------------------------------------------------------
# Dynamic Working Directory Alignment
# -----------------------------------------------------------------------------
# Dynamically change the current working directory (CWD) to the parent folder
# of the project root (~/workspace/agents/). This guarantees that:
# 1. The local package imports use the canonical 'bq_mcp_agent.agent' path.
# 2. The GenAI SDK packages the extra files preserving the 'bq_mcp_agent/' namespace.
# 3. The remote Control Plane successfully unpickles the agent with zero ModuleNotFoundErrors.
# -----------------------------------------------------------------------------
project_parent = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
os.chdir(project_parent)
if project_parent not in sys.path:
    sys.path.insert(0, project_parent)

# Load configurations dynamically from .env
load_dotenv(os.path.join(project_parent, "bq_mcp_agent/.env"))

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "gcp-sandbox-kwlee")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
if LOCATION == "global":
    LOCATION = "us-central1"  # Agent Engine is deployed regionally

# 1. Initialize the modern AgentPlatform Client with v1beta1 for Agent Identity support
from vertexai import types as vertexai_types

client = vertexai.Client(
    project=PROJECT_ID,
    location=LOCATION,
    http_options=dict(api_version="v1beta1")
)

# Import the Data Science root agent using the fully qualified package namespace
from bq_mcp_agent.agent import root_agent

# 2. Wrap BigQuery MCP agent inside AdkApp wrapper
adk_app = AdkApp(agent=root_agent)

# -----------------------------------------------------------------------------
# Environment variables dynamically loaded from .env
# -----------------------------------------------------------------------------
bq_env_keys = [
    "GEMINI_MODEL",
    "GOOGLE_GENAI_USE_VERTEXAI",
    "GOOGLE_CLOUD_PROJECT",
    "GOOGLE_CLOUD_LOCATION",
    "GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY",
    "OTEL_SEMCONV_STABILITY_OPT_IN",
    "OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT",
]
env_vars = {key: os.environ[key] for key in bq_env_keys if key in os.environ}

# -----------------------------------------------------------------------------
# Explicitly append Production Runtime URIs to the env_vars payload dictionary
# -----------------------------------------------------------------------------
env_vars["ADK_SESSION_SERVICE_URI"] = "agentengine://"
env_vars["ADK_MEMORY_SERVICE_URI"] = "agentengine://"
env_vars["ADK_ARTIFACT_SERVICE_URI"] = "gs://adk-sandbox-bucket"

# -----------------------------------------------------------------------------
# Production Single-Step Deployment Flow (Simultaneous Session & Memory Activation)
# -----------------------------------------------------------------------------
print(f"Deploying 'bq_mcp_agent' to AgentPlatform in a single step...")

# Construct the staging bucket dynamically
staging_bucket_uri = os.environ.get("ADK_ARTIFACT_SERVICE_URI", f"gs://adk-sandbox-bucket")

# Deploy and activate session and memory services simultaneously using the official agent=adk_app specs
remote_agent = client.agent_engines.create(
    agent=adk_app,
    config={
        "display_name": "BigQuery MCP Agent",
        "description": "Expert Data Science Agent for querying enterprise BigQuery datasets, analyzing data, and summarizing findings.",
        "requirements": [
            "google-genai",
            "google-auth>=2.53.0",
            "google-adk[agent-identity]>=2.1.0",
            "a2a-sdk>=0.3.4,<0.4",
            "mcp>=1.27.1",
            "google-cloud-aiplatform[agent_engines,adk]",
            "python-dotenv",
            "pydantic",
            "cloudpickle",
            "pyyaml",
            "google-api-core",
        ],
        "extra_packages": [
            "bq_mcp_agent/agent.py",
            "bq_mcp_agent/__init__.py",
        ],
        "env_vars": env_vars,
        "identity_type": vertexai_types.IdentityType.AGENT_IDENTITY,
        "staging_bucket": staging_bucket_uri,
    }
)

print(f"\nSUCCESS: Agent deployed successfully to Agent Runtime!")
print(f"AgentPlatform Resource Name: {remote_agent.api_resource.name}")
print(f"To run chat sessions on this deployed agent, use the resource URI: {remote_agent.api_resource.name}")
