# DeepAgents API Reference

Complete reference for LangChain's DeepAgents framework functions, classes, and configurations.

## Core Functions

### create_deep_agent

Create a synchronous deep agent with built-in middleware.

```python
from deepagents import create_deep_agent

agent = create_deep_agent(
    tools: list[Callable] = None,
    system_prompt: str = None,
    subagents: list[dict | CustomSubAgent] = None,
    model: str | LanguageModelLike = "claude-sonnet-4-20250514",
    interrupt_on: dict[str, dict | bool] = None,
    middleware: list[AgentMiddleware] = None,
)
```

**Parameters:**
- `tools` (list): List of functions or @tool decorated callables. These tools are available to both main agent and sub-agents (unless sub-agent specifies custom tools).
- `system_prompt` (str): Custom instructions prepended to base system prompt. Define agent's role, workflows, and expectations.
- `subagents` (list): List of sub-agent configurations. Each can be a SubAgent dict or CustomSubAgent dict.
- `model` (str | LanguageModelLike): Model to use. String format "provider:model" or LangChain model object. Default: "claude-sonnet-4-20250514".
- `interrupt_on` (dict): Human-in-the-loop configuration. Maps tool names to approval configs.
- `middleware` (list): Additional custom middleware to append to default stack.

**Returns:**
- `CompiledStateGraph`: LangGraph agent that can be invoked, streamed, or used with LangGraph features.

**Example:**
```python
agent = create_deep_agent(
    tools=[search_tool, calculator],
    system_prompt="You are a research assistant...",
    model="openai:gpt-4o"
)
```

### async_create_deep_agent

Create an asynchronous deep agent. Same parameters as `create_deep_agent`.

```python
from deepagents import async_create_deep_agent

agent = async_create_deep_agent(
    tools=[async_search],
    system_prompt="...",
)

# Use with async operations
async for chunk in agent.astream(...):
    process(chunk)
```

**When to use:**
- Working with async tools (e.g., MCP tools)
- Need non-blocking I/O operations
- Integrating with async frameworks

## Sub-Agent Configuration

### SubAgent Dictionary

Standard sub-agent configuration.

```python
subagent = {
    "name": str,                    # Required: Sub-agent identifier
    "description": str,             # Required: When to use this sub-agent
    "system_prompt": str,           # Required: Sub-agent instructions
    "tools": list[Callable],        # Optional: Specific tools (default: inherit all)
    "model": str | LanguageModelLike | dict,  # Optional: Model override
    "middleware": list[AgentMiddleware],      # Optional: Additional middleware
}
```

**Field Details:**

**name** (str, required):
- Identifier used by main agent to call sub-agent
- Must be unique among all sub-agents
- Use descriptive names like "research-agent", "data-analyzer"

**description** (str, required):
- Shown to main agent to decide when to delegate
- Should clearly state the sub-agent's expertise and use cases
- Example: "Expert at conducting deep research on specific topics with proper citations"

**system_prompt** (str, required):
- Instructions specific to this sub-agent
- Should be focused and specialized
- Include output format expectations

**tools** (list, optional):
- Subset of main agent tools or additional specialized tools
- Default: All tools from main agent
- Use to restrict or expand tool access

**model** (str | dict, optional):
- Override main agent's model
- String: "provider:model"
- Dict: {"model": "...", "temperature": 0, "max_tokens": 8192}
- Use faster models for simple sub-agents

**middleware** (list, optional):
- Additional middleware beyond defaults
- Used for sub-agent-specific state or tools
- Does NOT include SubAgentMiddleware (prevents recursion)

**Example:**
```python
research_subagent = {
    "name": "deep-researcher",
    "description": "Conducts comprehensive research using multiple sources",
    "system_prompt": """You are a research specialist.
    Conduct thorough research and provide cited answers.
    Format: [1], [2] for citations, ### Sources section at end.""",
    "tools": [internet_search, academic_db_search],
    "model": "openai:gpt-4o",
}
```

### CustomSubAgent Dictionary

Use a pre-built LangGraph agent as sub-agent.

```python
from langchain.agents import create_agent

# Build custom agent
custom_agent = create_agent(
    model="...",
    tools=[...],
    system_prompt="..."
)

# Use as sub-agent
custom_subagent = {
    "name": str,           # Required: Identifier
    "description": str,    # Required: When to use
    "graph": Runnable,     # Required: Pre-built agent/graph
}
```

**When to use CustomSubAgent:**
- Need complex agent logic not achievable with simple prompts
- Want to reuse existing agent implementation
- Require special state management or workflow

## Built-in Tools

### Planning Tool: write_todos

