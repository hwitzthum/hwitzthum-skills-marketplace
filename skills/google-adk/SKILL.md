---
name: google-adk
description: Comprehensive guide for building, evaluating, and deploying AI agents using Google's Agent Development Kit (ADK). Use when creating single agents, multi-agent systems, workflow orchestrations, or deploying agentic applications. Covers Python and Java implementations, tool integration, LLM configuration, evaluation frameworks, and deployment to Vertex AI Agent Engine, Cloud Run, or containers.
---

# Google Agent Development Kit (ADK)

Build production-ready AI agents with Google's Agent Development Kit - a flexible, code-first framework for creating, orchestrating, evaluating, and deploying sophisticated agentic systems.

## Quick Reference

**Installation:**
```bash
# Python
pip install google-adk

# Java (Maven)
<dependency>
  <groupId>com.google.adk</groupId>
  <artifactId>google-adk</artifactId>
  <version>0.2.0</version>
</dependency>
```

**Basic Agent Structure (Python):**
```python
from google.adk.agents import Agent

root_agent = Agent(
    name="agent_name",
    model="gemini-2.0-flash",
    instruction="Agent behavior instructions",
    description="What this agent does",
    tools=[function1, function2]
)
```

## Core Concepts

### Agent Types

ADK provides three agent categories:

1. **LLM Agents** (`Agent`, `LlmAgent`) - Use LLMs for reasoning, planning, and dynamic decision-making
2. **Workflow Agents** (`SequentialAgent`, `ParallelAgent`, `LoopAgent`) - Deterministic execution patterns without LLM overhead
3. **Custom Agents** - Extend `BaseAgent` for specialized logic

### Key Components

- **Agent**: Self-contained execution unit with specific capabilities
- **Tool**: Functions or capabilities agents can invoke (custom functions, pre-built tools, OpenAPI specs, MCP tools, or other agents)
- **Runner**: Execution engine managing agent interactions and event flow
- **Session**: Maintains conversation state and history
- **Event**: Communication units representing actions (messages, tool calls, responses)

## Agent Creation Workflow

### 1. Environment Setup

**Python:**
```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# or .venv\Scripts\activate.bat on Windows

# Install ADK
pip install google-adk
```

**Java:**
```xml
<!-- Add to pom.xml -->
<dependency>
  <groupId>com.google.adk</groupId>
  <artifactId>google-adk</artifactId>
  <version>0.2.0</version>
</dependency>
```

### 2. Configure Authentication

Create `.env` file in project directory:

**For Google AI Studio:**
```bash
GOOGLE_API_KEY=your_api_key_here
```

**For Vertex AI:**
```bash
GOOGLE_GENAI_USE_VERTEXAI=TRUE
GOOGLE_CLOUD_PROJECT=your_project_id
GOOGLE_CLOUD_LOCATION=us-central1
```

Run `gcloud auth login` before starting.

### 3. Define Tools

Tools give agents capabilities beyond conversation:

**Python function tool:**
```python
def get_weather(city: str) -> dict:
    """Retrieves weather for a city.
    
    Args:
        city: City name
        
    Returns:
        dict with status and report or error
    """
    # Implementation
    return {"status": "success", "report": "Weather data"}
```

**Java function tool:**
```java
public static Map<String, String> getWeather(
    @Schema(name = "city", description = "City name") String city) {
    return Map.of("status", "success", "report", "Weather data");
}
```

**Pre-built tools:**
```python
from google.adk.tools import google_search, built_in_code_execution

agent = Agent(
    name="search_agent",
    model="gemini-2.0-flash",
    tools=[google_search, built_in_code_execution]
)
```

### 4. Create Agent

**Basic LLM Agent (Python):**
```python
from google.adk.agents import Agent

agent = Agent(
    name="assistant",
    model="gemini-2.0-flash",
    instruction="You are a helpful assistant",
    description="Assists with general queries",
    tools=[tool1, tool2]
)
```

**Basic LLM Agent (Java):**
```java
import com.google.adk.agents.LlmAgent;
import com.google.adk.tools.FunctionTool;

BaseAgent agent = LlmAgent.builder()
    .name("assistant")
    .model("gemini-2.0-flash")
    .instruction("You are a helpful assistant")
    .description("Assists with general queries")
    .tools(
        FunctionTool.create(MyClass.class, "tool1"),
        FunctionTool.create(MyClass.class, "tool2")
    )
    .build();
```

