# LangGraph Design Patterns

Common architectural patterns for building agents with LangGraph.

## Agent Architectures

### 1. ReAct Pattern (Reasoning + Acting)

The fundamental pattern for tool-using agents that reason and act iteratively.

**When to use:** Single-agent tasks requiring tool calls and reasoning loops

**Structure:**
- Agent node (LLM) → Conditional edge → Tools node → Back to agent
- Agent decides: Call tool OR finish
- Tools execute and return results
- Loop continues until agent finishes

**Code pattern:**
```python
workflow.add_node("agent", call_model)
workflow.add_node("tools", tool_node)
workflow.add_conditional_edges("agent", tools_condition)
workflow.add_edge("tools", "agent")
```

### 2. Plan-and-Execute Pattern

Agent first creates a plan, then executes steps sequentially.

**When to use:** Complex tasks needing upfront planning

**Structure:**
- Planner node → Executor nodes → Validator node
- Plan created once, then executed step-by-step
- Each step can be re-planned if needed

### 3. Reflection Pattern

Agent generates output, reflects on quality, and iterates.

**When to use:** Tasks requiring quality assessment and refinement

**Structure:**
- Generator node → Reflector node → Conditional edge
- If quality sufficient: END
- If not: Back to generator with feedback

### 4. Router Pattern

Route different request types to specialized handlers.

**When to use:** Multiple distinct workflows based on input classification

**Structure:**
- Classifier node → Conditional edges → Specialized handlers
- Each handler optimized for specific task type

## Multi-Agent Patterns

### 1. Network (Peer-to-Peer)

Agents can communicate directly with any other agent.

**When to use:** Collaborative problem-solving, no clear hierarchy

**Characteristics:**
- Each agent decides next agent to invoke
- Flexible communication paths
- More complex coordination

**Implementation:**
```python
def agent_node(state):
    # Agent decides who to call next
    if needs_research:
        return Command(goto="researcher")
    elif needs_analysis:
        return Command(goto="analyst")
    return Command(goto=END)
```

### 2. Supervisor (Hierarchical)

Central supervisor coordinates specialized agents.

**When to use:** Clear task delegation, centralized control

**Characteristics:**
- Supervisor receives all inputs and outputs
- Worker agents don't communicate directly
- Simpler coordination logic

**Implementation:**
```python
def supervisor(state):
    # Supervisor decides which agent to call
    decision = llm.with_structured_output(Router).invoke(state)
    return Command(goto=decision["next"])

# Agents report back to supervisor
for agent in agents:
    workflow.add_edge(agent, "supervisor")
```

### 3. Hierarchical Teams

Nested supervisors managing sub-teams of agents.

**When to use:** Very complex systems with clear organizational structure

**Characteristics:**
- Multiple levels of supervision
- Teams can be treated as single agents
- Scales to large systems

### 4. Sequential Workflow

Deterministic sequence of agent steps.

**When to use:** Well-defined processes with fixed order

**Characteristics:**
- Predictable execution path
- Each agent processes in turn
- Clear input/output contracts

**Implementation:**
```python
workflow.add_edge("agent1", "agent2")
workflow.add_edge("agent2", "agent3")
workflow.add_edge("agent3", END)
```

## State Management Patterns

### 1. Shared Global State

All agents access and modify common state.

**When to use:** Agents need visibility into all information

**Pattern:**
```python
class GlobalState(TypedDict):
    messages: Annotated[list, add_messages]
    shared_data: dict
    status: str

# All agents receive and update same state
```

### 2. Private Agent State

Agents have private state, only share final results.

**When to use:** Agents work independently, minimal information sharing

**Pattern:**
```python
def agent_wrapper(state: GlobalState):
    # Extract relevant data for this agent
    agent_state = {"input": state["task"]}
    
    # Run agent with private state
    result = agent_graph.invoke(agent_state)
    
    # Return only final output to global state
    return {"results": result["output"]}
```

### 3. Scoped State Channels

Different state keys for different purposes.

**When to use:** Complex workflows with distinct data flows

**Pattern:**
```python
class State(TypedDict):
    # User-facing messages
    messages: Annotated[list, add_messages]
    
    # Internal coordination
    next_agent: str
    task_queue: list
    
    # Results accumulation
    research_data: dict
    analysis_results: dict
```

