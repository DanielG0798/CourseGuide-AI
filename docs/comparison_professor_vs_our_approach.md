# Comparison: Professor's Agent Style vs. Our CourseGuide AI Skeleton

## Purpose of this document

This file compares how our professor teaches agent construction in the course examples (`chapter_02/01_first_agent.py`, `chapter_03/01_complete_agent.py`, `chapter_03/01_complete_mcp_server.py`) with the skeleton we created in this repo. The goal is to keep what the professor expects while still respecting our team's M1 model-stack decision.

---

## 1. What the professor's examples do

### Chapter 2 example
- Uses the **OpenAI Agents SDK**: `Agent`, `Runner`, `set_default_openai_client`.
- Points the SDK at the **NRP (Nautilus) OpenAI-compatible endpoint** using `AsyncOpenAI`.
- Loads API keys and base URL from a `.env` file via `python-dotenv`.
- Sets a **tracing processor** so token usage and timing print to the console.
- Defines an agent with a name, instructions, and model (`gpt-oss`).
- Runs it synchronously with `Runner.run_sync(agent, input=...)`, then prints `result.final_output`.

### Chapter 3 example
- Extends the Chapter 2 pattern to include an **MCP server**.
- The MCP server is a separate Python file launched over stdio with `MCPServerStdio`.
- The server exposes **tools** (`add`, `append`) and **resources** (`greeting://{name}`) using `FastMCP`.
- The agent instructions explicitly tell the model **when to use each tool** (e.g., "For math calculations, always use the add tool").
- The agent is declared with `mcp_servers=[mcp_server]` and run asynchronously.

---

## 2. What our skeleton currently does

- Uses a **custom wrapper** (`src/shared/model_client.py`) around `openai.OpenAI` / `AsyncOpenAI`.
- Supports **BYOM primary / NRP fallback** through environment variables.
- Loads **instructor policies** from YAML files in `config/`.
- Has a **rule-based classifier** (`classify_help_type`) instead of asking the model to pick a tool.
- Has no MCP integration yet in the M2 prototype.
- Uses synchronous calls in the CLI entry point.

---

## 3. Exact similarities

| Area | Professor's code | Our skeleton | Verdict |
|------|------------------|--------------|---------|
| `.env` for secrets | Yes (`load_dotenv`) | Yes (`python-dotenv` in `requirements.txt`, loaded in `config.py`) | Same |
| OpenAI-compatible API | Yes, via `AsyncOpenAI(base_url=..., api_key=...)` | Yes, via `OpenAI/AsyncOpenAI(base_url=..., api_key=...)` | Same underlying library |
| Agent instructions / persona | Yes, `instructions` string | Yes, `PERSONA` + policy-driven system prompt | Same concept |
| Separating agent from model client setup | Yes, `set_default_openai_client` then `Agent` | Yes, `ModelClient` config then agent code | Same separation of concerns |
| MCP as tool layer | Yes, `FastMCP` server + `MCPServerStdio` client | Empty `mcp_servers/` folder, no integration yet | Same intent but not yet implemented |
| Tracing/logging | Yes, custom `ConsoleTracingProcessor` | Not implemented yet | Needs to be added |

---

## 4. Key differences

### 4.1 Agents SDK vs. raw OpenAI client

| Professor's approach | Our current approach |
|----------------------|----------------------|
| `from agents import Agent, Runner` | `from openai import OpenAI, AsyncOpenAI` directly |
| Agent lifecycle handled by SDK | We manually build message lists and call `client.chat.completions.create` |
| `Runner.run_sync` / `Runner.run` | Custom `ask()` function in `src/m2/agent.py` |

**Why we did it this way:** Our M1 decision chose BYOM as the primary stack. Using a thin wrapper makes it easy to switch base URL, model name, and API key from a config file without depending on the exact version of the Agents SDK. It also keeps the code readable for teammates who have not used the SDK before.

