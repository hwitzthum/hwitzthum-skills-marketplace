---
name: langgraph
description: Comprehensive guide for building stateful, agentic AI applications using the LangGraph framework. Use when building agents with LangChain, creating multi-agent systems, implementing workflows with cycles and state management, adding human-in-the-loop capabilities, building ReAct agents, creating supervisor architectures, implementing persistence and memory, or working with checkpointers and streaming. Covers graph construction, state management, tool integration, multi-agent patterns, checkpointing, and deployment strategies.
---

# LangGraph Framework Skill

Build stateful, multi-agent AI applications with LangGraph - a framework for creating sophisticated agent workflows as cyclical graphs with built-in persistence, human-in-the-loop capabilities, and flexible orchestration.

## What is LangGraph?

LangGraph is a low-level orchestration framework for building long-running, stateful agents and multi-agent systems. Unlike linear chains, LangGraph represents workflows as **graphs with cycles**, enabling agents to reason iteratively and make dynamic decisions.

**Core capabilities:**
- **Stateful workflows**: Maintain context across multiple steps with built-in persistence
- **Cyclical execution**: Agents can loop, retry, and make sequential decisions
- **Human-in-the-loop**: Pause execution for human approval or input at any point
- **Multi-agent orchestration**: Coordinate multiple specialized agents with various patterns
- **Durable execution**: Automatic checkpointing for fault tolerance and recovery
- **Streaming**: Real-time feedback with multiple streaming modes

## When to Use LangGraph

Use LangGraph when building:

1. **Tool-using agents** that reason iteratively (ReAct pattern)
2. **Multi-agent systems** requiring coordination between specialists
3. **Workflows with cycles** where steps may repeat based on conditions
4. **Human-in-the-loop applications** needing approval gates or human input
5. **Long-running processes** requiring persistence and resumption
6. **Complex decision flows** with conditional branching
7. **Stateful applications** maintaining context across interactions

LangGraph is ideal when AgentExecutor or simple chains are insufficient for your complexity needs.

## Quick Start

### Installation

```bash
pip install -U langgraph langchain langchain-anthropic
```

### Basic ReAct Agent (Prebuilt)

The fastest way to create a tool-using agent:

```python
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool

@tool
def get_weather(city: str) -> str:
    """Get weather for a given city."""
    return f"It's sunny in {city}!"

agent = create_react_agent(
    model="anthropic:claude-3-7-sonnet-latest",
    tools=[get_weather],
    prompt="You are a helpful assistant"
)

result = agent.invoke({
    "messages": [{"role": "user", "content": "What's the weather in SF?"}]
})
```

**Why this works:** The prebuilt agent handles the entire ReAct loop - the model calls tools, tools execute, and results flow back to the model until completion.

### Custom Graph Construction

For full control, build graphs from scratch. See `scripts/basic_react_agent.py` for complete implementation.

## Core Concepts

### 1. State

State is a shared data structure passed between nodes. Define using TypedDict:

```python
from typing import Annotated, TypedDict
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]  # Messages with smart merging
    user_id: str                             # Simple value (replaced)
    count: int
```

**Reducers** control how updates merge:
- `add_messages`: Appends messages, updates existing by ID
- Default: Replaces the value entirely
- Custom: Define your own merge logic

**Why reducers matter:** They let you accumulate data (like messages) instead of overwriting, essential for conversational agents.

### 2. Nodes

Nodes are functions that process state and return updates:

```python
def my_node(state: AgentState):
    # Process state
    response = model.invoke(state["messages"])
    
    # Return state updates (not full state)
    return {"messages": [response]}
```

**Key principle:** Nodes return dictionaries containing only the fields to update, not the entire state.

### 3. Edges

Edges connect nodes and control flow:

```python
from langgraph.graph import StateGraph, START, END

workflow = StateGraph(AgentState)

# Fixed edge: Always go from A to B
workflow.add_edge("node_a", "node_b")

# Conditional edge: Decide dynamically
def should_continue(state):
    return "tools" if state["needs_tools"] else END

workflow.add_conditional_edges("agent", should_continue)
```

**Why conditional edges:** They enable dynamic routing based on state, like deciding whether to call tools or finish.

### 4. Graph Compilation

Compile the workflow to create an executable graph:

```python
from langgraph.checkpoint.memory import InMemorySaver

checkpointer = InMemorySaver()
graph = workflow.compile(
    checkpointer=checkpointer,  # Enable persistence
    interrupt_before=["approval"],  # Pause before approval node
)
```

## Building Agents Step-by-Step

### Step 1: Define State

```python
from typing import Annotated, Sequence
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class State(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
```

### Step 2: Create Nodes

```python
from langchain_openai import ChatOpenAI

model = ChatOpenAI(model="gpt-4o-mini")
model_with_tools = model.bind_tools([tool1, tool2])

def call_model(state: State):
    response = model_with_tools.invoke(state["messages"])
    return {"messages": [response]}
```

