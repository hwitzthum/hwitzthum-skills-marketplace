"""
Research Agent Example - DeepAgents Framework

This script demonstrates building a sophisticated research agent with:
- Internet search capability
- Specialized research sub-agent for deep dives
- Critique sub-agent for quality review
- Proper citation handling
"""

import os
from typing import Literal
from tavily import TavilyClient
from deepagents import create_deep_agent

# Initialize Tavily client for web search
tavily_client = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY", ""))

def internet_search(
    query: str,
    max_results: int = 5,
    topic: Literal["general", "news", "finance"] = "general",
    include_raw_content: bool = False,
) -> dict:
    """
    Run a web search using Tavily.
    
    Args:
        query: Search query string
        max_results: Maximum number of results to return (default: 5)
        topic: Type of content to search (general, news, or finance)
        include_raw_content: Whether to include full page content
    
    Returns:
        Dictionary containing search results with titles, URLs, and snippets
    """
    search_docs = tavily_client.search(
        query,
        max_results=max_results,
        include_raw_content=include_raw_content,
        topic=topic,
    )
    return search_docs


# Sub-agent prompt for deep research
research_subagent_prompt = """You are a dedicated research specialist.
Your job is to conduct thorough research based on the user's questions.

Conduct comprehensive research using multiple searches when needed.
Only your FINAL answer will be passed back to the main agent.

<Citation Rules>
- Assign each unique URL a single citation number in your text [1], [2], etc.
- End with ### Sources section that lists each source with corresponding numbers
- IMPORTANT: Number sources sequentially without gaps (1,2,3,4...) in the final list
- Each source should be a separate line item in a list
- Example format:
  [1] Source Title: URL
  [2] Source Title: URL
- Citations are critical. Users will use these to investigate further.
</Citation Rules>

You have access to the `internet_search` tool.
Use it multiple times if needed to gather comprehensive information.
"""

# Sub-agent prompt for critique
critique_subagent_prompt = """You are a tough but fair editor and fact-checker.

Your job is to review research reports and provide constructive critique on:
- Accuracy: Are claims properly supported by sources?
- Completeness: Are important aspects missing?
- Clarity: Is the writing clear and well-organized?
- Citations: Are sources properly cited and reliable?

Provide specific, actionable feedback. Be thorough but concise.
"""

# Define specialized sub-agents
research_subagent = {
    "name": "research-agent",
    "description": "Expert at conducting deep research on specific topics with proper citations",
    "system_prompt": research_subagent_prompt,
    "tools": [internet_search],
}

critique_subagent = {
    "name": "critique-agent",
    "description": "Reviews and critiques research reports for accuracy and quality",
    "system_prompt": critique_subagent_prompt,
    "model": "anthropic:claude-3-5-haiku-20241022",  # Fast, efficient model for review
    "temperature": 0,  # Deterministic critique
}

# Main agent instructions
main_agent_instructions = """You are an expert research coordinator.

Your workflow for conducting research:

1. **Plan the research** (use write_todos):
   - Break down the research question into sub-questions
   - Identify what information is needed
   
2. **Delegate research** (use task tool):
   - For each sub-question, delegate to the research-agent sub-agent
   - The research-agent will conduct thorough searches and provide cited answers
   
3. **Synthesize findings** (use write_file):
   - Combine findings from all sub-agents into a cohesive report
   - Save intermediate drafts to files for organization
   
4. **Request critique** (use task tool):
   - Send the draft report to critique-agent for review
   - Review the feedback carefully
   
5. **Finalize report** (use edit_file):
   - Address the critique feedback
   - Refine the report for clarity and completeness
   
6. **Deliver the final report**:
   - Present the polished research to the user
   - Ensure all citations are properly formatted

Use the filesystem tools to organize your work:
- write_file: Save drafts and intermediate findings
- edit_file: Refine content based on feedback
- read_file: Review saved content
- ls: Check what files you have

Remember: The sub-agents return only their final answers, so give them clear,
specific instructions in your delegation messages.
"""

# Create the deep research agent
def create_research_agent():
    """
    Create and return a configured deep research agent.
    
    Returns:
        LangGraph agent configured for research tasks
    """
    agent = create_deep_agent(
        tools=[internet_search],
        system_prompt=main_agent_instructions,
        subagents=[research_subagent, critique_subagent],
        model="claude-sonnet-4-20250514",  # Default model
    )
    return agent


# Example usage
if __name__ == "__main__":
    # Create the agent
    agent = create_research_agent()
    
    # Example research query
    research_query = "What are the latest developments in quantum computing and their potential applications?"
    
    # Invoke the agent
    print("Starting research on:", research_query)
    print("-" * 80)
    
    result = agent.invoke({
        "messages": [{"role": "user", "content": research_query}]
    })
    
    # Print the final response
    final_message = result["messages"][-1]
    print("\nFinal Research Report:")
    print("=" * 80)
    print(final_message.content)
    
    # Print any files created
    if "files" in result and result["files"]:
        print("\n\nFiles created during research:")
        print("-" * 80)
        for filename in result["files"]:
            print(f"- {filename}")
