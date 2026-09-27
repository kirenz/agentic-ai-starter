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

Folders with a `_solution` twin are exercises: look for `# TODO`. The `_solution` folders contain a working version. `m00_first_agent` has no twin; it is complete as it is.

`uv run python -m scripts.make_exercises` regenerates the exercise folders from the solutions and overwrites any edits you made in them.

## Useful commands

```bash
uv run pytest                                  # offline tests
uv run pytest -m live                          # tests that call the Gemini API
uv run python -m helpdesk.check_models         # list Flash models, check the configured one
uv run python -m scripts.run_programmatically  # module 2: runner, sessions, events, tokens
uv run python -m ui.gradio_app                 # module 9: chat UI
```

### Module-specific commands

**Module 4, memory.** `adk web` does not write sessions to memory, so the recall of `m04_context` shows up in this demo instead:

```bash
uv run python -m scripts.memory_demo
```

**Module 6, A2A.** Start the remote billing agent in a second terminal before you open `m06_a2a_client` in `adk web`:

```bash
uv run uvicorn scripts.a2a_billing_server:a2a_app --port 8001
```

**Evaluation.** Each run calls the agent and, in addition, a judge model several times per case, so it costs noticeably more than a normal chat:

```bash
uv run pytest -m live tests/live/test_eval_live.py
uv run adk eval agents/m03_tools_solution tests/eval/nimbus_tools.test.json \
  --config_file_path tests/eval/test_config.json --print_detailed_results
```

**Module 10, LangGraph.** The same assistant built with LangChain and LangGraph:

```bash
uv run python -m langgraph_version.support_agent   # create_agent, middleware, approval
uv run python -m langgraph_version.mcp_agent       # tools from the MCP ticket server
uv run python -m langgraph_version.streaming_demo  # streaming
uv run python -m langgraph_version.support_graph   # hand-built StateGraph
uv run python -m langgraph_version.multi_agent     # supervisor with subagents
```

**Deployment.** See [docs/deploy-cloud-run.md](docs/deploy-cloud-run.md) to run an agent on Cloud Run.

## Sharing an API key

Your group shares one key. Requests are retried automatically when the limit is reached, but every call counts: test with short prompts and stop agents you do not need.

Tested with google-adk 2.10.0 and the model set in `src/helpdesk/config.py`.
