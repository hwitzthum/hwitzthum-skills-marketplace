#!/usr/bin/env python3
"""
Basic ReAct Agent Example

This script demonstrates creating a simple ReAct (Reasoning and Action) agent
with LangGraph. It shows the fundamental pattern of tool-calling agents.
"""

from typing import Annotated, TypedDict, Sequence
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition


# Define State
class AgentState(TypedDict):
    """The state of the agent."""
    messages: Annotated[Sequence[BaseMessage], add_messages]


def create_basic_react_agent(model, tools, system_prompt: str = "You are a helpful assistant"):
    """
    Create a basic ReAct agent with the given model and tools.
    
    Args:
        model: A chat model that supports tool calling
        tools: List of tools the agent can use
        system_prompt: System prompt for the agent
        
    Returns:
        Compiled graph ready to execute
    """
    # Bind tools to model
    model_with_tools = model.bind_tools(tools)
    
    # Define the node that calls the model
    def call_model(state: AgentState):
        messages = state["messages"]
        # Add system prompt if this is the first call
        if not any(m.type == "system" for m in messages):
            messages = [{"role": "system", "content": system_prompt}] + list(messages)
        response = model_with_tools.invoke(messages)
        return {"messages": [response]}
    
    # Create tool node
    tool_node = ToolNode(tools)
    
    # Build the graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", tool_node)
    
    # Set entry point
    workflow.add_edge(START, "agent")
    
    # Add conditional edge from agent
    workflow.add_conditional_edges(
        "agent",
        tools_condition,  # Determines if we call tools or end
    )
    
    # Add edge from tools back to agent
    workflow.add_edge("tools", "agent")
    
    return workflow.compile()


# Example usage
if __name__ == "__main__":
    from langchain_openai import ChatOpenAI
    from langchain_core.tools import tool
    
    # Define a simple tool
    @tool
    def get_weather(city: str) -> str:
        """Get the weather for a given city."""
        return f"It's always sunny in {city}!"
    
    # Create model
    model = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    
    # Create agent
    agent = create_basic_react_agent(
        model=model,
        tools=[get_weather],
        system_prompt="You are a helpful weather assistant"
    )
    
    # Run the agent
    result = agent.invoke({
        "messages": [HumanMessage(content="What's the weather in San Francisco?")]
    })
    
    print("Final response:")
    print(result["messages"][-1].content)
