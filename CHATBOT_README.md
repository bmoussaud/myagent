# Setlistfm Chatbot with Gradio

This repository contains a chatbot interface built with Gradio that allows you to interact with a Setlist.fm agent. The agent can help you find information about artists, concerts, and setlists.

## Features

- 🎸 Search for artists and their information
- 🎵 Find setlists from past concerts
- 🏟️ Get venue information
- 🌍 Search by artist, city, or country

## Requirements

The chatbot requires the following libraries:

- gradio
- semantic-kernel
- fastapi
- python-dotenv
- uvicorn
- pydantic
- requests
- azure-monitor-opentelemetry (optional for telemetry)
- azure-ai-inference (optional for telemetry)
- azure-ai-projects (optional for telemetry)

## Setup

1. Clone the repository
2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file based on the `.env.sample` template:
   ```
   cp .env.sample .env
   ```
4. Edit the `.env` file and add your API keys:
   ```
   SETLISTFM_API_KEY=your_setlistfm_api_key
   OPENAI_API=your_openai_api_key
   ```

## Running the Chatbot

To run the chatbot, execute:

```bash
python gradio_chatbot.py
```

The chatbot will be accessible at `http://localhost:7860` in your web browser.

## Example Queries

Here are some example queries you can try:

- "Find setlists for Radiohead in London"
- "What songs did Metallica play at their last concert?"
- "Tell me about the artist Adele"
- "Find concerts in New York"
- "What venues has Ed Sheeran played at?"
- "Compare the setlists of two recent Taylor Swift concerts"

## Customization

The chatbot can be customized in the following ways:

- Change the OpenAI model used (gpt-3.5-turbo, gpt-4o, etc.)
- Modify the appearance through Gradio theme settings
- Add more example queries

## Architecture

The chatbot is built with the following components:

- Gradio: Provides the web UI
- Semantic Kernel: Powers the agent's reasoning capabilities
- Setlist.fm API: Provides data about artists, concerts, and setlists

## License

This project is licensed under the MIT License - see the LICENSE file for details.
