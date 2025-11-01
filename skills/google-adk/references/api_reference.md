# ADK API Reference

Detailed API specifications for Google Agent Development Kit components.

## Core Agent Classes

### BaseAgent

Foundation class for all agents in ADK.

**Key Methods:**
- `run(message: str)` - Execute agent with input message
- `async_run(message: str)` - Asynchronous execution

### Agent / LlmAgent

LLM-powered agent for reasoning and dynamic decision-making.

**Constructor Parameters:**
```python
Agent(
    name: str,              # Required: Agent identifier
    model: str,             # Required: Model ID (e.g., "gemini-2.0-flash")
    instruction: str,       # Agent behavior instructions
    description: str,       # Agent purpose (for multi-agent delegation)
    tools: List[Tool],      # Tools available to agent
    sub_agents: List[Agent], # Child agents for delegation
    generate_content_config: GenerateContentConfig  # Model configuration
)
```

**Java Builder:**
```java
LlmAgent.builder()
    .name(String)
    .model(String)
    .instruction(String)
    .description(String)
    .tools(FunctionTool...)
    .build()
```

### SequentialAgent

Executes agents in defined sequence.

```python
SequentialAgent(
    name: str,
    description: str,
    agents: List[Agent]  # Agents executed in order
)
```

### ParallelAgent

Executes multiple agents simultaneously.

```python
ParallelAgent(
    name: str,
    description: str,
    agents: List[Agent]  # Agents run in parallel
)
```

### LoopAgent

Iteratively executes an agent.

```python
LoopAgent(
    name: str,
    description: str,
    agent: Agent,
    max_iterations: int  # Maximum loop count
)
```

## Tools

### Pre-built Tools

```python
from google.adk.tools import (
    google_search,              # Web search capability
    built_in_code_execution,    # Execute Python code
    PreloadMemoryTool,          # Memory retrieval
    AgentEngineSandboxCodeExecutor  # Secure code execution
)
```

### Custom Function Tools

**Python:**
Define regular Python functions with type hints and docstrings:

```python
def tool_name(param: str, value: int = 0) -> dict:
    """Tool description shown to LLM.
    
    Args:
        param: Parameter description
        value: Optional parameter with default
        
    Returns:
        Dictionary with result
    """
    return {"result": "value"}
```

**Java:**
Use `@Schema` annotations for parameter documentation:

```java
public static Map<String, String> toolName(
    @Schema(name = "param", description = "Parameter description") String param,
    @Schema(name = "value", description = "Value description") int value
) {
    return Map.of("result", "value");
}

// Register with FunctionTool
FunctionTool.create(ClassName.class, "toolName")
```

## Runner and Session Management

### InMemoryRunner

Manages agent execution locally.

**Python:**
```python
from google.adk.runner import InMemoryRunner

runner = InMemoryRunner(agent)

# Create session
session = runner.session_service().create_session(
    agent_name="my_agent",
    user_id="user-123"
).blocking_get()

# Run agent
events = runner.run(user_id, session.id(), message_content)

# Async execution
async for event in runner.run_async(user_id, session.id(), message):
    process_event(event)
```

**Java:**
```java
import com.google.adk.runner.InMemoryRunner;
import com.google.adk.sessions.Session;

InMemoryRunner runner = new InMemoryRunner(agent);

Session session = runner
    .sessionService()
    .createSession(agentName, userId)
    .blockingGet();

Flowable<Event> events = runner.runAsync(userId, session.id(), content);
```

## Model Configuration

### GenerateContentConfig

Advanced model parameter configuration.

```python
from google.genai import types

config = types.GenerateContentConfig(
    temperature=0.7,           # Randomness (0-1)
    max_output_tokens=2000,    # Response length limit
    top_p=0.95,               # Nucleus sampling
    top_k=40,                 # Top-k sampling
    safety_settings=[...],     # Content filtering
    stop_sequences=[...]       # Generation stops
)
```

### Safety Settings

```python
from google.genai import types

safety_settings = [
    types.SafetySetting(
        category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
        threshold=types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
    )
]
```

**Categories:**
- `HARM_CATEGORY_HARASSMENT`
- `HARM_CATEGORY_HATE_SPEECH`
- `HARM_CATEGORY_SEXUALLY_EXPLICIT`
- `HARM_CATEGORY_DANGEROUS_CONTENT`

**Thresholds:**
- `BLOCK_NONE`
- `BLOCK_LOW_AND_ABOVE`
- `BLOCK_MEDIUM_AND_ABOVE`
- `BLOCK_HIGH_AND_ABOVE`

## Evaluation

### AgentEvaluator

Systematic agent performance assessment.

```python
from google.adk.evaluation import AgentEvaluator

evaluator = AgentEvaluator()

# Evaluate against test set
results = evaluator.evaluate(
    agent=my_agent,
    eval_set=evaluation_data,
    metrics=['response_quality', 'trajectory_correctness']
)
```

### Evaluation Set Format

```json
{
  "name": "agent_test_suite",
  "test_cases": [
    {
      "user_message": "Input query",
      "expected_trajectory": ["tool1", "tool2"],
      "expected_response_contains": ["keyword1", "keyword2"]
    }
  ]
}
```

## CLI Commands

```bash
# Web UI
adk web [--port PORT] [--no-reload]

# Terminal interaction
adk run [--agent-path PATH]

# API server
adk api_server [--port PORT]

# Evaluation
adk eval <agent_path> <evalset_path>

# Version info
adk version
```

## Environment Variables

```bash
# Google AI Studio
GOOGLE_API_KEY=your_key

# Vertex AI
GOOGLE_GENAI_USE_VERTEXAI=TRUE
GOOGLE_CLOUD_PROJECT=project_id
GOOGLE_CLOUD_LOCATION=us-central1

# Optional
ADK_LOG_LEVEL=INFO
ADK_DEV_UI_PORT=8000
```

## Model IDs

**Gemini Models:**
- `gemini-2.0-flash` - Fast, efficient
- `gemini-2.0-flash-exp` - Experimental with Live API
- `gemini-2.5-flash` - Latest generation
- `gemini-1.5-pro` - Previous generation

**Via LiteLLM:**
- `gpt-4o` - OpenAI GPT-4o
- `claude-3-5-sonnet` - Anthropic Claude
- `mistral-large` - Mistral AI

## Best Practices

1. **Tool Design**: Keep tools focused, single-purpose
2. **Error Handling**: Return structured error objects from tools
3. **Docstrings**: Provide clear, detailed tool documentation
4. **Type Hints**: Use Python type hints for better LLM understanding
5. **Testing**: Create evaluation sets early in development
6. **Context Management**: Be mindful of token limits in conversations
