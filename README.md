# Managed Agent CLI

Minimal Python app that opens a Claude Managed Agents session, streams the
agent's replies, and exits cleanly on completion or error.

## Setup

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=your-api-key
```

## Run

```bash
python app.py "your message here"
```

The app talks to agent `agent_01MmQtpJhjZkUajdKEWtZdtj` in environment
`env_017EK9eJMy4LUMcPaCBvP38A`. It:

1. Creates a session with `client.beta.sessions.create`.
2. Opens the event stream with `client.beta.sessions.events.stream` before
   sending anything, so no early events are missed.
3. Sends a `user.message` event via `client.beta.sessions.events.send`.
4. Prints `agent.message` text as it streams in.
5. Stops on `session.status_idle` (once the agent isn't waiting on further
   input) or `session.status_terminated`.
6. Exits with a non-zero status and a message on stderr for API/connection
   errors or a `session.error` event.
