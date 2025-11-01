---
name: deepagent
description: Comprehensive guide for building sophisticated AI agents using LangChain's DeepAgents framework. Use when building autonomous agents that handle complex, multi-step tasks requiring planning, file management, sub-agent delegation, and sustained reasoning over long time horizons. Key use cases include research agents, coding agents, analysis agents, data processing workflows, and any task requiring hierarchical task decomposition with specialized sub-agents.
---

# LangChain DeepAgents Framework

Build sophisticated "deep" AI agents capable of handling complex, multi-step tasks through planning, file management, hierarchical delegation, and detailed prompting.

## Core Concepts

DeepAgents extends beyond simple tool-calling loops to provide four key capabilities inspired by Claude Code, Deep Research, and Manus:

1. **Planning Tool** - Structured task decomposition via TODO lists
2. **Virtual Filesystem** - Context management and artifact storage
3. **Sub-Agent Delegation** - Hierarchical task distribution with context isolation
4. **Detailed System Prompt** - Comprehensive behavioral instructions

## Quick Start

### Basic Agent Creation

```python
from deepagents import create_deep_agent
from langchain_core.tools import tool

@tool
def internet_search(query: str, max_results: int = 5) -> str:
    """Run a web search"""
    # Implementation here
    return results

# Define agent instructions
instructions = """You are an expert researcher.
Your job is to conduct thorough research and write polished reports."""

# Create the agent
agent = create_deep_agent(
    tools=[internet_search],
    system_prompt=instructions,
    model="claude-sonnet-4-20250514"  # Optional, this is the default
)

# Invoke the agent
result = agent.invoke({
    "messages": [{"role": "user", "content": "Research quantum computing"}]
})
```

### Async Agent Creation

```python
from deepagents import async_create_deep_agent

agent = async_create_deep_agent(
    tools=[async_tool],
    system_prompt=instructions
)

async for chunk in agent.astream(
    {"messages": [{"role": "user", "content": "query"}]},
    stream_mode="values"
):
    if "messages" in chunk:
        chunk["messages"][-1].pretty_print()
```

## Architecture

DeepAgents uses a **middleware-based architecture** where capabilities are added through composable components:

### Default Middleware Stack

1. **TodoListMiddleware** - Planning and task tracking
2. **FilesystemMiddleware** - File operations and memory
3. **SubAgentMiddleware** - Hierarchical delegation
4. **SummarizationMiddleware** - Context management (from LangChain)
5. **AnthropicPromptCachingMiddleware** - Performance optimization
6. **HumanInTheLoopMiddleware** - Tool approval workflow

Each middleware can extend state, provide tools, and modify system prompts.

## Planning with TODO Lists

The planning tool helps agents structure complex tasks. It's a no-op tool that aids reasoning without executing actions.

```python
from langchain.agents import create_agent
from langchain.agents.middleware import TodoListMiddleware

agent = create_agent(
    model="claude-sonnet-4-20250514",
    middleware=[
        TodoListMiddleware(
            system_prompt="Use write_todos to structure your approach..."
        )
    ]
)
```

**TODO Structure:**
```python
{
    "description": "Research quantum computing applications",
    "status": "pending" | "in_progress" | "completed"
}
```

The agent maintains an explicit plan in state, preventing shallow reasoning over long horizons.

## Virtual Filesystem

FilesystemMiddleware provides four tools for managing information:

- `write_file` - Create or overwrite files
- `read_file` - Retrieve file contents
- `edit_file` - Modify existing files
- `ls` - List available files

### Short-term Memory (Default)

Files stored in agent state, single-level directory:

```python
from deepagents import create_deep_agent

agent = create_deep_agent(tools=[...], system_prompt="...")

# Pass files in
result = agent.invoke({
    "messages": [...],
    "files": {"notes.txt": "Initial context"}
})

# Access files after execution
files = result["files"]
```

### Long-term Memory (Persistent)

Enable persistent storage with a Store backend:

```python
from langchain.agents import create_agent
from deepagents.middleware import FilesystemMiddleware
from langgraph.store.memory import InMemoryStore

store = InMemoryStore()

agent = create_agent(
    model="claude-sonnet-4-20250514",
    store=store,
    middleware=[
        FilesystemMiddleware(
            long_term_memory=True,
            custom_tool_descriptions={
                "write_file": "Use this to save important findings..."
            }
        )
    ]
)
```

