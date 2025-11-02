# DeepAgent Skill - Quick Reference Guide

## What You're Getting

A complete, production-ready skill for building sophisticated AI agents using LangChain's DeepAgents framework.

## Installation

Simply upload the `deepagent.skill` file to Claude through the Skills menu. The skill will automatically activate when you need to build or work with deep agents.

## What This Skill Enables

### 1. Quick Agent Creation
Ask Claude: "Create a research agent using DeepAgents that can search the web and write reports"

Claude will use the skill to:
- Provide the exact code structure
- Configure proper tools and middleware
- Set up sub-agents for specialized tasks
- Include best practices for prompts

### 2. Advanced Configurations
Ask Claude: "Show me how to add human-in-the-loop approval to my DeepAgent"

Claude will reference:
- Complete API documentation
- Working code examples
- Configuration patterns
- Error handling approaches

### 3. Production Deployment
Ask Claude: "Help me deploy my DeepAgent to production with persistence"

Claude will provide:
- Database configuration for checkpointing
- Memory management strategies
- Docker/Kubernetes deployment configs
- Monitoring and optimization tips

### 4. Troubleshooting
Ask Claude: "My DeepAgent is running out of context - how do I fix this?"

Claude will suggest:
- Filesystem tools for context management
- Sub-agent delegation patterns
- Automatic tool result eviction
- Memory strategies

## Skill Contents Overview

### Main Documentation (SKILL.md)
- Core concepts and quick start
- Architecture overview
- Planning, filesystem, and sub-agent systems
- Design patterns and best practices
- ~450 lines of essential guidance

### Working Examples (scripts/)
1. **research_agent.py** - Complete research agent with web search, citations, and critique workflow
2. **coding_agent.py** - Complete coding agent with execution, testing, and file management

### Detailed References (references/)
1. **api_reference.md** - Complete API documentation with signatures, parameters, and examples
2. **advanced_config.md** - Production patterns, optimization, deployment strategies

## Common Use Cases

### Research Agent
```
"Create a DeepAgent that researches topics, uses multiple sources, 
provides proper citations, and has a quality review process"
```

### Coding Agent
```
"Build a DeepAgent that writes Python code, tests it automatically,
organizes files, and persists project context"
```

### Analysis Agent
```
"Create a DeepAgent with specialized sub-agents for data analysis,
visualization, and report generation"
```

### Custom Workflow
```
"I need an agent that does X, then delegates Y to a specialist,
saves results to files, and iterates until quality is met"
```

## Key Features You Can Request

✅ **Planning Tools** - TODO lists for complex task decomposition  
✅ **Virtual Filesystem** - Context management and artifact storage  
✅ **Sub-Agents** - Hierarchical delegation with context isolation  
✅ **Human-in-the-Loop** - Approval workflows for sensitive operations  
✅ **Custom Middleware** - Extend with your own capabilities  
✅ **MCP Integration** - Use Model Context Protocol tools  
✅ **Memory Management** - Ephemeral and persistent storage options  
✅ **Performance Optimization** - Caching, streaming, model selection  

## Example Conversation Starters

**For Beginners:**
- "What is DeepAgents and how does it differ from regular LangChain agents?"
- "Show me the simplest possible DeepAgent example"
- "Walk me through creating my first research agent"

**For Intermediate Users:**
- "How do I add sub-agents to handle specialized tasks?"
- "What's the best way to manage context in long-running agents?"
- "Show me how to use the filesystem tools effectively"

**For Advanced Users:**
- "Help me design a multi-stage pipeline with parallel sub-agents"
- "What are the best practices for production deployment with persistence?"
- "How can I optimize costs by using different models for different sub-agents?"

**For Troubleshooting:**
- "My agent keeps running out of context - what should I do?"
- "How do I prevent my agent from calling the same tool repeatedly?"
- "My sub-agent isn't working as expected - help me debug"

## Why This Skill Is Valuable

1. **Comprehensive** - Covers everything from basics to production deployment
2. **Practical** - Includes working code you can run immediately
3. **Current** - Based on latest DeepAgents architecture (0.2+ release)
4. **Proven** - Patterns from real implementations (Claude Code, Deep Research, etc.)
5. **Production-Ready** - Includes error handling, optimization, and deployment strategies

## What Makes DeepAgents Special

Unlike simple tool-calling agents, DeepAgents can:
- **Plan** complex tasks using explicit TODO lists
- **Remember** using a virtual filesystem for artifacts
- **Delegate** to specialized sub-agents with isolated context
- **Sustain** reasoning over long time horizons
- **Manage** context automatically to avoid limitations

This skill gives Claude comprehensive knowledge to help you leverage all these capabilities effectively.

## Getting Started

1. Upload `deepagent.skill` to Claude
2. Start with a simple question like: "Show me a basic DeepAgent example"
3. Build from there based on your needs
4. Reference the scripts for working code
5. Check references for advanced patterns

## Support & Resources

The skill includes:
- Detailed error handling patterns
- Common pitfalls and solutions
- Performance optimization techniques
- Testing strategies
- Deployment configurations

Claude can help you with any aspect by referencing the appropriate section of the skill documentation.

---

**Ready to build sophisticated AI agents?** Just ask Claude - the skill will guide the way!
