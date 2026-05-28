import os
import sys
from dotenv import load_dotenv
from vertexai.agent_engines import AdkApp

# =====================================================================
# 1. ENVIRONMENT & mTLS CONFIGURATION
# =====================================================================
# Bypass local OpenSSL mTLS decoder routine issues dynamically
os.environ["GOOGLE_API_USE_CLIENT_CERTIFICATE"] = "false"
os.environ["GOOGLE_API_USE_MTLS_ENDPOINT"] = "never"

# Set up project path namespaces
project_parent = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
os.chdir(project_parent)
if project_parent not in sys.path:
    sys.path.insert(0, project_parent)

# Load configurations from the project's .env file
load_dotenv(os.path.join(project_parent, "bq_mcp_agent/.env"))

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "gcp-sandbox-kwlee")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
if LOCATION == "global":
    LOCATION = "us-central1"

# =====================================================================
# 2. CLIENT & AGENT PLATFORM INITIALIZATION
# =====================================================================
import vertexai
from vertexai import types as vertexai_types

# Initialize client with v1beta1 support for Agent Identity
client = vertexai.Client(
    project=PROJECT_ID,
    location=LOCATION,
    http_options=dict(api_version="v1beta1")
)

# Import and wrap the Data Science app
from bq_mcp_agent.agent import app
adk_app = AdkApp(app=app)

# =====================================================================
# 3. DEPLOYMENT PAYLOAD VARIABLES
# =====================================================================
bq_env_keys = [
    "GEMINI_MODEL",
    "GOOGLE_GENAI_USE_VERTEXAI",
    "GOOGLE_CLOUD_LOCATION",
    "GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY",
    "OTEL_SEMCONV_STABILITY_OPT_IN",
    "OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT",
]

env_vars = {key: os.environ[key] for key in bq_env_keys if key in os.environ}

# Add managed runtime URIs for Session, Memory, and Artifact services
env_vars["ADK_SESSION_SERVICE_URI"] = "agentengine://"
env_vars["ADK_MEMORY_SERVICE_URI"] = "agentengine://"
env_vars["ADK_ARTIFACT_SERVICE_URI"] = "gs://adk-sandbox-bucket"

staging_bucket_uri = os.environ.get("ADK_ARTIFACT_SERVICE_URI", "gs://adk-sandbox-bucket")

requirements_list = [
    "google-genai",
    "google-auth>=2.53.0",
    "google-adk[agent-identity]>=2.1.0",
    "a2a-sdk>=0.3.4,<0.4",
    "mcp>=1.27.1",
    "google-cloud-aiplatform[agent_engines]>=1.154.0",
    "python-dotenv",
    "pydantic",
    "cloudpickle",
    "pyyaml",
    "google-api-core",
]

# =====================================================================
# 4. EXECUTE AGENT ENGINE DEPLOYMENT
# =====================================================================
print(f"Deploying 'bq_mcp_agent' to AgentPlatform in a single step...")

remote_agent = client.agent_engines.create(
    agent=adk_app,
    config={
        "display_name": "BigQuery MCP Agent",
        "description": "Expert Data Science Agent for querying enterprise BigQuery datasets, analyzing data, and summarizing findings.",
        "requirements": requirements_list,
        "extra_packages": ["bq_mcp_agent"],
        "env_vars": env_vars,
        "identity_type": vertexai_types.IdentityType.AGENT_IDENTITY,
        "staging_bucket": staging_bucket_uri,
    }
)

# =====================================================================
# 5. DEPLOYMENT SUCCESS REPORTING
# =====================================================================
print(f"\nSUCCESS: Agent deployed successfully to Agent Runtime!")
print(f"AgentPlatform Resource Name: {remote_agent.api_resource.name}")
print(f"To run chat sessions on this deployed agent, use the resource URI: {remote_agent.api_resource.name}")
