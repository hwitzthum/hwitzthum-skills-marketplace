#!/usr/bin/env python3
"""
Multi-Agent Supervisor Pattern

This script demonstrates how to create a supervisor agent that coordinates
multiple specialized agents in a hierarchical system.
"""

from typing import Annotated, Literal, TypedDict
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.types import Command
from langgraph.prebuilt import create_react_agent


class SupervisorState(MessagesState):
    """State that includes routing information."""
    next: str


def create_supervisor_node(llm, members: list[str]):
    """
    Create a supervisor node that routes to different agents.
    
    Args:
        llm: Language model for decision making
        members: List of agent names to route to
        
    Returns:
        Supervisor node function
    """
    options = ["FINISH"] + members
    
    system_prompt = (
        f"You are a supervisor tasked with managing a conversation between the"
        f" following workers: {members}. Given the following user request,"
        " respond with the worker to act next. Each worker will perform a"
        " task and respond with their results and status. When finished,"
        " respond with FINISH."
    )
    
    class Router(TypedDict):
        """Router output schema."""
        next: Literal[*options]
    
    def supervisor_node(state: SupervisorState) -> Command:
        """Route to the next agent or finish."""
        messages = [
            SystemMessage(content=system_prompt),
        ] + state["messages"]
        
        response = llm.with_structured_output(Router).invoke(messages)
        goto = response["next"]
        
        if goto == "FINISH":
            goto = END
            
        return Command(goto=goto, update={"next": goto})
    
    return supervisor_node


def create_multi_agent_system(llm, agents: dict, supervisor_name: str = "supervisor"):
    """
    Create a multi-agent system with a supervisor.
    
    Args:
        llm: Language model for the supervisor
        agents: Dictionary mapping agent names to agent graphs/functions
        supervisor_name: Name for the supervisor node
        
    Returns:
        Compiled multi-agent graph
    """
    workflow = StateGraph(SupervisorState)
    
    # Add agent nodes
    for name, agent in agents.items():
        workflow.add_node(name, agent)
    
    # Add supervisor node
    member_names = list(agents.keys())
    supervisor = create_supervisor_node(llm, member_names)
    workflow.add_node(supervisor_name, supervisor)
    
    # Connect supervisor to agents
    for member in member_names:
        workflow.add_edge(member, supervisor_name)
    
    # Set entry point
    workflow.add_edge(START, supervisor_name)
    
    return workflow.compile()


# Example usage
if __name__ == "__main__":
    from langchain_openai import ChatOpenAI
    from langchain_core.tools import tool
    
    # Define tools for different agents
    @tool
    def search_web(query: str) -> str:
        """Search the web for information."""
        return f"Search results for: {query}"
    
    @tool
    def analyze_data(data: str) -> str:
        """Analyze data and provide insights."""
        return f"Analysis of: {data}"
    
    # Create models
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    
    # Create specialized agents
    search_agent = create_react_agent(llm, [search_web])
    analysis_agent = create_react_agent(llm, [analyze_data])
    
    # Create agent nodes that work with SupervisorState
    def search_node(state: SupervisorState):
        result = search_agent.invoke(state)
        return {"messages": result["messages"]}
    
    def analysis_node(state: SupervisorState):
        result = analysis_agent.invoke(state)
        return {"messages": result["messages"]}
    
    # Create multi-agent system
    agents = {
        "search_agent": search_node,
        "analysis_agent": analysis_node,
    }
    
    system = create_multi_agent_system(llm, agents)
    
    # Run the system
    result = system.invoke({
        "messages": [HumanMessage(content="Search for LangGraph info and analyze it")]
    })
    
    print("Multi-agent execution complete")
    print(f"Final messages: {len(result['messages'])}")
