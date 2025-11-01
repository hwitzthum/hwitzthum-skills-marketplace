# Advanced DeepAgents Configuration

Advanced patterns, optimization strategies, and production configurations for LangChain DeepAgents.

## Production-Ready Agent Template

```python
import os
from deepagents import create_deep_agent
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.store.postgres import PostgresStore

def create_production_agent():
    """
    Production-ready agent with persistence, monitoring, and optimization.
    """
    
    # Database connection for persistence
    db_uri = os.environ["DATABASE_URL"]
    checkpointer = PostgresSaver.from_conn_string(db_uri)
    store = PostgresStore.from_conn_string(db_uri)
    
    # Define tools
    tools = [tool1, tool2, tool3]
    
    # Define specialized sub-agents
    subagents = [
        {
            "name": "analyzer",
            "description": "Data analysis specialist",
            "system_prompt": "...",
            "tools": [analysis_tool],
            "model": {
                "model": "openai:gpt-4o-mini",  # Cost-effective for sub-tasks
                "temperature": 0,
                "max_tokens": 4096
            }
        },
        {
            "name": "writer",
            "description": "Report writing specialist",
            "system_prompt": "...",
            "model": "anthropic:claude-sonnet-4-20250514"
        }
    ]
    
    # Create agent with optimizations
    agent = create_deep_agent(
        tools=tools,
        system_prompt=PRODUCTION_SYSTEM_PROMPT,
        subagents=subagents,
        model="anthropic:claude-sonnet-4-20250514",
        interrupt_on={
            "dangerous_operation": True,
            "data_deletion": True
        }
    )
    
    # Attach persistence
    agent.checkpointer = checkpointer
    
    # Configure store for long-term memory
    agent = agent.with_config({
        "store": store
    })
    
    return agent

# Usage
agent = create_production_agent()

# Invoke with user context
result = agent.invoke(
    {"messages": [...]},
    config={
        "configurable": {
            "thread_id": f"user-{user_id}",
            "user_id": user_id
        }
    }
)
```

## Memory Management Strategies

### Strategy 1: Ephemeral + Selective Persistence

Best for: Most applications balancing convenience and persistence

```python
from deepagents.memory.backends import CompositeBackend, StateBackend, StoreBackend
from deepagents.middleware import FilesystemMiddleware

backend = CompositeBackend(
    default=StateBackend(),  # Ephemeral by default
    routes={
        "/memories/": StoreBackend(),      # Persist memories
        "/templates/": StoreBackend(),     # Persist templates
        "/cache/": StateBackend(),         # Ephemeral cache
    }
)

agent = create_agent(
    middleware=[
        FilesystemMiddleware(backend=backend, long_term_memory=True)
    ],
    ...
)
```

**Usage pattern:**
```python
# Agent automatically handles routing
write_file("/memories/user_preferences.json", prefs)  # Persisted
write_file("temp_analysis.txt", data)                 # Ephemeral
write_file("/templates/report_template.md", template) # Persisted
```

### Strategy 2: Full Persistence

Best for: Long-running projects, collaborative agents

```python
from langgraph.store.postgres import PostgresStore

store = PostgresStore.from_conn_string(db_uri)

agent = create_agent(
    store=store,
    middleware=[
        FilesystemMiddleware(
            backend=StoreBackend(),
            long_term_memory=True
        )
    ],
    ...
)
```

### Strategy 3: Ephemeral Only

Best for: Stateless operations, quick tasks, privacy-sensitive

```python
# Default behavior - no special configuration needed
agent = create_deep_agent(...)
```

## Context Management

### Automatic Tool Result Eviction

Large tool results are automatically saved to files when they exceed token limit:

```python
from deepagents.middleware import FilesystemMiddleware

agent = create_agent(
    middleware=[
        FilesystemMiddleware(
            tool_token_limit_before_evict=15000  # Lower for aggressive eviction
        )
    ],
    ...
)
```

**How it works:**
1. Tool executes and returns large result (e.g., 25k tokens)
2. Middleware checks size against limit
3. If over limit, saves to `/tool_results/tool_name_timestamp.txt`
4. Replaces tool message content with: "Large result saved to file"
5. Agent can read file when needed

### Manual Context Management

```python
system_prompt = """When tool results are very large:
1. Scan the result for relevant information
2. Extract key points into a summary file
3. Save full result to a reference file
4. Continue working with the summary

Example:
tool_result = internet_search(...)  # Large result
write_file("summary.txt", extract_key_points(tool_result))
write_file("/ref/full_search.txt", tool_result)
"""
```

### Summarization Middleware

Automatically compress conversation history:

```python
from langchain.agents.middleware import SummarizationMiddleware

agent = create_agent(
    middleware=[
        SummarizationMiddleware(
            max_tokens=100000,  # Trigger summarization at this limit
            summarize_last_n=20  # Keep last N messages unsummarized
        ),
        # ... other middleware
    ],
    ...
)
```

## Sub-Agent Design Patterns

### Pattern 1: Sequential Pipeline

