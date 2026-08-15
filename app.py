#!/usr/bin/env python3
"""Minimal CLI that talks to a Claude Managed Agent and streams its replies.

Usage:
    export ANTHROPIC_API_KEY=...
    python app.py "your message here"
"""

import sys

import anthropic

AGENT_ID = "agent_01MmQtpJhjZkUajdKEWtZdtj"
ENVIRONMENT_ID = "env_017EK9eJMy4LUMcPaCBvP38A"


def run(message: str) -> int:
    client = anthropic.Anthropic()

    try:
        session = client.beta.sessions.create(
            agent=AGENT_ID,
            environment_id=ENVIRONMENT_ID,
        )
    except (anthropic.APIStatusError, anthropic.APIConnectionError) as e:
        print(f"Failed to create session: {e}", file=sys.stderr)
        return 1
    except TypeError as e:
        # The SDK raises a bare TypeError (not an APIError subclass) when no
        # credentials can be resolved (no API key, auth token, or profile).
        print(f"Failed to create session: {e}", file=sys.stderr)
        return 1

    print(f"Session: {session.id}", file=sys.stderr)

    try:
        # Stream-first: open the stream before sending, so no early events are missed.
        with client.beta.sessions.events.stream(session_id=session.id) as stream:
            client.beta.sessions.events.send(
                session_id=session.id,
                events=[
                    {
                        "type": "user.message",
                        "content": [{"type": "text", "text": message}],
                    }
                ],
            )

            for event in stream:
                if event.type == "agent.message":
                    for block in event.content:
                        if block.type == "text":
                            print(block.text, end="", flush=True)
                elif event.type == "session.status_idle":
                    # requires_action means the agent is waiting on us (tool
                    # confirmation / custom tool result) - not done yet.
                    if event.stop_reason.type != "requires_action":
                        print()
                        break
                elif event.type == "session.status_terminated":
                    print("\n[session terminated]", file=sys.stderr)
                    break
                elif event.type == "session.error":
                    print(f"\n[session error] {event.error.message}", file=sys.stderr)
                    return 1
    except (anthropic.APIStatusError, anthropic.APIConnectionError) as e:
        print(f"API error: {e}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nInterrupted.", file=sys.stderr)
        return 130

    return 0


if __name__ == "__main__":
    message = " ".join(sys.argv[1:]) or "Hello!"
    sys.exit(run(message))
