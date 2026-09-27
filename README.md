# Nimbus Support Assistant: agentic AI starter

Hands-on code for building AI agents with Google ADK and LangGraph. You build one support assistant for the fictional **Nimbus Home Hub** step by step.

## Setup

1. Install [uv](https://docs.astral.sh/uv/) and VS Code.
2. Clone this repository and install everything:

   ```bash
   uv sync
   ```

3. Copy `.env.example` to `.env` and paste the API key you received for your group.
4. Start the development UI and pick an agent in the browser:

   ```bash
   uv run adk web agents
   ```

ADK prints a few `[EXPERIMENTAL]` warnings on startup. They are expected and can be ignored.

## Structure

| Folder | Module |
|---|---|
| `agents/m00_first_agent` | Your first agent |
| `agents/m02_core*` | Runner, sessions, state, events |
| `agents/m03_tools*`, `agents/m03_mcp*` | Function tools, agents as tools, MCP |
| `agents/m04_context*` | Memory, compaction, just-in-time retrieval |
| `agents/m05_workflow*` | Graph workflows, routing, human approval |
| `agents/m06_multiagent*`, `agents/m06_a2a_client*` | Multi-agent systems and A2A |
| `agents/m07_guardrails*` | Plugins, callbacks, confirmations |
| `tests/eval` | Evaluation sets |
| `ui/` | Chat UI with Gradio |
| `langgraph_version/` | The same assistant in LangChain/LangGraph: tools, MCP, middleware, memory, graph, multi-agent, streaming |

Folders without `_solution` are exercises: look for `# TODO`. The `_solution` folders contain a working version.

`uv run python -m scripts.make_exercises` regenerates the exercise folders from the solutions and overwrites any edits you made in them.

## Useful commands

```bash
uv run pytest                    # offline tests
uv run pytest -m live            # tests that call the Gemini API
uv run python -m scripts.run_programmatically
uv run python -m ui.gradio_app
```

## Sharing an API key

Your group shares one key. Requests are retried automatically when the limit is reached, but every call counts: test with short prompts and stop agents you do not need.

Tested with google-adk 2.10.0 and the model set in `src/helpdesk/config.py`.
