import os

from google.adk.integrations.agent_registry import AgentRegistry
from google.adk.agents import Agent
from google.adk.models import Gemini
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools.preload_memory_tool import PreloadMemoryTool

from google.auth import default
from google.genai import types
from google.adk.apps import App

project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
location = os.environ.get("GOOGLE_CLOUD_LOCATION", "global")

if not project_id:
    raise ValueError("GOOGLE_CLOUD_PROJECT environment variable not set.")

# Initialize the client
registry = AgentRegistry(
    project_id=project_id,
    location=location,
)

# Retrieve an MCP toolset using its resource name in short or full format
# Short formats automatically imply the client's configured project and location
# Short format: "mcpServers/SERVER_ID"
# Full format: f"projects/{project_id}/locations/{location}/mcpServers/SERVER_ID"
mcp_toolset = registry.get_mcp_toolset(
    f"projects/gcp-sandbox-kwlee/locations/global/mcpServers/agentregistry-00000000-0000-0000-3781-81d342859334"
)

async def add_session_to_memory_callback(callback_context: CallbackContext):
    """Ensures conversation continuity by triggering memory generation."""
    try:
        await callback_context.add_session_to_memory()
    except ValueError:
        pass


root_agent = Agent(
    name="bq_mcp_agent",
    model=Gemini(
            model="gemini-flash-latest",
            retry_options=types.HttpRetryOptions(attempts=3),
        ),
    instruction=(
        "You are an expert Data Science Agent. "
        "Your goal is to query enterprise BigQuery datasets, analyze the data, "
        "and summarize your findings. "
        f"When executing SQL queries, use project_id `{project_id}` as the "
        "billing project unless the user specifies a different one. "
        "Present results clearly with formatted numbers. "
        "Remember user preferences like preferred regions, date ranges, "
        "or analysis formats across conversations."
    ),
    tools=[mcp_toolset, PreloadMemoryTool()],
    after_agent_callback=add_session_to_memory_callback,
)

app = App(
    name="bq_mcp_agent",
    root_agent=root_agent,
)