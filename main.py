import os
import argparse

from dotenv import load_dotenv
from google import genai
from google.genai import types
from prompts import system_prompt
from call_function import available_functions


def main() -> None:
    parser = argparse.ArgumentParser(description="AI Code Assistant")
    parser.add_argument("user_prompt", type=str, help="User prompt")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()

    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY evniornment variable not set")

    client = genai.Client(api_key=api_key)
    messages = [types.Content(role="user", parts=[types.Part(text=args.user_prompt)])]
    if args.verbose:
        print(f"User prompt: {args.user_prompt}")

    generate_content(client, messages, args.verbose)


def generate_content(client: genai.Client, messages: list[types.Content], verbose: bool) -> None:
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=messages,
        config=types.GenerateContentConfig(
            tools=[available_functions], system_instruction=system_prompt
        )
    )
    if not response.usage_metadata:
        raise RuntimeError("Gemini API response appears to be malformed")
    
    if verbose:
        print(f"Prompt tokens: {response.usage_metadata.promp_token_count}")
        print(f"Response tokens: {response.usage_metadata.candidates_token_count}")
    print(f"Response: {response.text}")

    if response.function_calls:
        for function_call in response.function_calls:
            print(f"Calling function: {function_call.name}({function_call.args})")


if __name__ == "__main__":
    main()