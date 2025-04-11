"""
This module provides functionality for interacting with the OpenAI API to generate responses.
It handles environment variable loading and provides a simple interface for making API calls
to generate text responses based on user prompts.
"""

import json
import os

import requests
from colorama import Fore, init
from dotenv import load_dotenv
from openai import OpenAI

# Initialize colorama
init()

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_weather(latitude, longitude):
    response = requests.get(
        f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,wind_speed_10m&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m"
    )
    data = response.json()
    return data["current"]["temperature_2m"]


def get_time(time_zone):
    """
    Get the current time in the specified timezone.

    Args:
        time_zone (str): The timezone name (e.g., 'America/New_York', 'Europe/London')

    Returns:
        str: Formatted current time in the specified timezone
    """
    try:
        from datetime import datetime

        import pytz

        # Get timezone object
        tz = pytz.timezone(time_zone)
        # Get current time in specified timezone
        current_time = datetime.now(tz)
        # Format time as string
        return current_time.strftime("%Y-%m-%d %H:%M:%S %Z")
    except pytz.exceptions.UnknownTimeZoneError:
        return (
            f"Error: Unknown timezone '{time_zone}'. Please use a valid timezone name."
        )

def run_command_in_bash(command):
    """
    Run a command in Bash and return the output.

    Args:
        command (str): The command to execute in Bash.

    Returns:
        str: The output of the command.
    """
    import subprocess

    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"Error executing command: {e.stderr.strip()}"


def generate_response(messages):
    """
    Generate a response using OpenAI's API.
    """
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        tools=[
            {
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "description": "Get the current weather for a location",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "latitude": {"type": "number"},
                            "longitude": {"type": "number"},
                        },
                        "required": ["latitude", "longitude"],
                    },
                },
                "strict": True,
            },
            {
                "type": "function",
                "function": {
                    "name": "run_command_in_bash",
                    "description": "Run a command in Bash",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "command": {"type": "string"},
                        },
                        "required": ["latitude", "longitude"],
                    },
                },
                "strict": True,
            },
            {
                "type": "function",
                "function": {
                    "name": "get_time",
                    "description": "Get the current time for a timezone (e.g., 'America/New_York', 'Europe/London')",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "time_zone": {"type": "string"},
                        },
                        "required": ["time_zone"],
                    },
                },
                "strict": True,
            },
        ],
    )
    return response.choices[0].message


# Example usage
if __name__ == "__main__":
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
    ]
    while True:
        try:
            print(
                f"{Fore.BLUE}Enter a prompt for the AI (or 'quit' to exit): {Fore.RESET}"
            )
            user_prompt = input()
            if user_prompt.lower() == "quit":
                break

            messages.append({"role": "user", "content": user_prompt})
            max_iterations = 5  # Prevent infinite loops
            iteration = 0

            while iteration < max_iterations:
                iteration += 1
                try:
                    completion = generate_response(messages)
                    if completion.content:
                        print(f"{Fore.CYAN}Assistant:{Fore.RESET} {completion.content}")
                        messages.append(
                            {"role": "assistant", "content": completion.content}
                        )

                    if completion.tool_calls:
                        messages.append(completion)
                        for tool_call in completion.tool_calls:
                            try:
                                print(
                                    f"{Fore.GREEN}Tool Request:{Fore.RESET} {tool_call.function}"
                                )
                                args = json.loads(tool_call.function.arguments)
                                function_name = tool_call.function.name
                                if function_name == "get_weather":
                                    result = get_weather(args["latitude"], args["longitude"])
                                elif function_name == "get_time":
                                    result = get_time(args["time_zone"])
                                elif function_name == "run_command_in_bash":
                                    result = run_command_in_bash(args["command"])
                                else:
                                    raise ValueError(f"Unknown function: {function_name}")
                                
                                print(f"{Fore.MAGENTA}{function_name}{Fore.RESET}: {result}")
                                messages.append({
                                    "role": "tool",
                                    "tool_call_id": tool_call.id,
                                    "content": str(result),
                                })
                            except json.JSONDecodeError as e:
                                print(
                                    f"{Fore.RED}Error parsing tool arguments:{Fore.RESET} {e}"
                                )
                            except KeyError as e:
                                print(
                                    f"{Fore.RED}Missing required argument:{Fore.RESET} {e}"
                                )
                            except Exception as e:
                                print(
                                    f"{Fore.RED}Error executing tool call:{Fore.RESET} {e}"
                                )
                    else:
                        break  # No more tool calls, exit the inner loop

                except Exception as e:
                    print(f"{Fore.RED}Error in completion:{Fore.RESET} {e}")
                    break

            if iteration == max_iterations:
                print(
                    f"{Fore.RED}\nReached maximum number of iterations. Starting fresh.{Fore.RESET}"
                )

        except KeyboardInterrupt:
            print(f"{Fore.RED}\nExiting...{Fore.RESET}")
            break
        except Exception as e:
            print(f"{Fore.RED}\nAn error occurred:{Fore.RESET} {e}")
