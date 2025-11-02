# LangGraph API Reference

This reference covers the core LangGraph APIs and components.

## Core Graph Components

### StateGraph

The main graph building class for creating stateful workflows.

```python
from langgraph.graph import StateGraph, START, END

class MyState(TypedDict):
    messages: list
    count: int

workflow = StateGraph(MyState)
```

**Key Methods:**
- `add_node(name, func)` - Add a node to the graph
- `add_edge(from_node, to_node)` - Add a fixed edge
- `add_conditional_edges(source, condition, mapping)` - Add conditional routing
- `set_entry_point(node)` - Set the starting node (alternative to START)
- `compile(checkpointer=None, interrupt_before=None, interrupt_after=None)` - Compile the graph

### MessagesState

Pre-built state class for message-based workflows.

```python
from langgraph.graph import MessagesState

class MyState(MessagesState):
    # Automatically includes:
    # messages: Annotated[list, add_messages]
    custom_field: str
```

## State Management

### Reducers

Functions that define how state updates are combined.

```python
from typing import Annotated
from langgraph.graph.message import add_messages

class State(TypedDict):
    # Append messages instead of replacing
    messages: Annotated[list, add_messages]
    
    # Default behavior (replace)
    count: int
```

**Built-in Reducers:**
- `add_messages` - Append messages, updating by ID
- `operator.add` - Addition for numbers or concatenation for sequences

## Prebuilt Components

### create_react_agent

```python
from langgraph.prebuilt import create_react_agent

agent = create_react_agent(
    model="anthropic:claude-3-7-sonnet-latest",
    tools=[tool1, tool2],
    prompt="System prompt",
    checkpointer=memory,
)
```

### ToolNode

```python
from langgraph.prebuilt import ToolNode, tools_condition

tool_node = ToolNode([tool1, tool2])
workflow.add_node("tools", tool_node)
workflow.add_conditional_edges("agent", tools_condition)
```

## Checkpointers

- `InMemorySaver` - Development/testing
- `SqliteSaver` - File-based persistence  
- `AsyncSqliteSaver` - Async SQLite
- `PostgresSaver` - Production Postgres

## Execution

- `invoke(input, config)` - Sync, returns final state
- `stream(input, stream_mode)` - Stream outputs
- `ainvoke()` / `astream()` - Async versions

**Stream Modes:** `"values"`, `"updates"`, `"messages"`, `"custom"`, `"debug"`

## Human-in-the-Loop

```python
from langgraph.types import interrupt, Command

def node(state):
    decision = interrupt("Approve?")
    return {"approved": decision}

# Resume
graph.invoke(Command(resume="yes"), config)
```
