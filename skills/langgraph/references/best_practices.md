# LangGraph Best Practices

Guidelines for building production-ready LangGraph applications.

## State Design

**Keep state minimal and focused**
- Only include data that needs to persist across nodes
- Avoid storing computed values that can be regenerated
- Use TypedDict for clear state schema

**Use appropriate reducers**
- `add_messages` for message lists (handles updates by ID)
- Default behavior (replacement) for simple values
- Custom reducers for complex merge logic

**Example:**
```python
class State(TypedDict):
    # Good: Only essential data
    messages: Annotated[list, add_messages]
    user_id: str
    
    # Avoid: Temporary or computed values
    # intermediate_result: dict  # Regenerate in nodes instead
```

## Node Design

**Single Responsibility Principle**
- Each node should have one clear purpose
- Break complex logic into multiple nodes
- Makes testing and debugging easier

**Handle errors gracefully**
```python
def safe_node(state):
    try:
        return {"result": risky_operation(state)}
    except SpecificError as e:
        return {"error": str(e), "fallback": True}
```

**Return explicit state updates**
```python
# Good: Clear what's being updated
def node(state):
    return {"count": state["count"] + 1, "status": "complete"}

# Avoid: Modifying state in place
def bad_node(state):
    state["count"] += 1  # Don't do this
    return state
```

## Tool Design

**Provide detailed docstrings**
- LLMs use docstrings to understand when to call tools
- Include parameter descriptions
- Specify expected output format

```python
@tool
def search_database(query: str, limit: int = 10) -> str:
    """Search the customer database.
    
    Args:
        query: Natural language search query
        limit: Maximum number of results (default 10)
        
    Returns:
        JSON string with matching customer records
    """
    return search(query, limit)
```

**Use Pydantic for complex inputs**
```python
from pydantic import BaseModel, Field

class SearchParams(BaseModel):
    query: str = Field(description="Search query")
    filters: dict = Field(default={}, description="Optional filters")
    
@tool(args_schema=SearchParams)
def search(query: str, filters: dict = None):
    """Advanced search with filters."""
    pass
```

**Keep tools focused**
- One tool = one action
- Avoid tools that do multiple unrelated things
- Easier for LLM to choose correctly

## Prompting

**Provide clear system instructions**
```python
system_prompt = """You are a customer service agent.

Your responsibilities:
1. Answer customer questions using available tools
2. Escalate complex issues to human agents
3. Maintain a friendly, professional tone

Guidelines:
- Always verify information before responding
- Ask clarifying questions when needed
- Use tools to look up current information
"""
```

**Guide tool usage**
- Explain when each tool should be used
- Provide examples of good tool calls
- Specify output expectations

**Set appropriate temperature**
- Lower (0-0.3) for deterministic, factual tasks
- Higher (0.7-1.0) for creative tasks
- Consider task requirements

## Checkpointing Strategy

**Choose the right checkpointer**
- `InMemorySaver`: Development, testing, demos
- `SqliteSaver`: Small apps, local development
- `PostgresSaver`: Production, multiple users, scale

**Use meaningful thread IDs**
```python
# Good: User-specific threads
config = {"configurable": {"thread_id": f"user-{user_id}"}}

# Good: Session-based threads
config = {"configurable": {"thread_id": f"session-{session_id}"}}
```

**Clean up old threads**
```python
# Implement cleanup for inactive threads
def cleanup_old_threads(checkpointer, days=30):
    cutoff = datetime.now() - timedelta(days=days)
    # Remove threads not accessed since cutoff
```

## Streaming

**Stream for better UX**
- Use `stream_mode="messages"` for LLM tokens
- Provide progress updates for long operations
- Show intermediate results when possible

**Buffer appropriately**
```python
# Token streaming
async for token, metadata in graph.astream(input, stream_mode="messages"):
    print(token.content, end="", flush=True)

# State streaming with processing
for chunk in graph.stream(input, stream_mode="updates"):
    processed = process_update(chunk)
    display(processed)
```

**Handle streaming errors**
```python
async def safe_stream(graph, input):
    try:
        async for chunk in graph.astream(input):
            yield chunk
    except Exception as e:
        yield {"error": str(e)}
```

## Multi-Agent Systems

**Choose the right pattern**
- Network: Equal agents, flexible collaboration
- Supervisor: Clear delegation, centralized control
- Sequential: Fixed workflow, predictable
- Hierarchical: Complex systems, nested teams

