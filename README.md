# AI Tooling in Python

A Python toolkit for AI-powered applications using OpenAI's API.

## Setup

1. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On macOS/Linux
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure OpenAI API key in `.env`:
```env
OPENAI_API_KEY=your_api_key_here
```

## Usage

This tool is designed to be used from the command line:

```bash
python agent.py
```

This will start an interactive session where you can:

1. Enter prompts for the AI assistant
2. The assistant can call various tools including:
   - Getting weather information
   - Running bash commands
   - Getting current time in different timezones
3. Type 'quit' to exit the session

Example interaction:

```
Enter a prompt for the AI (or 'quit' to exit): 
What's the temperature in New York?

Tool Request: get_weather
get_weather: 22.4

Assistant: The current temperature in New York is 22.4°C.
```

## License

Apache License 2.0