Files prefixed with `/memories/` persist across threads when `long_term_memory=True`.

**Context Management:** Tools returning large results (>20k tokens) are automatically evicted to filesystem to preserve context window.

## Sub-Agent Delegation

Sub-agents enable hierarchical task decomposition with context isolation:

```python
from deepagents import create_deep_agent

# Define specialized sub-agent
research_subagent = {
    "name": "research-agent",
    "description": "Expert at conducting deep research on specific topics",
    "system_prompt": """You are a research specialist.
    Conduct thorough research and provide detailed, cited answers.""",
    "tools": [internet_search],
    "model": "openai:gpt-4o"  # Optional model override
}

agent = create_deep_agent(
    tools=[...],
    system_prompt="You are a project coordinator...",
    subagents=[research_subagent]
)
```

### Sub-Agent Properties

- **Context Isolation:** Each invocation runs in separate conversation
- **Autonomous Execution:** Sub-agents complete tasks independently
- **Single Result:** Returns synthesized result, not message stream
- **Stateless:** No state maintained between invocations

### Default General-Purpose Sub-Agent

Always available with same instructions and tools as main agent, useful for context quarantine.

### Custom Pre-Built Sub-Agents

```python
from langchain.agents import create_agent

# Build custom agent graph
custom_agent = create_agent(
    model="claude-sonnet-4-20250514",
    tools=[specialized_tools],
    system_prompt="Specialized instructions..."
)

# Use as sub-agent
custom_subagent = {
    "name": "data-analyzer",
    "description": "Specialized for complex data analysis",
    "graph": custom_agent
}

agent = create_deep_agent(
    tools=[...],
    system_prompt="...",
    subagents=[custom_subagent]
)
```

## Model Configuration

### Main Agent Model

```python
from langchain.chat_models import init_chat_model

model = init_chat_model("openai:gpt-4o")

agent = create_deep_agent(
    model=model,
    tools=[...],
    system_prompt="..."
)
```

### Per-SubAgent Model Configuration

```python
subagent = {
    "name": "critique-agent",
    "description": "Reviews and critiques outputs",
    "system_prompt": "You are a tough editor...",
    "model": "anthropic:claude-3-5-haiku-20241022",  # Fast, deterministic
    "temperature": 0,
    "max_tokens": 8192
}
```

## Human-in-the-Loop

Require human approval for specific tool executions:

```python
from deepagents import create_deep_agent
from langgraph.checkpoint.memory import InMemorySaver

# Configure tool approval
agent = create_deep_agent(
    tools=[your_tools],
    system_prompt="...",
    interrupt_on={
        "write_file": {
            "allowed_decisions": ["approve", "edit", "reject"]
        },
        "delete_data": True  # Shortcut for all approval options
    }
)

# Attach checkpointer (required for HITL)
agent.checkpointer = InMemorySaver()
```

### Approval Workflow

```python
from langgraph.types import Command

config = {"configurable": {"thread_id": "1"}}

# Start execution
for s in agent.stream({"messages": [{"role": "user", "content": "..."}]}, config=config):
    print(s)

# Approve tool call
for s in agent.stream(Command(resume=[{"type": "accept"}]), config=config):
    print(s)

# Edit tool call
for s in agent.stream(
    Command(resume=[{
        "type": "edit",
        "args": {"action": "write_file", "args": {"path": "output.txt", "content": "..."}}
    }]),
    config=config
):
    print(s)

# Reject with feedback
for s in agent.stream(
    Command(resume=[{"type": "response", "args": "Please revise the approach..."}]),
    config=config
):
    print(s)
```

## Custom Middleware

Extend agent capabilities with custom middleware:

```python
from langchain.agents.middleware import AgentMiddleware

class CustomMiddleware(AgentMiddleware):
    name = "custom"
    
    @property
    def state_schema(self):
        return {"custom_field": str}
    
    @property
    def tools(self):
        return [custom_tool]
    
    def wrap_model_call(self, request, handler):
        # Modify system prompt
        request.system_prompt += "\nCustom instructions..."
        return handler(request)

agent = create_agent(
    model="claude-sonnet-4-20250514",
    middleware=[CustomMiddleware(), ...]
)
```

