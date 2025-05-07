import os
import asyncio
import gradio as gr
from dotenv import load_dotenv
from setlist_agent import SetlistFMAgent

# Load environment variables
load_dotenv()

# Get API keys from environment variables
setlistfm_api_key = os.environ.get("SETLISTFM_API_KEY")
if not setlistfm_api_key:
    raise ValueError("Please set the SETLISTFM_API_KEY environment variable")

openai_api_key = os.environ.get("OPENAI_API")
if not openai_api_key:
    raise ValueError("Please set the OPENAI_API environment variable")

# Initialize the SetlistFM agent
agent = SetlistFMAgent(
    setlistfm_api_key, model_name="gpt-4o", api_key_env="OPENAI_API")

# Store conversation history
conversation_history = []


async def process_message(message, history):
    """Process user message and get response from agent"""
    try:
        # Get response from agent
        response = await agent.chat(message)
        return response
    except Exception as e:
        return f"Error processing your request: {str(e)}"

# Create a simple Gradio chat interface
demo = gr.ChatInterface(
    fn=process_message,
    title="Setlist Music Assistant",
    description="Ask questions about artists, concerts, and setlists.",
    examples=[
        "Find setlists for Muse in London",
        "What songs did Metallica play at their last concert?",
        "Tell me about the artist Adele",
        "Find concerts in New York"
    ],
    theme=gr.themes.Default()
)

if __name__ == "__main__":
    # Launch the app
    print("Starting Setlistfm Music Assistant")
    # Set share=False in production
    demo.launch(share=True, server_name="0.0.0.0")
