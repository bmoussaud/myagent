import os
import asyncio
import logging
import semantic_kernel as sk
from dotenv import load_dotenv
from semantic_kernel.utils.logging import setup_logging
from semantic_kernel.planners.sequential_planner import SequentialPlanner
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from semantic_kernel.connectors.ai.open_ai.services.open_ai_chat_completion import OpenAIChatCompletion
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.connectors.ai.open_ai.prompt_execution_settings.azure_chat_prompt_execution_settings import (
    AzureChatPromptExecutionSettings,
)
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.agents import ChatCompletionAgent, ChatHistoryAgentThread
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.functions import KernelArguments

from setlist_client import SetlistFMClient
from setlist_agent import SetlistFMPlugin
from config import enable_telemetry,get_logger

from azure.monitor.opentelemetry import configure_azure_monitor

    
#configure_azure_monitor(connection_string=application_insights_connection_string)

async def main():
    # Load environment variables from .env file
    load_dotenv()
    
    # Get API keys from environment variables
    setlist_api_key = os.environ.get("SETLISTFM_API_KEY", "YOUR_API_KEY")
    
    # Create kernel and add OpenAI chat service
    kernel = sk.Kernel()
    kernel.add_service(AzureChatCompletion(service_id='agent'))

    # Set the logging level for  semantic_kernel.kernel to DEBUG.
    setup_logging()
    logging.getLogger("kernel").setLevel(logging.DEBUG)
    

    # Import the SetlistFM plugin
    setlist_plugin = SetlistFMPlugin(setlist_api_key)
    kernel.add_plugin(setlist_plugin, "setlistfm")

    execution_settings = kernel.get_prompt_execution_settings_from_service_id(service_id='agent')
    execution_settings.function_choice_behavior = FunctionChoiceBehavior.Auto()

    # Create a chat history object
    agent = ChatCompletionAgent(
        kernel=kernel,
        name="SampleAssistantAgent",
        instructions=f"""
        You are a helpful music assistant that provides information about artists, concerts, and setlists.
        You can search for artists, find setlists from concerts, and provide venue information.
        
        When asked about an artist's concerts or setlists, use the SetlistFM plugin to search for that information.
        Always try to be helpful and provide as much relevant information as possible.
        
        If the user asks for something you can't do, politely explain your limitations.
        """,
        arguments=KernelArguments(
            settings=execution_settings,
        ),
    )

    enable_telemetry(log_to_project=False)
    thread: ChatHistoryAgentThread = None
    is_complete: bool = False
    while not is_complete:
        # processing logic here
        user_input = input("User:> ")
        if not user_input:
            continue

        if user_input.lower() == "enable_telemetry":
            # Enable telemetry logging to the project
            enable_telemetry(log_to_project=True)
            print("Telemetry logging enabled.")
            continue;

        if user_input.lower() == "exit":
            is_complete = True
            break
        
        async for response in agent.invoke(messages=user_input, thread=thread):
    
            print(f"{response.content}")
            thread = response.thread

if __name__ == "__main__":
    asyncio.run(main())