**Why we should consider the professor's way:** The rubric for M2 expects "at least one MCP tool integrated." The Agents SDK has built-in MCP support (`mcp_servers=[...]`), which is exactly what the professor demonstrated. Re-implementing that ourselves is extra work and increases the chance of diverging from the course examples.

**Recommendation:** Refactor M2 to use the OpenAI Agents SDK, but keep our `ModelClient` as a configurable wrapper around the SDK's client setup. That gives us BYOM flexibility *and* MCP compatibility.

### 4.2 Model endpoint

| Professor's approach | Our current approach |
|----------------------|----------------------|
| Hard-coded to NRP (`base_url=os.getenv("NRP_BASE_URL")`, model="gpt-oss") | Configurable via env vars (`MODEL_BASE_URL`, `MODEL_NAME`, defaulting to OpenAI-compatible) |

**Defense:** Our team's M1 explicitly selected BYOM primary with NRP as fallback. A configurable endpoint is therefore correct for our project. We can set `MODEL_BASE_URL` and `MODEL_NAME` to NRP values and use the exact same runtime the professor uses.

### 4.3 Tool use / MCP integration

| Professor's approach | Our current approach |
|----------------------|----------------------|
| Tools defined in `FastMCP` server; agent instructed when to call them | Rule-based keyword classifier (`classify_help_type`) |

**Why we should change this:** The M2 rubric wants a working agent with "at least one MCP tool integrated." A keyword classifier is not an MCP tool. We should replace the classifier with an MCP tool (e.g., `classify_help_request`) or add a real tool like `lookup_course_policy`.

**Recommended refactor:** Create an MCP server in `mcp_servers/course_policy_server.py` that exposes `lookup_course_policy(course_id)` and `classify_help_type(question)`. Then wire that server into an Agents SDK agent, similar to `chapter_03/01_complete_agent.py`.

### 4.4 Sync vs. async

| Professor's approach | Our current approach |
|----------------------|----------------------|
| Async first (`async def main`, `Runner.run`) | Sync in CLI (`client.chat(...)`), async method available but unused |

**Recommendation:** Align with the professor and make the main entry point async. This matters once MCP servers are added, because `MCPServerStdio` is async-only.

### 4.5 Tracing / observability

| Professor's approach | Our current approach |
|----------------------|----------------------|
| Custom `ConsoleTracingProcessor` prints token usage per span | No tracing |

**Recommendation:** Add a simple tracing/logging helper so we can show usage during demos and in the screen recording. This is low effort and matches the course style.

---

## 5. Suggested refactor plan

To stay close to the professor's teaching while keeping our team's M1 decisions, we should:

1. **Add `openai-agents` to `requirements.txt`.**
2. **Rewrite `src/shared/model_client.py`** to return a configured `AsyncOpenAI` client and optionally set the default SDK client.
3. **Rewrite `src/m2/agent.py`** to use `Agent` + `Runner` from the Agents SDK.
4. **Create `mcp_servers/course_policy_server.py`** with at least one MCP tool (e.g., `lookup_course_policy`).
5. **Add a tracing processor** in `src/shared/tracing.py` similar to the professor's `ConsoleTracingProcessor`.
6. **Keep the policy YAML files and the configurable env vars** so BYOM primary / NRP fallback still works.

This gives us the best of both worlds: the code looks like the course examples, but the model endpoint and policies are controlled by our team's configuration.

---

## 6. What to keep unchanged

- **BYOM primary / NRP fallback decision** from M1.
- **Course policy YAML format** in `config/`.
- **Problem domain** (instructor-configurable learning agent for STEM).
- **Milestone-based folder structure** (`src/m2/`, `src/m3/`, `src/m4/`).
- **Test cases in YAML** because they are easy for non-technical teammates to read and edit.

---

## 7. Conclusion

The skeleton is structurally sound, but the M2 agent implementation should be refactored to use the OpenAI Agents SDK and MCP pattern shown by the professor. This reduces risk with the M2 rubric and makes the codebase easier to grade. The team's BYOM/NRP choice can be preserved through environment configuration, so no M1 decision needs to change.