Provided by TodoListMiddleware. Helps structure complex tasks.

```python
# Agent calls this internally
write_todos(todos: list[dict])
```

**Todo Structure:**
```python
{
    "description": "Task description",
    "status": "pending" | "in_progress" | "completed"
}
```

**Usage Pattern:**
```python
# Agent thinking:
# "Let me structure this complex research task..."
write_todos([
    {"description": "Research background on topic", "status": "pending"},
    {"description": "Gather recent developments", "status": "pending"},
    {"description": "Synthesize findings", "status": "pending"},
    {"description": "Write report", "status": "pending"}
])
```

### Filesystem Tools

Provided by FilesystemMiddleware. Manage files in virtual filesystem.

#### write_file

Create or overwrite a file.

```python
write_file(path: str, content: str) -> str
```

**Parameters:**
- `path`: File path (single-level, no subdirectories)
- `content`: File contents as string

**Returns:** Confirmation message

**Usage:**
```python
# Save research findings
write_file("findings.txt", "Key points:\n1. ...\n2. ...")

# Persist across sessions (with long_term_memory=True)
write_file("/memories/project_notes.md", "Project context...")
```

#### read_file

Read file contents.

```python
read_file(path: str) -> str
```

**Parameters:**
- `path`: File path to read

**Returns:** File contents as string

**Raises:** Error if file doesn't exist

#### edit_file

Modify existing file using search/replace.

```python
edit_file(path: str, old_content: str, new_content: str) -> str
```

**Parameters:**
- `path`: File to edit
- `old_content`: Text to find and replace
- `new_content`: Replacement text

**Returns:** Confirmation message

**Note:** `old_content` must match exactly and appear once in file.

#### ls

List files in filesystem.

```python
ls(path: str = "/") -> list[str]
```

**Parameters:**
- `path`: Directory to list (currently only "/" supported)

**Returns:** List of filenames

### Sub-Agent Delegation: task

Provided by SubAgentMiddleware. Delegate to sub-agents.

```python
task(subagent: str, message: str) -> str
```

**Parameters:**
- `subagent`: Name of sub-agent to invoke ("general-purpose" always available)
- `message`: Instructions and context for sub-agent

**Returns:** Sub-agent's final response

**Best Practices:**
- Give clear, specific instructions
- Include necessary context
- Sub-agent returns only final answer (no back-and-forth)
- Use for context isolation

**Example:**
```python
# Main agent delegates research
task(
    subagent="research-agent",
    message="Research the latest developments in quantum computing. "
            "Focus on practical applications. Provide citations."
)
```

## Middleware Classes

### TodoListMiddleware

Adds planning capability with write_todos tool.

```python
from langchain.agents.middleware import TodoListMiddleware

middleware = TodoListMiddleware(
    system_prompt: str = None,  # Optional: Additional prompt about TODO usage
)
```

**State Schema:**
```python
{
    "todos": list[dict]  # List of TODO items with description and status
}
```

### FilesystemMiddleware

Adds file operations and context management.

```python
from deepagents.middleware import FilesystemMiddleware

middleware = FilesystemMiddleware(
    backend: BACKEND_TYPES = None,           # Memory backend (default: StateBackend)
    system_prompt: str = None,               # Optional: Additional prompt
    custom_tool_descriptions: dict = None,   # Override tool descriptions
    tool_token_limit_before_evict: int = 20000,  # Token limit for auto-eviction
)
```

**Parameters:**
- `backend`: Memory backend (StateBackend, StoreBackend, or CompositeBackend)
- `system_prompt`: Additional filesystem usage instructions
- `custom_tool_descriptions`: Custom descriptions for fs tools
- `tool_token_limit_before_evict`: Auto-save large tool results to file

**State Schema:**
```python
{
    "files": dict[str, str]  # Filename -> content mapping
}
```

**Memory Backends:**

**StateBackend** (default): Ephemeral, stored in graph state
```python
from deepagents.memory.backends import StateBackend
backend = StateBackend()
```

**StoreBackend**: Persistent, requires Store
```python
from deepagents.memory.backends import StoreBackend
from langgraph.store.memory import InMemoryStore

store = InMemoryStore()
backend = StoreBackend()
# Pass store to agent runtime
```

**CompositeBackend**: Hybrid (ephemeral + persistent)
```python
from deepagents.memory.backends import CompositeBackend, StateBackend, StoreBackend

backend = CompositeBackend(
    default=StateBackend(),
    routes={"/memories/": StoreBackend()}
)
```

### SubAgentMiddleware

Enables hierarchical agent delegation.

