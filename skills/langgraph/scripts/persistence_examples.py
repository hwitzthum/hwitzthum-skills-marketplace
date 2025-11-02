#!/usr/bin/env python3
"""
Persistence and Checkpointing Example

This script demonstrates how to use checkpointers for:
- Conversation memory across sessions
- Human-in-the-loop workflows
- Error recovery and resumption
- Time travel debugging
"""

from typing import TypedDict
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.prebuilt import create_react_agent


def demonstrate_conversation_memory():
    """Show how checkpointers enable conversation memory."""
    print("=== Conversation Memory Example ===\n")
    
    from langchain_openai import ChatOpenAI
    
    model = ChatOpenAI(model="gpt-4o-mini")
    
    # Create agent with checkpointer
    checkpointer = InMemorySaver()
    agent = create_react_agent(
        model=model,
        tools=[],
        checkpointer=checkpointer
    )
    
    # Use the same thread_id for both conversations
    config = {"configurable": {"thread_id": "user-123"}}
    
    # First conversation
    print("First message:")
    result1 = agent.invoke(
        {"messages": [HumanMessage(content="My name is Alice")]},
        config
    )
    print(result1["messages"][-1].content)
    
    print("\nSecond message (remembers context):")
    result2 = agent.invoke(
        {"messages": [HumanMessage(content="What's my name?")]},
        config
    )
    print(result2["messages"][-1].content)
    
    print()


def demonstrate_human_in_the_loop():
    """Show human-in-the-loop with interrupts."""
    print("\n=== Human-in-the-Loop Example ===\n")
    
    from langchain_openai import ChatOpenAI
    from langgraph.checkpoint.memory import InMemorySaver
    
    class State(TypedDict):
        input: str
        draft: str
        approved: bool
        output: str
    
    def create_draft(state: State):
        """Create a draft that requires approval."""
        draft = f"Draft version of: {state['input']}"
        return {"draft": draft, "approved": False}
    
    def wait_for_approval(state: State):
        """This is an interrupt point - execution pauses here."""
        from langgraph.types import interrupt
        # Interrupt and wait for human input
        approved = interrupt("Please approve the draft")
        return {"approved": approved}
    
    def finalize(state: State):
        """Finalize the output after approval."""
        if state["approved"]:
            return {"output": f"Final: {state['draft']}"}
        else:
            return {"output": "Rejected"}
    
    # Build graph with interrupts
    workflow = StateGraph(State)
    workflow.add_node("create_draft", create_draft)
    workflow.add_node("wait_approval", wait_for_approval)
    workflow.add_node("finalize", finalize)
    
    workflow.add_edge(START, "create_draft")
    workflow.add_edge("create_draft", "wait_approval")
    workflow.add_edge("wait_approval", "finalize")
    workflow.add_edge("finalize", END)
    
    checkpointer = InMemorySaver()
    graph = workflow.compile(checkpointer=checkpointer)
    
    config = {"configurable": {"thread_id": "thread-1"}}
    
    # First run - will pause at interrupt
    print("Starting workflow...")
    result = graph.invoke({"input": "Hello World"}, config)
    print(f"Status: {result}")
    
    # Resume with approval
    print("\nResuming with approval...")
    from langgraph.types import Command
    result = graph.invoke(Command(resume=True), config)
    print(f"Final output: {result.get('output')}")


def demonstrate_error_recovery():
    """Show how checkpointers enable error recovery."""
    print("\n=== Error Recovery Example ===\n")
    
    class State(TypedDict):
        step: int
        data: str
    
    def step1(state: State):
        print("Executing step 1...")
        return {"step": 1, "data": "Step 1 complete"}
    
    def step2(state: State):
        print("Executing step 2...")
        return {"step": 2, "data": state["data"] + " -> Step 2 complete"}
    
    def step3(state: State):
        print("Executing step 3...")
        # Simulate error
        if state["step"] == 2:
            raise Exception("Simulated error in step 3")
        return {"step": 3, "data": state["data"] + " -> Step 3 complete"}
    
    workflow = StateGraph(State)
    workflow.add_node("step1", step1)
    workflow.add_node("step2", step2)
    workflow.add_node("step3", step3)
    
    workflow.add_edge(START, "step1")
    workflow.add_edge("step1", "step2")
    workflow.add_edge("step2", "step3")
    workflow.add_edge("step3", END)
    
    # Use SQLite for persistent storage
    checkpointer = SqliteSaver.from_conn_string(":memory:")
    graph = workflow.compile(checkpointer=checkpointer)
    
    config = {"configurable": {"thread_id": "recovery-thread"}}
    
    try:
        print("First attempt (will fail):")
        result = graph.invoke({"step": 0, "data": "Start"}, config)
    except Exception as e:
        print(f"Error occurred: {e}")
    
    print("\nRecovering from last successful checkpoint...")
    # Get the state at the last successful checkpoint
    state = graph.get_state(config)
    print(f"Recovered state: step={state.values['step']}, data={state.values['data']}")


def list_checkpoints():
    """Show how to list and inspect checkpoints."""
    print("\n=== Listing Checkpoints ===\n")
    
    from langchain_openai import ChatOpenAI
    
    model = ChatOpenAI(model="gpt-4o-mini")
    checkpointer = InMemorySaver()
    agent = create_react_agent(model=model, tools=[], checkpointer=checkpointer)
    
    config = {"configurable": {"thread_id": "inspection-thread"}}
    
    # Have a few conversations
    for msg in ["Hello", "How are you?", "Goodbye"]:
        agent.invoke({"messages": [HumanMessage(content=msg)]}, config)
    
    # List all checkpoints for this thread
    print("Checkpoints for thread:")
    for checkpoint_tuple in checkpointer.list(config):
        checkpoint = checkpoint_tuple.checkpoint
        print(f"- Checkpoint ID: {checkpoint['id']}")
        print(f"  Step: {checkpoint.get('step', 'N/A')}")
        print()


# Example usage
if __name__ == "__main__":
    print("LangGraph Persistence Examples")
    print("=" * 50)
    
    demonstrate_conversation_memory()
    demonstrate_human_in_the_loop()
    demonstrate_error_recovery()
    list_checkpoints()
