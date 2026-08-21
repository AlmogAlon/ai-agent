# simple-ai-agent

A minimal tool-calling AI agent: FastAPI + the OpenAI Responses API + Redis for per-session conversation history. It includes a calculator exposed through native function calling and a small tool registry so more tools can be added without restructuring the agent loop.

## Run

```bash
cp .env.example .env
# Replace the placeholder in .env with your OpenAI API key.
docker compose up --build
```

The default model is `gpt-5-mini`. Override it with `OPENAI_MODEL` in `.env`.

## Use

Start a conversation (omit `session_id` on the first call):

```bash
curl -X POST localhost:8001/chat \
  -H 'content-type: application/json' \
  -d '{"message": "Hello, who are you?"}'
```

The response includes a `session_id` — pass it back on subsequent calls to continue the same conversation:

```bash
curl -X POST localhost:8001/chat \
  -H 'content-type: application/json' \
  -d '{"session_id": "<id-from-previous-response>", "message": "What did I just ask you?"}'
```

Inspect stored history:

```bash
curl localhost:8001/history/<session_id>
```

## Observe agent actions

Agent runs are logged to the application output. With Docker Compose, follow them with:

```bash
docker compose logs -f agent
```

Each run logs model iterations, native tool calls and their results. Tool arguments and
results are truncated to 500 characters, but may still contain user data, so treat these
development logs as sensitive.

## Notes

- Requests use the OpenAI API and therefore require API access and may incur usage charges.
- Redis has no persistent volume by default, so conversation history is lost on `docker compose down`. Add a volume to the `redis` service in `docker-compose.yml` if you want it to survive restarts.
- Add tools by registering them in `app/tools.py`; the native tool-calling loop in `app/agent.py` already knows how to call them.