```python
subagents = [
    {
        "name": "researcher",
        "description": "Gathers raw information",
        "system_prompt": "Research and return raw findings with citations",
        "tools": [search_tool]
    },
    {
        "name": "analyzer",
        "description": "Analyzes research findings",
        "system_prompt": "Analyze data and extract insights",
        "tools": [analysis_tool]
    },
    {
        "name": "writer",
        "description": "Writes polished reports",
        "system_prompt": "Transform analysis into clear report",
        "model": "anthropic:claude-sonnet-4-20250514"
    }
]

# Main agent orchestrates
system_prompt = """Workflow:
1. research = task("researcher", "Research X")
2. analysis = task("analyzer", f"Analyze: {research}")
3. report = task("writer", f"Write report from: {analysis}")
"""
```

### Pattern 2: Parallel Specialists

```python
subagents = [
    {"name": "tech-researcher", "description": "Technical research", ...},
    {"name": "market-researcher", "description": "Market research", ...},
    {"name": "legal-researcher", "description": "Legal research", ...},
]

system_prompt = """For comprehensive analysis:
1. Delegate each aspect to specialist
2. tech = task("tech-researcher", ...)
3. market = task("market-researcher", ...)
4. legal = task("legal-researcher", ...)
5. Synthesize all findings into unified report
"""
```

### Pattern 3: Iterative Refinement

```python
subagents = [
    {
        "name": "generator",
        "description": "Generates initial content",
        "system_prompt": "Create initial draft",
        "model": "openai:gpt-4o-mini"  # Fast for drafts
    },
    {
        "name": "critic",
        "description": "Provides detailed critique",
        "system_prompt": "Critique for accuracy, clarity, completeness",
        "temperature": 0  # Consistent feedback
    }
]

system_prompt = """Iterative improvement:
1. draft = task("generator", request)
2. feedback = task("critic", draft)
3. If feedback suggests improvements:
   - draft = task("generator", f"Improve {draft} based on: {feedback}")
   - Repeat until quality threshold met
4. Deliver final draft
"""
```

### Pattern 4: Expert Panel

```python
subagents = [
    {"name": "expert-1", "description": "Expert in domain A", ...},
    {"name": "expert-2", "description": "Expert in domain B", ...},
    {"name": "expert-3", "description": "Expert in domain C", ...},
    {"name": "moderator", "description": "Synthesizes expert opinions", ...}
]

system_prompt = """Multi-expert analysis:
1. Get each expert's perspective independently
2. e1 = task("expert-1", question)
3. e2 = task("expert-2", question)
4. e3 = task("expert-3", question)
5. synthesis = task("moderator", f"Synthesize: {e1}, {e2}, {e3}")
"""
```

## Model Selection Strategy

### By Task Complexity

```python
MODEL_CONFIG = {
    "main": "anthropic:claude-sonnet-4-20250514",    # Complex orchestration
    "research": "openai:gpt-4o",                     # Deep analysis
    "simple": "openai:gpt-4o-mini",                  # Simple tasks
    "fast": "anthropic:claude-3-5-haiku-20241022",   # Speed-critical
    "code": "anthropic:claude-sonnet-4-20250514",    # Code generation
}

subagents = [
    {"name": "researcher", "model": MODEL_CONFIG["research"], ...},
    {"name": "summarizer", "model": MODEL_CONFIG["simple"], ...},
    {"name": "critic", "model": MODEL_CONFIG["fast"], ...},
]
```

### By Cost Optimization

```python
# Main agent: Powerful model for orchestration
# Sub-agents: Smaller models for focused tasks
# Critique: Fast model with deterministic output

agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-20250514",  # $3/$15 per M tokens
    subagents=[
        {
            "name": "worker",
            "model": "openai:gpt-4o-mini",  # $0.150/$0.600 per M tokens
            ...
        },
        {
            "name": "critic",
            "model": {
                "model": "anthropic:claude-3-5-haiku-20241022",  # $1/$5 per M tokens
                "temperature": 0
            },
            ...
        }
    ]
)
```

## Custom Middleware Examples

### Example 1: API Rate Limiting

```python
from langchain.agents.middleware import AgentMiddleware
import time

class RateLimitMiddleware(AgentMiddleware):
    name = "rate_limiter"
    
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.last_request = 0
        
    def wrap_model_call(self, request, handler):
        # Rate limit model calls
        elapsed = time.time() - self.last_request
        min_interval = 60.0 / self.requests_per_minute
        
        if elapsed < min_interval:
            time.sleep(min_interval - elapsed)
        
        self.last_request = time.time()
        return handler(request)
```

### Example 2: Request Logging

```python
class LoggingMiddleware(AgentMiddleware):
    name = "logger"
    
    def wrap_model_call(self, request, handler):
        print(f"Model Request: {len(request.messages)} messages")
        result = handler(request)
        print(f"Model Response: {len(result.content)} chars")
        return result
    
    def wrap_tool_call(self, request, handler):
        print(f"Tool Call: {request.tool_call.name}")
        result = handler(request)
        print(f"Tool Result: {len(str(result))} chars")
        return result
```