### Step 3: Add Tool Handling

```python
from langgraph.prebuilt import ToolNode

tool_node = ToolNode([tool1, tool2])
```

**Why ToolNode:** It automatically executes tools called by the LLM and formats results.

### Step 4: Define Routing Logic

```python
from langgraph.prebuilt import tools_condition

# tools_condition checks if LLM made tool calls
# Returns "tools" if yes, END if no
```

### Step 5: Build and Compile Graph

```python
workflow = StateGraph(State)
workflow.add_node("agent", call_model)
workflow.add_node("tools", tool_node)

workflow.add_edge(START, "agent")
workflow.add_conditional_edges("agent", tools_condition)
workflow.add_edge("tools", "agent")  # Loop back after tools

app = workflow.compile()
```

**Execution flow:**
1. Start → Agent (LLM)
2. If tool calls → Tools → Back to Agent
3. If no tool calls → END

### Step 6: Execute

```python
from langchain_core.messages import HumanMessage

result = app.invoke({
    "messages": [HumanMessage(content="What's 25 * 4?")]
})

print(result["messages"][-1].content)  # Final response
```

**Why this structure:** The loop allows the agent to use tools multiple times, reasoning about results before responding.

## Persistence and Memory

### Enable Checkpointing

```python
from langgraph.checkpoint.memory import InMemorySaver

checkpointer = InMemorySaver()
graph = workflow.compile(checkpointer=checkpointer)
```

### Conversation Memory

```python
config = {"configurable": {"thread_id": "user-123"}}

# First conversation
graph.invoke({"messages": [HumanMessage("My name is Alice")]}, config)

# Second conversation - remembers context
graph.invoke({"messages": [HumanMessage("What's my name?")]}, config)
```

**Thread management:** Each `thread_id` maintains separate conversation state. Different IDs = different conversations.

### Checkpointer Options

- **InMemorySaver**: Development/testing (data lost on restart)
- **SqliteSaver**: Persistent local storage
- **AsyncSqliteSaver**: Async version for async graphs
- **PostgresSaver**: Production-ready, handles scale

```python
# SQLite for persistence
from langgraph.checkpoint.sqlite import SqliteSaver

checkpointer = SqliteSaver.from_conn_string("checkpoints.db")
graph = workflow.compile(checkpointer=checkpointer)
```

**Why persistence matters:** Enables conversation memory, error recovery, human-in-the-loop, and time-travel debugging.

## Multi-Agent Systems

LangGraph excels at coordinating multiple agents. See `scripts/supervisor_pattern.py` for full implementation.

### Supervisor Pattern

A central supervisor delegates tasks to specialized agents:

```python
from langgraph.types import Command

def supervisor_node(state):
    # LLM decides which agent to call
    decision = llm.with_structured_output(Router).invoke(state["messages"])
    
    if decision["next"] == "FINISH":
        return Command(goto=END)
    
    return Command(goto=decision["next"])

# Specialized agents
workflow.add_node("researcher", research_agent)
workflow.add_node("analyst", analysis_agent)
workflow.add_node("supervisor", supervisor_node)

# Agents report back to supervisor
for agent in ["researcher", "analyst"]:
    workflow.add_edge(agent, "supervisor")

workflow.add_edge(START, "supervisor")
```

**Why supervisors:** Simplify coordination when you have clear task delegation and don't need peer-to-peer communication.

### Network Pattern

Agents can communicate with any other agent:

```python
def agent_node(state):
    result = process(state)
    
    # Decide next agent dynamically
    if needs_research:
        return Command(goto="researcher", update=result)
    elif needs_analysis:
        return Command(goto="analyst", update=result)
    else:
        return Command(goto=END, update=result)
```

**When to use:** Flexible collaboration where agents decide who to involve based on context.

## Human-in-the-Loop

### Interrupt for Approval

```python
from langgraph.types import interrupt

def approval_node(state):
    # Pause execution here
    decision = interrupt("Approve this action?")
    return {"approved": decision == "yes"}

graph = workflow.compile(
    checkpointer=memory,
    interrupt_before=["approval_node"]  # Can also use interrupt_after
)
```

### Resume After Interrupt

```python
from langgraph.types import Command

config = {"configurable": {"thread_id": "1"}}

# First run - pauses at interrupt
graph.invoke(input, config)

# Resume with approval
graph.invoke(Command(resume="yes"), config)
```

**Why interrupts:** Enable human review before critical actions, gather user input mid-workflow, or pause for debugging.

## Streaming

Stream outputs for responsive UIs. See `scripts/streaming_examples.py` for complete examples.

### Stream State Updates

```python
for chunk in graph.stream(input, stream_mode="updates"):
    print(f"Update from node: {chunk}")
```

### Stream LLM Tokens

```python
async for token, metadata in graph.astream(input, stream_mode="messages"):
    if hasattr(token, 'content') and token.content:
        print(token.content, end="", flush=True)
```