**Define clear agent boundaries**
```python
# Each agent has specific expertise
research_agent = create_react_agent(model, research_tools)
analysis_agent = create_react_agent(model, analysis_tools)
writing_agent = create_react_agent(model, writing_tools)
```

**Manage state sharing carefully**
- Shared state: Full transparency, potential conflicts
- Private state: Isolation, less context
- Choose based on coordination needs

## Testing

**Test nodes independently**
```python
def test_node():
    state = {"input": "test"}
    result = my_node(state)
    assert result["output"] == "expected"
```

**Test with checkpointers**
```python
def test_with_memory():
    checkpointer = InMemorySaver()
    graph = workflow.compile(checkpointer=checkpointer)
    
    config = {"configurable": {"thread_id": "test-1"}}
    result1 = graph.invoke(input1, config)
    result2 = graph.invoke(input2, config)
    
    # Verify state persistence
    assert result2["context"] includes result1
```

**Test streaming**
```python
async def test_streaming():
    chunks = []
    async for chunk in graph.astream(input, stream_mode="updates"):
        chunks.append(chunk)
    
    assert len(chunks) > 0
    assert chunks[-1]["status"] == "complete"
```

## Performance

**Minimize state size**
- Store references instead of full objects
- Use IDs instead of entire documents
- Compress large data if needed

**Use async for I/O bound operations**
```python
async def fetch_data(state):
    # Concurrent API calls
    results = await asyncio.gather(
        api1.get(state["query"]),
        api2.get(state["query"]),
    )
    return {"results": results}
```

**Cache expensive operations**
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def expensive_lookup(key):
    return perform_expensive_operation(key)

def node(state):
    result = expensive_lookup(state["key"])
    return {"result": result}
```

**Batch operations when possible**
```python
def batch_process(state):
    items = state["items"]
    
    # Process in batches instead of one-by-one
    batch_size = 10
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        process_batch(batch)
```

## Monitoring and Debugging

**Use LangSmith for observability**
```python
import os
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "your-key"
os.environ["LANGCHAIN_PROJECT"] = "my-project"

# Traces automatically sent to LangSmith
```

**Add logging**
```python
import logging

logger = logging.getLogger(__name__)

def node(state):
    logger.info(f"Processing state: {state.get('id')}")
    try:
        result = process(state)
        logger.info("Processing complete")
        return result
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        raise
```

**Use breakpoints for debugging**
```python
graph = workflow.compile(
    checkpointer=memory,
    interrupt_before=["critical_node"]  # Pause for inspection
)

# Inspect state at breakpoint
state = graph.get_state(config)
print("State at breakpoint:", state.values)

# Resume
graph.invoke(None, config)
```

## Security

**Validate tool inputs**
```python
@tool
def execute_query(query: str) -> str:
    """Execute database query."""
    # Validate before executing
    if not is_safe_query(query):
        return "Error: Invalid query"
    return db.execute(query)
```

**Sanitize user inputs**
```python
def node(state):
    user_input = state["messages"][-1].content
    # Remove or escape dangerous content
    safe_input = sanitize(user_input)
    return {"processed": safe_input}
```

**Set resource limits**
```python
# Limit execution time
from langchain_core.runnables import RunnableConfig

config = RunnableConfig(
    recursion_limit=20,  # Max graph steps
    max_concurrency=5,   # Parallel node limit
)

result = graph.invoke(input, config)
```

## Deployment

**Use environment variables for configuration**
```python
import os

DATABASE_URL = os.getenv("DATABASE_URL")
API_KEY = os.getenv("API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
```

**Implement health checks**
```python
def health_check():
    try:
        # Test critical components
        checkpointer.get(test_config)
        model.invoke("test")
        return {"status": "healthy"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
```

**Version your graphs**
```python
# Track graph versions in state
class State(TypedDict):
    _graph_version: str  # e.g., "v2.1.0"
    messages: list

# Handle version migrations
def migrate_state(old_state, from_version, to_version):
    # Transform state for compatibility
    pass
```

**Monitor performance**
```python
import time

def timed_node(state):
    start = time.time()
    result = expensive_operation(state)
    duration = time.time() - start
    
    # Log or send to monitoring service
    logger.info(f"Node took {duration:.2f}s")
    
    return result
```
