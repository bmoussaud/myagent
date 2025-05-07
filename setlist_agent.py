

from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from semantic_kernel.functions import KernelArguments
from semantic_kernel.agents import ChatCompletionAgent, ChatHistoryAgentThread
import json
import os
import logging
import semantic_kernel as sk
from semantic_kernel.functions import kernel_function
from dotenv import load_dotenv
from setlist_client import SetlistFMClient
from opentelemetry.trace import get_tracer
from opentelemetry import trace
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from azure.core.settings import settings
settings.tracing_implementation = "opentelemetry"

# Setup tracing to console
# span_exporter = ConsoleSpanExporter()
# tracer_provider = TracerProvider()
# tracer_provider.add_span_processor(SimpleSpanProcessor(span_exporter))
# trace.set_tracer_provider(tracer_provider)
# /Setup tracing to console
tracer = get_tracer(__name__)


class SetlistFMPlugin:
    def __init__(self, api_key):
        """Initialize the SetlistFMPlugin with a valid API key."""
        self.client = SetlistFMClient(api_key=api_key)

    @kernel_function(
        description="Search for an artist by name",
        name="search_artists"
    )
    def search_artists(self, artist_name: str) -> str:
        """Search for artists matching a given name.

        Args:
            artist_name: The name of the artist to search for.

        Returns:
            A JSON string containing information about matching artists.
        """
        trace.get_current_span().set_attribute("artist_name", artist_name)
        try:
            result = self.client.search_artists(artist_name)
            # Format the output nicely for the agent
            return json.dumps(result, indent=2)
        except Exception as e:
            return f"Error searching for artist: {str(e)}"

    @kernel_function(
        description="Search for setlists by artist name, city name, or country code",
        name="search_setlists"
    )
    def search_setlists(self, artist_name: str = "", city_name: str = "", country_code: str = "") -> str:
        """Search for setlists by artist name, city name, or country code.

        Args:
            artist_name: Optional name of the artist.
            city_name: Optional name of the city.
            country_code: Optional country code.

        Returns:
            A JSON string containing information about matching setlists.
        """
        try:
            span = trace.get_current_span()
            span.set_attribute(
                "artist_name", artist_name if artist_name else 'empty')
            span.set_attribute(
                "city_name", city_name if city_name else 'empty')
            span.set_attribute(
                "country_code", country_code if country_code else 'empty')
            result = self.client.search_setlists(
                artist_name=artist_name if artist_name else None,
                city_name=city_name if city_name else None,
                country_code=country_code if country_code else None
            )
            return json.dumps(result, indent=2)
        except Exception as e:
            return f"Error searching for setlists: {str(e)}"

    @kernel_function(
        description="Get a specific setlist by its ID",
        name="get_setlist"
    )
    def get_setlist(self, setlist_id: str) -> str:
        """Get details of a specific setlist by its ID.

        Args:
            setlist_id: The ID of the setlist to retrieve.

        Returns:
            A JSON string containing information about the setlist.
        """
        try:
            trace.get_current_span().set_attribute("setlist_id", setlist_id)
            result = self.client.get_setlist(setlist_id)
            return json.dumps(result, indent=2)
        except Exception as e:
            return f"Error getting setlist: {str(e)}"

    @kernel_function(
        description="Get venue information by venue ID",
        name="get_venue"
    )
    def get_venue(self, venue_id: str) -> str:
        """Get details of a specific venue by its ID.

        Args:
            venue_id: The ID of the venue to retrieve.

        Returns:
            A JSON string containing information about the venue.
        """
        try:
            trace.get_current_span().set_attribute("venue_id", venue_id)
            result = self.client.get_venue(venue_id)
            return json.dumps(result, indent=2)
        except Exception as e:
            return f"Error getting venue: {str(e)}"


class SetlistFMAgent:
    def __init__(self, api_key, model_name="gpt-3.5-turbo", api_key_env="OPENAI_API_KEY"):
        """
        Initialize the Setlist.fm Agent.

        Args:
            api_key: Setlist.fm API key
            model_name: Name of the OpenAI model to use
            api_key_env: Name of the environment variable containing the OpenAI API key
        """
        # Set up the Semantic Kernel
        self.kernel = sk.Kernel()

        # Configure OpenAI chat service
        openai_api_key = os.environ.get(api_key_env)
        if not openai_api_key:
            raise ValueError(
                f"Please set the {api_key_env} environment variable")

        self.kernel.add_service(AzureChatCompletion(
            service_id='Agent', deployment_name=model_name))

        # Import the SetlistFM plugin
        self.setlist_plugin = SetlistFMPlugin(api_key)
        self.kernel.add_plugin(self.setlist_plugin, "SetlistFM")

        execution_settings = self.kernel.get_prompt_execution_settings_from_service_id(
            service_id='Agent')
        execution_settings.function_choice_behavior = FunctionChoiceBehavior.Auto()

        # Create system prompt for the agent
        self.system_prompt = """
            You are a helpful music assistant that provides information about artists, concerts, and setlists.
            You can search for artists, find setlists from concerts, and provide venue information.

            When asked about an artist's concerts or setlists, use the SetlistFM plugin to search for that information.
            Always try to be helpful and provide as much relevant information as possible.

            If the user asks for something you can't do, politely explain your limitations.
            """
        self.agent = ChatCompletionAgent(
            kernel=self.kernel,
            name="MySetListAgent",
            instructions=self.system_prompt,
            arguments=KernelArguments(
                settings=execution_settings,
            ))
        self.thread: ChatHistoryAgentThread = None

    async def chat(self, user_message):
        """Send a message to the agent and get a response.

        Args:
            user_message: The message to send to the agent.

        Returns:
            The agent's response.       

        """
        logging.info(f"chat called with message: {user_message}")
        responses = []
        async for response in self.agent.invoke(messages=user_message, thread=self.thread):
            responses.append(response.content)
            self.thread = response.thread

        result = "\n".join([r.content for r in responses])
        logging.info(f"chat result: {result}")
        return str(result)


if __name__ == "__main__":
    # Load environment variables from .env file
    load_dotenv()

    # Replace with your actual API key or set the environment variable
    setlistfm_api_key = os.environ.get("SETLISTFM_API_KEY", "YOUR_API_KEY")

    # Create the agent"
    agent = SetlistFMAgent(
        setlistfm_api_key, model_name="gpt-4o", api_key_env="OPENAI_API")

    print("Welcome to the Setlist.fm Agent! Type 'exit' to quit.")

    # Simple interaction loop
    import asyncio

    async def main():
        while True:
            user_input = input("\nYou: ")
            if user_input.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break

            response = await agent.chat(user_input)
            print(f"\nAgent: {response}")

    # Run the main async loop
    asyncio.run(main())
