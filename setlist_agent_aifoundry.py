# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to use basic agent operations with function tools from
    the Azure Agents service using a synchronous client with Azure Monitor tracing.
    View the results in the "Tracing" tab in your Azure AI Foundry project page.

USAGE:
    python sample_agents_functions_with_azure_monitor_tracing.py

    Before running the sample:

    pip install azure-ai-projects azure-identity opentelemetry-sdk azure-monitor-opentelemetry

    Set these environment variables with your own values:
    1) PROJECT_CONNECTION_STRING - The project connection string, as found in the overview page of your
       Azure AI Foundry project.
    2) MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Azure AI Foundry project.
    3) AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED - Optional. Set to `true` to trace the content of chat
       messages, which may contain personal data. False by default.
"""
from setlist_agent import SetlistFMPlugin
from typing import Any, Callable, Set

import os
import time
import json
from azure.ai.projects import AIProjectClient
from azure.ai.projects.telemetry import trace_function
from azure.identity import DefaultAzureCredential
from azure.ai.projects.models import FunctionTool, RequiredFunctionToolCall, SubmitToolOutputsAction, ToolOutput
from opentelemetry import trace
from azure.monitor.opentelemetry import configure_azure_monitor
from dotenv import load_dotenv
load_dotenv()

project_client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(), conn_str=os.environ["PROJECT_CONNECTION_STRING"]
)

# Enable Azure Monitor tracing
application_insights_connection_string = project_client.telemetry.get_connection_string()
if not application_insights_connection_string:
    print("Application Insights was not enabled for this project.")
    print("Enable it via the 'Tracing' tab in your AI Foundry project page.")
    exit()
configure_azure_monitor(
    connection_string=application_insights_connection_string)

# enable additional instrumentations if needed
project_client.telemetry.enable()

scenario = os.path.basename(__file__)
tracer = trace.get_tracer(__name__)

# The trace_func decorator will trace the function call and enable adding additional attributes
# to the span in the function implementation. Note that this will trace the function parameters and their values.
setlist_api_key = os.environ.get("SETLISTFM_API_KEY", "YOUR_API_KEY")


@trace_function()
def search_artists(artist_name: str) -> str:
    return SetlistFMPlugin(setlist_api_key).search_artists(artist_name)


@trace_function()
def search_setlists(self, artist_name: str = "", city_name: str = "", country_code: str = "") -> str:
    return SetlistFMPlugin(setlist_api_key).search_setlists(artist_name, city_name, country_code)


@trace_function()
def get_setlist(setlist_id: str) -> str:
    return SetlistFMPlugin(setlist_api_key).get_setlist(setlist_id)


# Statically defined user functions for fast reference
setlistfm_functions: Set[Callable[..., Any]] = {
    search_artists, search_setlists, get_setlist
}

# Initialize function tool with user function
functions = FunctionTool(functions=setlistfm_functions)


instructions = f"""
        You are a helpful music assistant that provides information about artists, concerts, and setlists.
        You can search for artists, find setlists from concerts, and provide venue information.
        
        When asked about an artist's concerts or setlists, use the SetlistFM plugin to search for that information.
        Always try to be helpful and provide as much relevant information as possible.
        
        If the user asks for something you can't do, politely explain your limitations.
        """

with tracer.start_as_current_span(scenario):
    with project_client:
        # Create an agent and run user's request with function calls
        agent = project_client.agents.create_agent(
            model=os.environ["MODEL_DEPLOYMENT_NAME"],
            name="my-setlist-aifoundry",
            instructions=instructions,
            tools=functions.definitions,
        )
        print(f"Created agent, ID: {agent.id}")

        thread = project_client.agents.create_thread()
        print(f"Created thread, ID: {thread.id}")

        message = project_client.agents.create_message(
            thread_id=thread.id,
            role="user",
            content="Quelle est la set list du dernier concert de Jul?",
        )
        print(f"Created message, ID: {message.id}")

        run = project_client.agents.create_run(
            thread_id=thread.id, agent_id=agent.id)
        print(f"Created run, ID: {run.id}")

        while run.status in ["queued", "in_progress", "requires_action"]:
            time.sleep(1)
            run = project_client.agents.get_run(
                thread_id=thread.id, run_id=run.id)

            if run.status == "requires_action" and isinstance(run.required_action, SubmitToolOutputsAction):
                tool_calls = run.required_action.submit_tool_outputs.tool_calls
                if not tool_calls:
                    print("No tool calls provided - cancelling run")
                    project_client.agents.cancel_run(
                        thread_id=thread.id, run_id=run.id)
                    break

                tool_outputs = []
                for tool_call in tool_calls:
                    if isinstance(tool_call, RequiredFunctionToolCall):
                        try:
                            output = functions.execute(tool_call)
                            tool_outputs.append(
                                ToolOutput(
                                    tool_call_id=tool_call.id,
                                    output=output,
                                )
                            )
                        except Exception as e:
                            print(
                                f"Error executing tool_call {tool_call.id}: {e}")

                print(f"Tool outputs: {tool_outputs}")
                if tool_outputs:
                    project_client.agents.submit_tool_outputs_to_run(
                        thread_id=thread.id, run_id=run.id, tool_outputs=tool_outputs
                    )

            print(f"Current run status: {run.status}")

        print(f"Run completed with status: {run.status}")

        # Delete the agent when done
        project_client.agents.delete_agent(agent.id)
        print("Deleted agent")

        # Fetch and log all messages
        messages = project_client.agents.list_messages(thread_id=thread.id)
        print(f"Messages: {messages}")
