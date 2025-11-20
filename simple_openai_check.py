#!/usr/bin/env python3
"""
Minimal OpenAI client that verifies Together API key usability by sending
a real LLM chat completion.

Environment variables:
  OPENAI_API_KEY   - required
  OPENAI_BASE_URL  - required (e.g. https://api.together.xyz/v1)
  OPENAI_MODEL     - required (e.g. meta-llama/Llama-3.1-8B-Instruct-Turbo)
"""

import os
import sys
from openai import OpenAI
from openai import OpenAIError


def main():
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL")
    model = os.getenv("OPENAI_MODEL")

    if not api_key:
        print("ERROR: OPENAI_API_KEY not set", file=sys.stderr)
        sys.exit(1)
    if not base_url:
        print("ERROR: OPENAI_BASE_URL not set", file=sys.stderr)
        sys.exit(1)
    if not model:
        print("ERROR: OPENAI_MODEL not set", file=sys.stderr)
        sys.exit(1)

    client = OpenAI(api_key=api_key, base_url=base_url)

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=4,
        )

        if response and response.choices:
            print("OK")
            sys.exit(0)

        print("ERROR: Empty response", file=sys.stderr)
        sys.exit(1)

    except OpenAIError as e:
        print(f"ERROR: OpenAI error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