### 5. Run Agent Locally

**Dev UI (recommended for development):**
```bash
# Python
adk web

# Java
mvn exec:java \
  -Dexec.mainClass="com.google.adk.web.AdkWebServer" \
  -Dexec.args="--adk.agents.source-dir=src/main/java"
```

**Terminal:**
```bash
# Python
adk run

# Java - implement main() method with InMemoryRunner
```

**API Server:**
```bash
adk api_server  # Creates local FastAPI server for testing
```

## Multi-Agent Systems

Build hierarchical agent systems where agents delegate to specialized sub-agents:

**Python:**
```python
from google.adk.agents import Agent

# Specialized agents
greeter = Agent(
    name="greeter",
    model="gemini-2.0-flash",
    instruction="Greet users warmly",
    description="Handles greetings and introductions"
)

task_executor = Agent(
    name="executor",
    model="gemini-2.0-flash",
    instruction="Execute tasks efficiently",
    description="Handles task execution"
)

# Coordinator with sub-agents
coordinator = Agent(
    name="coordinator",
    model="gemini-2.0-flash",
    instruction="Route requests to appropriate agents",
    description="Coordinates between greeter and executor",
    sub_agents=[greeter, task_executor]
)
```

**Agent Transfer:** LLM-driven dynamic routing allows agents to automatically transfer control to appropriate sub-agents based on request content and agent descriptions.

## Workflow Orchestration

Use workflow agents for deterministic, predictable execution patterns:

**Sequential Agent:**
```python
from google.adk.agents import SequentialAgent

workflow = SequentialAgent(
    name="pipeline",
    description="Executes agents in sequence",
    agents=[agent1, agent2, agent3]
)
```

**Parallel Agent:**
```python
from google.adk.agents import ParallelAgent

workflow = ParallelAgent(
    name="parallel_tasks",
    description="Runs agents simultaneously",
    agents=[agent1, agent2, agent3]
)
```

**Loop Agent:**
```python
from google.adk.agents import LoopAgent

workflow = LoopAgent(
    name="iterative_process",
    description="Repeats agent execution",
    agent=processing_agent,
    max_iterations=10
)
```

## Model Configuration

**Supported Models:**
- Gemini models (recommended): `gemini-2.0-flash`, `gemini-2.5-flash`
- Model-agnostic: Supports various LLMs via LiteLLM integration

**Advanced Configuration:**
```python
from google.genai import types

safety_settings = [
    types.SafetySetting(
        category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
        threshold=types.HarmBlockThreshold.OFF
    )
]

generate_config = types.GenerateContentConfig(
    safety_settings=safety_settings,
    temperature=0.7,
    max_output_tokens=2000,
    top_p=0.95
)

agent = Agent(
    name="configured_agent",
    model="gemini-2.0-flash",
    generate_content_config=generate_config,
    tools=[...]
)
```

## Memory and State Management

**Session Management:**
```python
from google.adk.runner import InMemoryRunner
from google.adk.sessions import Session

runner = InMemoryRunner(agent)
session = runner.session_service().create_session(
    agent_name="my_agent",
    user_id="user-123"
).blocking_get()
```

**Memory Tools:**
```python
from google.adk.tools import PreloadMemoryTool

agent = Agent(
    name="stateful_agent",
    model="gemini-2.0-flash",
    instruction="Use past interactions to personalize responses",
    tools=[PreloadMemoryTool()]
)
```

**Session Rewind:**
```python
# Rewind to previous state
runner.rewind_session(session_id, steps_back=2)
```

## Evaluation

Systematically assess agent performance before deployment.

**Create Evaluation Set:**

Use Dev UI to generate evaluation datasets from actual agent interactions, or create manually:

```json
{
  "name": "weather_agent_tests",
  "test_cases": [
    {
      "user_message": "What's the weather in New York?",
      "expected_trajectory": ["get_weather"],
      "expected_response_contains": ["New York", "weather"]
    }
  ]
}
```

**Run Evaluation:**

```bash
# CLI
adk eval path/to/agent path/to/evalset.json

# Programmatic (pytest)
from google.adk.evaluation import AgentEvaluator

evaluator = AgentEvaluator()
results = evaluator.evaluate(agent, eval_set)
```

