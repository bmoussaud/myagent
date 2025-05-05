# Setlist.fm Agent with Semantic Kernel

This project demonstrates a simple agent using Semantic Kernel that leverages the setlist.fm API to retrieve information about music artists and their live performances.

## Components

1. `setlist_client.py` - A Python client for accessing the setlist.fm API
2. `setlist_agent.py` - A Semantic Kernel agent that uses the setlist.fm client as a plugin
3. `test_setlist_client.py` - A simple test program for the setlist.fm client

## Prerequisites

- Python 3.8+
- Valid setlist.fm API key (sign up at https://www.setlist.fm/settings/api)
- OpenAI API key for the language model

## Setup

1. Install the required dependencies:
```bash
pip install semantic-kernel requests
```

2. Set your API keys as environment variables:
```bash
export SETLISTFM_API_KEY="your_setlistfm_api_key"
export OPENAI_API_KEY="your_openai_api_key"
```

## Usage

### Basic Chat Agent

```bash
python setlist_agent.py
```

### Sequential Planner Agent

```bash
python setlist_agent_planner.py
```

### Stepwise Planner Agent (recommended)

```bash
python setlist_agent_stepwise.py
```

You can then interact with the agent by asking questions about artists, concerts, setlists, and venues. For example:

- "Find concerts by Muse"
- "What songs did Muse play at their last concert?"
- "Show me information about Wembley Stadium"
- "Find setlists from concerts in London"

## Features

The agent provides access to the following setlist.fm functions:

- Search for artists by name
- Search for setlists by artist name, city name, or country code
- Get specific setlist details by ID
- Get venue information by ID

## Plugin Structure

The SetlistFMPlugin class exposes various functions from the setlist.fm client as semantic functions that can be used by the Semantic Kernel framework. Each function is annotated with `@kernel_function` to make it available to the kernel.

## How It Works

1. The agent initializes the Semantic Kernel and adds an OpenAI chat completion service
2. It imports the SetlistFMPlugin with functions that wrap the setlist.fm API client 
3. When a user sends a message, the agent processes it and decides which functions to call
4. Results from the API are formatted and presented to the user

## Planner Options

The repository includes three different implementation approaches:

1. **Basic Agent** (`setlist_agent.py`): Uses a simple chat model to respond to queries
2. **Sequential Planner** (`setlist_agent_planner.py`): Creates a structured plan and executes functions in sequence
3. **Stepwise Planner** (`setlist_agent_stepwise.py`): Uses a more sophisticated approach that can handle complex tasks in multiple steps with reasoning