**Why stream tokens:** Show LLM generation in real-time for better UX, especially with slow models.

### Stream Custom Data

```python
from langgraph.config import get_stream_writer

def my_tool(data: str) -> str:
    writer = get_stream_writer()
    
    # Send progress updates
    writer("Processing step 1...")
    step1()
    writer("Processing step 2...")
    step2()
    
    return "Complete"

# Receive custom updates
for chunk in graph.stream(input, stream_mode="custom"):
    print(chunk)
```

**Stream modes:**
- `"values"`: Full state after each node
- `"updates"`: Only state changes from each node
- `"messages"`: LLM tokens as generated
- `"custom"`: User-defined progress signals
- `"debug"`: Detailed execution traces

## Example Scripts

The `scripts/` directory contains complete, runnable examples:

- **basic_react_agent.py**: Build a ReAct agent from scratch with full explanation
- **supervisor_pattern.py**: Multi-agent system with supervisor coordination
- **streaming_examples.py**: All streaming modes demonstrated
- **persistence_examples.py**: Checkpointing, memory, human-in-the-loop, error recovery

Run any example:
```bash
python scripts/basic_react_agent.py
```

## Reference Documentation

### API Reference
See `references/api_reference.md` for detailed API covering StateGraph, prebuilt components, checkpointers, execution methods, and more.

### Design Patterns
Read `references/design_patterns.md` for comprehensive patterns including agent architectures (ReAct, Plan-Execute, Reflection), multi-agent patterns (Network, Supervisor, Hierarchical), state management strategies, error handling, and optimization techniques.

### Best Practices
Consult `references/best_practices.md` for production guidance on state design, node structure, tool creation, prompting strategies, checkpointing, testing, performance optimization, security, and deployment.

## Teaching Approach

When explaining LangGraph implementations:

1. **Start with why**: Explain the problem this solves
2. **Show the pattern**: Demonstrate the code structure
3. **Explain the flow**: Walk through execution step-by-step
4. **Highlight key concepts**: Point out important principles
5. **Discuss alternatives**: When to use different approaches
6. **Reference resources**: Point to relevant scripts and docs

For example, when building a ReAct agent:
- "We use `tools_condition` because it handles routing: if the LLM called tools, go to the tools node; otherwise, end."
- "The edge from tools back to agent creates a loop, allowing the agent to reason about tool results and potentially call more tools."
- "This pattern works because each iteration refines the agent's understanding until it has enough information to respond."

## Troubleshooting

**Agent loops infinitely:**
- Set `recursion_limit` in config: `{"recursion_limit": 20}`
- Review conditional logic to ensure END is reachable
- Check if tools are returning expected formats

**State not persisting:**
- Verify checkpointer is passed to `compile()`
- Ensure same `thread_id` is used across invocations
- Check checkpointer setup (e.g., PostgresSaver.setup())

**Tools not being called:**
- Verify tools are bound to model: `model.bind_tools([tool])`
- Check tool docstrings are clear and descriptive
- Ensure model supports tool calling (e.g., GPT-4, Claude 3+)

**Streaming not working:**
- For token streaming, model must support streaming
- Check `stream_mode` matches data type you want
- For async streaming, use `astream()` not `stream()`

## Production Deployment

**Recommended stack:**
- **Checkpointer**: PostgresSaver for scale and reliability
- **Monitoring**: LangSmith for observability and debugging
- **Environment**: Use environment variables for configuration
- **Error handling**: Implement retry logic and fallbacks
- **Resource limits**: Set recursion_limit, timeouts

**Example production setup:**
```python
import os
from langgraph.checkpoint.postgres import PostgresSaver

# Environment configuration
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGSMITH_KEY")

# Production checkpointer
checkpointer = PostgresSaver.from_conn_string(os.getenv("DATABASE_URL"))
checkpointer.setup()

# Compile with limits
graph = workflow.compile(checkpointer=checkpointer)

# Execute with config
config = {
    "recursion_limit": 50,
    "configurable": {"thread_id": f"user-{user_id}"}
}

result = graph.invoke(input, config)
```

## Resources

- **Official Docs**: https://langchain-ai.github.io/langgraph/
- **GitHub**: https://github.com/langchain-ai/langgraph
- **Tutorials**: https://langchain-ai.github.io/langgraph/tutorials/
- **API Reference**: https://langchain-ai.github.io/langgraph/reference/

## Summary

LangGraph enables building sophisticated AI agents through:
- **Graphs with cycles** for iterative reasoning
- **Built-in persistence** for memory and recovery
- **Human-in-the-loop** for controlled execution
- **Multi-agent coordination** with flexible patterns
- **Streaming** for responsive user experiences

Start with `create_react_agent` for quick prototypes, then build custom graphs when you need more control. Use checkpointing for production applications, and leverage streaming for better UX.

The framework's power comes from treating agents as graphs, enabling complex control flows while maintaining clarity and debuggability.
