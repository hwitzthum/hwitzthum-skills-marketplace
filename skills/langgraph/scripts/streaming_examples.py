#!/usr/bin/env python3
"""
Streaming Example

This script demonstrates different streaming modes in LangGraph:
- Stream state updates after each node
- Stream LLM tokens as they're generated
- Stream custom data from tools
"""

import asyncio
from typing import TypedDict
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.config import get_stream_writer
from langgraph.prebuilt import create_react_agent


def stream_state_updates(agent):
    """
    Stream state updates after each node execution.
    
    Args:
        agent: Compiled LangGraph agent
    """
    print("=== Streaming State Updates ===\n")
    
    for chunk in agent.stream(
        {"messages": [HumanMessage(content="What is 2+2?")]},
        stream_mode="updates"
    ):
        print(f"Update: {chunk}")
        print()


async def stream_llm_tokens(agent):
    """
    Stream LLM tokens as they're generated.
    
    Args:
        agent: Compiled LangGraph agent
    """
    print("\n=== Streaming LLM Tokens ===\n")
    
    async for token, metadata in agent.astream(
        {"messages": [HumanMessage(content="Write a short joke")]},
        stream_mode="messages"
    ):
        # Print tokens as they arrive
        if hasattr(token, 'content') and token.content:
            print(token.content, end="", flush=True)
    
    print("\n")


async def stream_custom_data():
    """Stream custom data from within nodes and tools."""
    print("\n=== Streaming Custom Data ===\n")
    
    # Define a tool that streams progress
    def process_data(data: str) -> str:
        """Process data with progress updates."""
        writer = get_stream_writer()
        
        steps = ["Loading data", "Processing", "Analyzing", "Complete"]
        for i, step in enumerate(steps):
            writer(f"Step {i+1}/{len(steps)}: {step}")
        
        return f"Processed: {data}"
    
    # Create simple graph with custom streaming
    class State(TypedDict):
        input: str
        output: str
    
    def node(state: State):
        writer = get_stream_writer()
        writer("Starting processing...")
        result = process_data(state["input"])
        writer("Finished processing!")
        return {"output": result}
    
    workflow = StateGraph(State)
    workflow.add_node("process", node)
    workflow.add_edge(START, "process")
    workflow.add_edge("process", END)
    graph = workflow.compile()
    
    # Stream with custom mode
    async for chunk in graph.astream(
        {"input": "test data"},
        stream_mode="custom"
    ):
        print(f"Custom update: {chunk}")


async def stream_multiple_modes(agent):
    """
    Stream multiple types of data simultaneously.
    
    Args:
        agent: Compiled LangGraph agent
    """
    print("\n=== Streaming Multiple Modes ===\n")
    
    async for stream_mode, chunk in agent.astream(
        {"messages": [HumanMessage(content="What's the weather?")]},
        stream_mode=["updates", "messages"]
    ):
        print(f"[{stream_mode}] {chunk}\n")


# Example usage
if __name__ == "__main__":
    from langchain_openai import ChatOpenAI
    from langchain_core.tools import tool
    
    @tool
    def calculator(operation: str) -> str:
        """Perform basic math operations."""
        try:
            return str(eval(operation))
        except:
            return "Invalid operation"
    
    # Create agent with streaming-enabled model
    model = ChatOpenAI(model="gpt-4o-mini", temperature=0, streaming=True)
    agent = create_react_agent(model, [calculator])
    
    # Demonstrate different streaming modes
    print("LangGraph Streaming Examples")
    print("=" * 50)
    
    # Sync streaming
    stream_state_updates(agent)
    
    # Async streaming
    asyncio.run(stream_llm_tokens(agent))
    asyncio.run(stream_custom_data())
    asyncio.run(stream_multiple_modes(agent))
