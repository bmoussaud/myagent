# based on https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/agents/sample_agents_openapi_connection_auth.py
# https://learn.microsoft.com/en-us/azure/ai-services/agents/how-to/tools/openapi-spec?tabs=python&pivots=code-example
import os
import jsonref
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.projects.models import OpenApiTool, OpenApiConnectionAuthDetails, OpenApiConnectionSecurityScheme
from dotenv import load_dotenv
load_dotenv()

project_client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(),
    conn_str=os.environ["AIPROJECT_CONNECTION_STRING"],
)

connection_name = os.environ["PROJECT_OPENAPI_CONNECTION_NAME"]
model_name = os.environ["MODEL_DEPLOYMENT_NAME"]
connection = project_client.connections.get(connection_name=connection_name)

print(connection.id)

with open("./setlistfm_openapi.json", "r") as f:
    openapi_spec = jsonref.loads(f.read())

# Create Auth object for the OpenApiTool (note that connection or managed identity auth setup requires additional setup in Azure)
auth = OpenApiConnectionAuthDetails(
    security_scheme=OpenApiConnectionSecurityScheme(connection_id=connection.id))

# Initialize an Agent OpenApi tool using the read in OpenAPI spec
openapi = OpenApiTool(name="setlistsfm", spec=openapi_spec,
                      description="Retrieve information about  artists, find setlists from concerts, and provide venue information", auth=auth)

# print(openapi)
for definition in openapi.definitions:
    # print(definition)
    print('====')


instructions = f"""
        You are a helpful music assistant that provides information about artists, concerts, and setlists.
        You can search for artists, find setlists from concerts, and provide venue information.
        
        When asked about an artist's concerts or setlists, use the SetlistFM plugin to search for that information.
        Always try to be helpful and provide as much relevant information as possible.
        
        If the user asks for something you can't do, politely explain your limitations.
        """
# Create an Agent with OpenApi tool and process Agent run
with project_client:
    agent = project_client.agents.create_agent(
        model=model_name, name="my-setlist-agent", instructions=instructions, tools=openapi.definitions
    )
    print(f"Created agent, ID: {agent.id}")

    # Create thread for communication
    thread = project_client.agents.create_thread()
    print(f"Created thread, ID: {thread.id}")

    # Create message to thread
    message = project_client.agents.create_message(
        thread_id=thread.id,
        role="user",
        content="Give the last 4 shows performed by Muse",
    )
    print(f"Created message: {message['id']}")

    # Create and process an Agent run in thread with tools
    run = project_client.agents.create_and_process_run(
        thread_id=thread.id, agent_id=agent.id)
    print(f"Run finished with status: {run.status}")

    if run.status == "failed":
        print(f"Run failed: {run.last_error}")

    # Delete the Agent when done
    project_client.agents.delete_agent(agent.id)
    print("Deleted agent")

    # Fetch and log all messages
    messages = project_client.agents.list_messages(thread_id=thread.id)
    print(f"Messages: {messages}")