**Evaluation Metrics:**
- Response quality (coherence, grounding, safety)
- Trajectory correctness (tool usage, execution path)
- Hallucination detection
- Safety compliance

## Deployment

### Vertex AI Agent Engine (Recommended)

**Python:**
```python
from vertexai.agent_engines import AdkApp

app = AdkApp(agent=agent)

# Test locally
async for event in app.async_stream_query(
    user_id="user-123",
    message="Test query"
):
    print(event)
```

**Deploy:**
```bash
# Deploy to Vertex AI Agent Engine Runtime
# Provides fully managed auto-scaling service
```

### Cloud Run

```bash
# Create Dockerfile
# Build and deploy container
gcloud run deploy agent-service \
  --source . \
  --region us-central1
```

### Docker/Custom Infrastructure

```bash
# Build container
docker build -t my-agent .

# Run locally
docker run -p 8000:8000 my-agent

# Deploy to any container platform
```

## Advanced Features

### Streaming

**Bidirectional audio/video streaming:**
```python
# Configure for Live API
agent = Agent(
    name="voice_agent",
    model="gemini-2.0-flash-exp",  # Model with Live API support
    instruction="Respond naturally to voice input"
)
```

Enable microphone in Dev UI for voice interactions.

### Code Execution

**Built-in sandbox:**
```python
from google.adk.tools import built_in_code_execution

agent = Agent(
    name="coding_agent",
    model="gemini-2.0-flash",
    tools=[built_in_code_execution]
)
```

**Vertex AI Sandbox:**
```python
from google.adk.tools import AgentEngineSandboxCodeExecutor

code_executor = AgentEngineSandboxCodeExecutor()
agent = Agent(
    name="secure_coder",
    model="gemini-2.0-flash",
    tools=[code_executor]
)
```

### Integration with Other Frameworks

**LangChain, CrewAI, LlamaIndex:**
```python
# Use ADK agents as tools in other frameworks
# Or integrate external framework tools into ADK
from langchain.tools import Tool

# Wrap ADK agent for use elsewhere
langchain_tool = Tool(
    name="adk_agent",
    func=agent.run,
    description="ADK agent functionality"
)
```

### A2A Protocol (Agent-to-Agent)

Enable remote agent communication:

```python
# Agent exposes A2A-compatible endpoint
# Other agents can discover and invoke remotely
```

## Project Structure

**Python:**
```
project/
├── .env                    # Environment configuration
├── agent_name/
│   ├── __init__.py
│   └── agent.py           # Agent definition
└── tests/
    └── test_agent.py      # Evaluation tests
```

**Java:**
```
project/
├── pom.xml
├── src/
│   ├── main/
│   │   └── java/
│   │       └── agents/
│   │           └── AgentClass.java
│   └── test/
│       └── java/
│           └── AgentTest.java
```

## Best Practices

1. **Clear Instructions**: Write specific, actionable agent instructions
2. **Tool Documentation**: Provide detailed docstrings for custom tools with Args and Returns
3. **Test Locally First**: Use Dev UI to debug before deployment
4. **Evaluate Rigorously**: Create comprehensive test cases covering edge cases
5. **Start Simple**: Begin with single agents, add complexity gradually
6. **Monitor Trajectories**: Use trace logs to understand agent decision-making
7. **Manage Context**: Use clear agent descriptions for proper delegation in multi-agent systems
8. **Security**: Implement proper authentication and follow safety guidelines

## Debugging

**Dev UI Trace Tab:**
- Hover over trace rows to highlight corresponding chat messages
- Click rows to inspect Event, Request, Response, and Graph views
- Blue rows indicate event generation
- View tool call sequences and agent logic flow

**Common Issues:**
- **Agent not in dropdown**: Ensure `adk web` runs in parent folder
- **Authentication errors**: Verify `.env` configuration and `gcloud auth login`
- **Tool not executing**: Check function signatures and docstrings
- **Transfer not working**: Verify sub-agent descriptions are specific

## Resources

- **Documentation**: https://google.github.io/adk-docs/
- **GitHub (Python)**: https://github.com/google/adk-python
- **API Reference**: https://google.github.io/adk-docs/api-reference/
- **Vertex AI Docs**: https://cloud.google.com/vertex-ai/generative-ai/docs/agent-development-kit/
- **Video Tutorial**: "Introducing Agent Development Kit" on YouTube

For detailed API specifications and advanced patterns, see `references/api_reference.md`.