### Example 3: Cost Tracking

```python
class CostTrackingMiddleware(AgentMiddleware):
    name = "cost_tracker"
    
    @property
    def state_schema(self):
        return {
            "total_cost": float,
            "input_tokens": int,
            "output_tokens": int
        }
    
    def wrap_model_call(self, request, handler):
        result = handler(request)
        
        # Calculate costs (example rates)
        input_cost = result.usage.input_tokens * 0.000003
        output_cost = result.usage.output_tokens * 0.000015
        
        # Update state (would need proper state management)
        print(f"Cost: ${input_cost + output_cost:.4f}")
        
        return result
```

## Error Handling and Retry Logic

### Tool Execution Errors

```python
from langchain_core.tools import tool

@tool
def robust_search(query: str) -> str:
    """Search with automatic retry and fallback"""
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            result = search_api.search(query)
            return result
        except RateLimitError:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
                continue
            return "Rate limit exceeded. Please try again later."
        except Exception as e:
            if attempt < max_retries - 1:
                continue
            return f"Search failed after {max_retries} attempts: {str(e)}"
```

### Agent-Level Error Handling

```python
def safe_invoke(agent, input_data, config):
    """Wrapper for agent invocation with error handling"""
    max_attempts = 2
    
    for attempt in range(max_attempts):
        try:
            result = agent.invoke(input_data, config=config)
            return {"success": True, "result": result}
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_attempts - 1:
                # Modify input for retry
                input_data["messages"].append({
                    "role": "system",
                    "content": f"Previous attempt failed: {e}. Please try a different approach."
                })
                continue
            return {"success": False, "error": str(e)}
```

## Performance Optimization

### Prompt Caching (Anthropic)

Enabled by default for Anthropic models. Optimize by:

```python
system_prompt = """
[Long unchanging instructions...]
[Best practices...]
[Tool descriptions...]

--- 

[Task-specific instructions that change frequently]
"""
```

Cache boundary typically at 1024+ tokens. Put static content first.

### Parallel Sub-Agent Invocation

```python
import asyncio
from deepagents import async_create_deep_agent

async def parallel_research(agent, topics):
    """Research multiple topics in parallel"""
    tasks = [
        agent.ainvoke({
            "messages": [{
                "role": "user",
                "content": f"Research {topic}"
            }]
        })
        for topic in topics
    ]
    
    results = await asyncio.gather(*tasks)
    return results

# Usage
agent = async_create_deep_agent(...)
results = asyncio.run(parallel_research(agent, ["topic1", "topic2", "topic3"]))
```

### Streaming for Responsiveness

```python
async def stream_agent_response(agent, user_input):
    """Stream agent output for better UX"""
    async for event in agent.astream_events(
        {"messages": [{"role": "user", "content": user_input}]},
        version="v1"
    ):
        if event["event"] == "on_chat_model_stream":
            # Stream token by token
            yield event["data"]["chunk"].content
        elif event["event"] == "on_tool_start":
            # Show tool being called
            yield f"\n[Using tool: {event['name']}]\n"
```

## Testing Deep Agents

### Unit Testing Tools

```python
import pytest

def test_search_tool():
    result = internet_search("test query", max_results=2)
    assert isinstance(result, dict)
    assert "results" in result
    assert len(result["results"]) <= 2

def test_code_execution():
    code = "print('hello')"
    result = run_python_code(code)
    assert "hello" in result.lower()
```

### Integration Testing Agents

```python
def test_research_agent():
    agent = create_research_agent()
    
    result = agent.invoke({
        "messages": [{
            "role": "user",
            "content": "Quick research on Python"
        }]
    })
    
    final_msg = result["messages"][-1].content
    assert len(final_msg) > 100  # Substantive response
    assert "python" in final_msg.lower()
```

### Mocking Sub-Agents

```python
class MockSubAgent:
    """Mock sub-agent for testing"""
    def invoke(self, input_data):
        return {
            "messages": [{
                "role": "assistant",
                "content": "Mock response"
            }]
        }

def test_main_agent_logic():
    # Test main agent orchestration without invoking real sub-agents
    agent = create_agent_with_mocked_subagents()
    ...
```

## Deployment Patterns

### Docker Container

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "agent_server.py"]
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: deepagent-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: deepagent
  template:
    metadata:
      labels:
        app: deepagent
    spec:
      containers:
      - name: deepagent
        image: your-registry/deepagent:latest
        env:
        - name: ANTHROPIC_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-keys
              key: anthropic
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
```

### Serverless (AWS Lambda example)

```python
import json
from deepagents import create_deep_agent

# Initialize agent outside handler for reuse
agent = create_deep_agent(...)

def lambda_handler(event, context):
    """AWS Lambda handler"""
    body = json.loads(event['body'])
    
    result = agent.invoke({
        "messages": [{"role": "user", "content": body['query']}]
    })
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'response': result["messages"][-1].content
        })
    }
```
