import os
import asyncio
import gradio as gr
from dotenv import load_dotenv
from setlist_agent import SetlistFMAgent
from config import enable_telemetry, get_logger

# Configure logging
logger = get_logger(__name__)

# Load environment variables
load_dotenv()

# Enable telemetry if needed
enable_telemetry()

# Get API keys from environment variables
setlistfm_api_key = os.environ.get("SETLISTFM_API_KEY")
if not setlistfm_api_key:
    raise ValueError("Please set the SETLISTFM_API_KEY environment variable")

openai_api_key = os.environ.get("OPENAI_API")
if not openai_api_key:
    raise ValueError("Please set the OPENAI_API environment variable")

# Initialize the SetlistFM agent with configurable model
DEFAULT_MODEL = "gpt-4o"  # Default model


def create_agent(model_name=DEFAULT_MODEL):
    """Create a new instance of the SetlistFM agent with specified model"""
    logger.info(f"Creating new agent with model: {model_name}")
    return SetlistFMAgent(setlistfm_api_key, model_name=model_name, api_key_env="OPENAI_API")


# Initialize the agent with the default model
agent = create_agent(DEFAULT_MODEL)

# Store conversation history
conversation_history = []


async def process_message(message, history):
    """Process user message and get response from agent"""
    # Update history with user message
    history.append({"role": "user", "content": message})

    # Log the incoming message
    logger.info(f"Received message: {message}")

    try:
        # Get response from agent
        response = await agent.chat(message)

        # Update history with assistant's response
        conversation_history.append({"role": "assistant", "content": response})

        return response
    except Exception as e:
        error_message = f"Error processing your request: {str(e)}"
        logger.error(f"Error in process_message: {e}")
        return error_message


def clear_conversation():
    """Clear the conversation history"""
    conversation_history.clear()
    return None


async def change_model(model_name):
    """Change the model used by the agent"""
    global agent
    agent = create_agent(model_name)
    return f"Model changed to {model_name}"


def create_demo():
    """Create the Gradio Blocks interface"""
    with gr.Blocks(title="Setlistfm Music Assistant", theme=gr.themes.Soft()) as demo:
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("# 🎸 Setlistfm Music Assistant")
                gr.Markdown("""
                This assistant can help you find information about:
                - Artists and their details
                - Concert setlists from past shows
                - Venue information
                """)

                """ with gr.Accordion("Settings", open=False):
                    model_dropdown = gr.Dropdown(
                        ["gpt-3.5-turbo", "gpt-4o", "gpt-4-turbo"],
                        label="Select Model",
                        value=DEFAULT_MODEL,
                        interactive=True
                    )
                    model_status = gr.Textbox(
                        label="Model Status", value=f"Using {DEFAULT_MODEL}", interactive=False)
                    model_btn = gr.Button("Change Model")
                    model_btn.click(
                        fn=lambda m: asyncio.run(change_model(m)),
                        inputs=model_dropdown,
                        outputs=model_status
                    ) """

                with gr.Row():
                    clear_btn = gr.Button("Clear Chat History")
                    clear_btn.click(fn=clear_conversation, outputs=[])

        with gr.Row():
            with gr.Column(scale=3):
                chatbot = gr.Chatbot(
                    height=500,
                    show_label=False,
                    avatar_images=("👤", "🎸"),
                    bubble_full_width=False,
                )

                with gr.Row():
                    msg = gr.Textbox(
                        placeholder="Ask about artists, concerts, or setlists...",
                        container=False,
                        scale=7,
                    )
                    submit_btn = gr.Button("Send", variant="primary", scale=1)

                with gr.Row():
                    gr.Examples(
                        examples=[
                            "Find setlists for Radiohead in London",
                            "What songs did Metallica play at their last concert?",
                            "Tell me about the artist Adele",
                            "Find concerts in New York",
                            "What venues has Ed Sheeran played at?",
                            "Compare the setlists of two recent Taylor Swift concerts"
                        ],
                        inputs=msg,
                        label="Example Queries"
                    )

        # Set up event handlers
        msg.submit(
            fn=process_message,
            inputs=[msg, chatbot],
            outputs=[chatbot],
            show_progress=True
        ).then(
            fn=lambda: "",
            outputs=[msg]
        )

        submit_btn.click(
            fn=process_message,
            inputs=[msg, chatbot],
            outputs=[chatbot],
            show_progress=True
        ).then(
            fn=lambda: "",
            outputs=[msg]
        )

    return demo

# Function to fetch recent setlists


async def fetch_trending_artists():
    """Fetch trending artists info to display on sidebar"""
    try:
        # This is just a placeholder - in a real implementation,
        # you might want to query for actual trending artists
        trending_artists = [
            "Taylor Swift",
            "Coldplay",
            "The Weeknd",
            "Billie Eilish",
            "Bad Bunny"
        ]

        results = []
        # Limit to top 3 to avoid rate limits
        for artist in trending_artists[:3]:
            response = await agent.chat(f"Give me a one sentence summary about {artist} without mentioning setlists")
            results.append(f"**{artist}**: {response}")

        return "\n\n".join(results)
    except Exception as e:
        logger.error(f"Error fetching trending artists: {e}")
        return "Unable to load trending artists information."

if __name__ == "__main__":
    demo = create_demo()

    # Print startup message
    print("="*50)
    print("Starting Setlistfm Music Assistant")
    print("Open the URL below in your browser")
    print("="*50)

    # Launch the app
    # Set share=False in production
    demo.launch(share=True, server_name="0.0.0.0", server_port=7860)