## Human-in-the-Loop Patterns

### 1. Approval Gates

Pause for human approval before critical actions.

**Pattern:**
```python
def approval_node(state):
    decision = interrupt(f"Approve: {state['action']}?")
    return {"approved": decision == "yes"}

workflow.add_conditional_edges(
    "approval_node",
    lambda s: "execute" if s["approved"] else "reject"
)
```

### 2. Human as Tool

Treat human input as a tool the agent can call.

**Pattern:**
```python
@tool
def ask_human(question: str) -> str:
    """Ask human for input."""
    return interrupt(question)

# Agent can call ask_human like any tool
```

### 3. Review and Edit

Human can review and modify agent output.

**Pattern:**
```python
def create_draft(state):
    draft = generate_content(state)
    return {"draft": draft}

def review_point(state):
    edited = interrupt({
        "draft": state["draft"],
        "message": "Review and edit"
    })
    return {"final": edited}
```

### 4. Breakpoint Debugging

Pause at any node for inspection.

**Pattern:**
```python
graph = workflow.compile(
    checkpointer=memory,
    interrupt_before=["critical_node"],  # Pause before
    interrupt_after=["review_node"]      # Pause after
)
```

## Error Handling Patterns

### 1. Retry with Backoff

Automatically retry failed operations.

**Pattern:**
```python
def resilient_node(state, config):
    max_retries = 3
    for attempt in range(max_retries):
        try:
            return execute_operation(state)
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)  # Exponential backoff
```

### 2. Fallback Nodes

Route to alternative nodes on failure.

**Pattern:**
```python
def try_primary(state):
    try:
        return {"result": primary_method(state)}
    except:
        return {"use_fallback": True}

workflow.add_conditional_edges(
    "try_primary",
    lambda s: "fallback" if s.get("use_fallback") else "success"
)
```

### 3. Checkpoint Recovery

Resume from last successful checkpoint after errors.

**Pattern:**
```python
try:
    result = graph.invoke(input, config)
except Exception:
    # Get state from last successful checkpoint
    state = graph.get_state(config)
    # Fix issue or modify state
    graph.update_state(config, {"fixed": True})
    # Resume execution
    result = graph.invoke(None, config)
```

## Optimization Patterns

### 1. Parallel Execution

Execute independent nodes concurrently.

**Pattern:**
```python
# Both nodes run in parallel
workflow.add_edge(START, "node1")
workflow.add_edge(START, "node2")

# Join results
workflow.add_edge("node1", "join")
workflow.add_edge("node2", "join")
```

### 2. Conditional Short-Circuits

Skip unnecessary work based on conditions.

**Pattern:**
```python
def early_exit_check(state):
    if can_answer_directly(state):
        return "direct_answer"
    return "full_process"

workflow.add_conditional_edges(
    "check",
    early_exit_check,
    {
        "direct_answer": "fast_path",
        "full_process": "comprehensive_path"
    }
)
```

### 3. Caching Results

Store and reuse expensive computations.

**Pattern:**
```python
cache = {}

def cached_node(state):
    key = state["query"]
    if key in cache:
        return {"result": cache[key], "from_cache": True}
    
    result = expensive_operation(state)
    cache[key] = result
    return {"result": result}
```

## Streaming Patterns

### 1. Progressive Output

Stream partial results as they become available.

**Pattern:**
```python
def streaming_node(state):
    writer = get_stream_writer()
    
    for chunk in process_in_chunks(state):
        writer(chunk)  # Stream each chunk
        
    return {"final": combine_chunks()}
```

### 2. Token-by-Token Display

Show LLM generation in real-time.

**Pattern:**
```python
async for token, metadata in graph.astream(
    input,
    stream_mode="messages"
):
    print(token.content, end="", flush=True)
```

### 3. Progress Indicators

Provide feedback during long operations.

**Pattern:**
```python
def long_operation(state):
    writer = get_stream_writer()
    
    steps = ["Loading", "Processing", "Analyzing", "Complete"]
    for i, step in enumerate(steps):
        writer(f"[{i+1}/{len(steps)}] {step}...")
        perform_step(step)
    
    return {"result": "done"}
```