```python
from deepagents.middleware.subagents import SubAgentMiddleware

middleware = SubAgentMiddleware(
    default_model: str | LanguageModelLike,  # Model for sub-agents
    default_tools: list[Callable],           # Tools inherited by sub-agents
    subagents: list[dict],                   # Sub-agent configurations
)
```

**Features:**
- Automatic "general-purpose" sub-agent (same as main agent)
- Context isolation per delegation
- Sub-agents don't have SubAgentMiddleware (no recursion)

## Human-in-the-Loop Configuration

### HumanInTheLoopConfig

Configure tool approval requirements.

```python
interrupt_on = {
    "tool_name": {
        "allowed_decisions": ["approve", "edit", "reject"]
    }
}
```

**Allowed Decisions:**
- `"approve"`: Allow human to accept tool call as-is
- `"edit"`: Allow human to modify tool call args
- `"reject"`: Allow human to provide feedback without calling tool

**Shortcut:**
```python
interrupt_on = {
    "dangerous_tool": True  # Enables all three decisions
}
```

### Approval Commands

#### Accept Tool Call

```python
from langgraph.types import Command

Command(resume=[{"type": "accept"}])
```

#### Edit Tool Call

```python
Command(resume=[{
    "type": "edit",
    "args": {
        "action": "tool_name",
        "args": {"param1": "value1", ...}
    }
}])
```

#### Reject with Feedback

```python
Command(resume=[{
    "type": "response",
    "args": "Feedback string explaining why rejected"
}])
```

## Agent State Schema

Combined state from all middleware:

```python
{
    "messages": list[BaseMessage],     # Conversation history
    "todos": list[dict],               # Planning tasks
    "files": dict[str, str],           # Virtual filesystem
    # Custom fields from user middleware
}
```

## Model Configuration

### String Format

```python
"provider:model-name"
```

Examples:
- `"anthropic:claude-sonnet-4-20250514"`
- `"openai:gpt-4o"`
- `"openai:gpt-4o-mini"`
- `"ollama:llama3"`

### LangChain Model Object

```python
from langchain.chat_models import init_chat_model

model = init_chat_model(
    "openai:gpt-4o",
    temperature=0.7,
    max_tokens=4096
)

agent = create_deep_agent(model=model, ...)
```

### Per-SubAgent Model Dict

```python
subagent = {
    "name": "fast-agent",
    "description": "...",
    "system_prompt": "...",
    "model": {
        "model": "anthropic:claude-3-5-haiku-20241022",
        "temperature": 0,
        "max_tokens": 8192
    }
}
```

## Invocation Patterns

### Basic Invocation

```python
result = agent.invoke({
    "messages": [{"role": "user", "content": "query"}]
})

final_message = result["messages"][-1]
```

### Streaming

```python
for chunk in agent.stream(
    {"messages": [{"role": "user", "content": "query"}]},
    stream_mode="values"
):
    if "messages" in chunk:
        chunk["messages"][-1].pretty_print()
```

### With Files

```python
result = agent.invoke({
    "messages": [...],
    "files": {
        "context.txt": "Initial context",
        "data.csv": "data,data\n1,2\n"
    }
})

output_files = result["files"]
```

### With Checkpointing (Memory)

```python
from langgraph.checkpoint.memory import InMemorySaver

agent.checkpointer = InMemorySaver()

config = {"configurable": {"thread_id": "user-123"}}

# First conversation
agent.invoke({...}, config=config)

# Later conversation (same thread)
agent.invoke({...}, config=config)  # Has memory
```

## Environment Variables

### LangSmith Tracing

```bash
export LANGSMITH_TRACING=true
export LANGSMITH_PROJECT=my-project
export LANGSMITH_API_KEY=your-key
```

### Model API Keys

```bash
export ANTHROPIC_API_KEY=your-key
export OPENAI_API_KEY=your-key
export TAVILY_API_KEY=your-key  # For search examples
```

## Common Patterns

### Multi-Stage Research

```python
stage1 = task("research-agent", "Research background on X")
stage2 = task("research-agent", f"Building on: {stage1}, research Y")
stage3 = task("critique-agent", f"Review this report: {stage2}")
```

### Iterative Refinement

```python
draft = "Initial content..."
write_file("draft.md", draft)

feedback = task("critique-agent", f"Review: {draft}")

# Read and edit based on feedback
content = read_file("draft.md")
edit_file("draft.md", "old text", "improved text")
```

### Parallel Research

```python
# Main agent can invoke multiple sub-agents
# Each gets isolated context
results = []
for topic in topics:
    result = task("research-agent", f"Research {topic}")
    results.append(result)

# Synthesize
write_file("synthesis.md", combine(results))
```