## MCP Tools Integration

Use Model Context Protocol tools (async required):

```python
from langchain_mcp_adapters.client import MultiServerMCPClient
from deepagents import async_create_deep_agent

async def main():
    # Collect MCP tools
    mcp_client = MultiServerMCPClient(...)
    mcp_tools = await mcp_client.get_tools()
    
    # Create agent
    agent = async_create_deep_agent(
        tools=mcp_tools,
        system_prompt="..."
    )
    
    # Stream execution
    async for chunk in agent.astream(
        {"messages": [{"role": "user", "content": "..."}]},
        stream_mode="values"
    ):
        if "messages" in chunk:
            chunk["messages"][-1].pretty_print()
```

## Advanced Patterns

### Research Agent with Critique Sub-Agent

See `scripts/research_agent.py` for complete implementation.

Key elements:
- Internet search tool for gathering information
- Research sub-agent for deep dives with proper citations
- Critique sub-agent for quality review
- Coordinator main agent that orchestrates workflow

### Coding Agent with File Management

See `scripts/coding_agent.py` for complete implementation.

Key elements:
- Code execution and testing tools
- File operations for organizing code
- Planning tool for structuring implementation
- Memory persistence for project context

## Design Patterns

### Sequential Workflow

```markdown
1. Analyze the request (write_todos to plan)
2. Research background (delegate to research sub-agent)
3. Generate draft (write_file to save)
4. Review draft (delegate to critique sub-agent)
5. Finalize report (edit_file to refine)
6. Deliver output (read_file and present)
```

### Conditional Branching

```markdown
1. Determine task type:
   **New analysis?** → Research workflow
   **Update existing?** → Edit workflow
   
2. Research workflow:
   - Gather information
   - Create new file
   - Generate report
   
3. Edit workflow:
   - Read existing file
   - Identify changes
   - Edit file
```

## Best Practices

### System Prompt Design

- **Be specific:** Define exact role and responsibilities
- **Include workflows:** Describe multi-step processes
- **Set expectations:** Clarify output format and quality standards
- **Reference tools:** Explain when to use each tool
- **Keep concise:** Focus on essential instructions

### Tool Design

- **Clear descriptions:** Explain what each tool does
- **Specific parameters:** Define expected inputs and outputs
- **Error handling:** Return informative error messages
- **Deterministic:** Make tools reliable and predictable

### Sub-Agent Design

- **Focused expertise:** Each sub-agent should have narrow, clear purpose
- **Isolated context:** Use sub-agents to prevent context pollution
- **Appropriate tools:** Give only necessary tools to each sub-agent
- **Clear descriptions:** Main agent needs to know when to delegate

### Context Management

- **Use filesystem:** Save long tool results to files
- **Leverage sub-agents:** Isolate complex subtasks
- **Enable summarization:** Let middleware compress history
- **Prefix /memories/:** Persist important information across sessions

## Debugging and Monitoring

### LangSmith Integration

```python
import os

os.environ["LANGSMITH_TRACING"] = "true"
os.environ["LANGSMITH_PROJECT"] = "deepagents-research"
os.environ["LANGSMITH_API_KEY"] = "your-key"

agent = create_deep_agent(...)
```

### Streaming for Observability

```python
for chunk in agent.stream(
    {"messages": [{"role": "user", "content": "..."}]},
    stream_mode="values"
):
    if "messages" in chunk:
        print(chunk["messages"][-1].content)
```

## Common Pitfalls

1. **Shallow Prompts:** Deep agents need detailed instructions to leverage capabilities fully
2. **Wrong Tool Granularity:** Tools should be neither too narrow nor too broad
3. **Ignoring Context Limits:** Monitor token usage, leverage filesystem for large data
4. **Over-Planning:** Don't force TODO lists for simple tasks
5. **Sub-Agent Overuse:** Delegation has overhead; use judiciously

## Performance Optimization

- **Prompt Caching:** Enabled by default for Anthropic models
- **Efficient Models:** Use faster models for sub-agents when appropriate
- **Context Pruning:** Leverage filesystem to evict large tool results
- **Summarization:** Enable automatic history compression for long tasks

## Resources

- **scripts/**: Example implementations (research agent, coding agent)
- **references/**: Detailed API documentation and configuration guide
