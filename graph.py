import logging
from chat_models import llm
from tools import web_search

from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
import operator
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate

# ------------------ Logging Setup ------------------
# Set up logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)



# ------------------ State Definition ------------------

#class State(TypedDict):
#    topic: str
#    research: str
#    final_answer: str

# State = TypedDict('State', {'topic': str, 'research': str, 'final_answer': str})    

AgentState = TypedDict('AgentState',{
    'topic': str, 
    'research_notes': Annotated[list,operator.add],
    'draft': str,              #writers current draft 
    'feedback': str,           #critics feedback for improvement
    'needs_improvement': bool, #flag to loop  
    'final_answer': str        #final accepted answer
    })    

# ------------------ Nodes --------------------

def researcher_node(state:AgentState) -> dict[str, any]:
    
    """A node that researches the given topic using the web search tool."""
    
    topic = state["topic"]
    logger.info(f"🔎 Researcher searching for: {topic}")
    
    # Use the tool directly
    search_result = web_search.invoke(topic)
    logger.info(f"✅ Researcher got {len(search_result)} characters of results")
    
    # Create a summary for the writer
    research_summary = f"Research on '{topic}':\n{search_result}"
    return {"research_notes": [research_summary]}
    

def writer_node(state:AgentState)-> dict:
    
    """Write or improve the summary based on existing notes and feedback."""
    
    topic = state["topic"]
    research = "\n\n".join(state["research_notes"])
    feedback = state.get("feedback", "")
    draft = state.get("draft","")
    
    if feedback:
        logger.info("✍️ Writer improving draft with feedback")
        prompt = ChatPromptTemplate.from_messages([
             ("system", "You are a skilled writer. Improve the following draft based on the critic's feedback. Keep the same general length and tone."),
            ("human", "Topic: {topic}\nResearch Notes: {research}\n\nCurrent Draft:\n{draft}\n\nCritic's Feedback:\n{feedback}\n\nWrite an improved version.")
        ])
        print("Writer improving draft with feedback -----",prompt)
        variables = {"topic": topic, "research": research, "draft": draft, "feedback": feedback}
    else:
        logger.info("✍️ Writer writing initial draft")
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a skilled professional writer. Based on the research, write a clear, well-structured summary (aim for 500-1000 words)."),
            ("human", "Topic: {topic}\nResearch Notes: {research}")
        ])
        print("Writer writing the initial draft -----",prompt)
        variables = {"topic": topic, "research": research}
                  
    chain = prompt | llm
    
    response = chain.invoke({"topic": topic,"research": research,"draft": draft,"feedback": feedback})
    
    # Extract text from response (handles list or string)
    
    if isinstance(response.content, list):
        new_draft = response.content[0]['text']
    else:
        new_draft = response.content
    
    logger.info(f"✅ Writer finished (draft length: {len(new_draft)} characters)")
    return {"draft": new_draft, "final_answer": new_draft, "feedback": ""}
    
    
def critic_node(state: AgentState) -> dict[str, any]:
    
    """Evaluate the draft based on length. If too short, request improvement."""
    
    draft = state.get("final_answer", "")
    
    # Rough estimate: 500 words ≈ 2500 characters (assuming 5 chars per word)
    min_words = 500
    min_chars = min_words * 5
    
    if len(draft) < min_chars:
        word_estimate = len(draft) // 5
        feedback = f"The draft is too short (about {word_estimate} words). Please expand to at least {min_words} words. Add more details, examples, or sections."
        logger.info(f"❌ Critic: draft too short ({word_estimate} words) – requesting improvement")
        return {"feedback": feedback, "needs_improvement": True}
    else:
        logger.info("✅ Critic: draft length acceptable – approving")
        return {"feedback": "", "needs_improvement": False}
    
# ------------------ Build Graph ------------------
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("researcher", researcher_node)
workflow.add_node("writer", writer_node)
workflow.add_node("critic", critic_node)

# Set entry point
workflow.set_entry_point("researcher")

# Add edges
workflow.add_edge("researcher", "writer")
workflow.add_edge("writer", "critic")

# Conditional edge from critic
def decide_next(state: AgentState) -> str:
    if state.get("needs_improvement", False):
        return "writer"      # go back to writer for improvement
    else:
        return "end"


# Add a conditional edge from the "critic" node
# Unlike a normal edge (which always goes to one node), a conditional edge
# runs a decision function (decide_next) that looks at the current state
# and returns the name of the next node to go to.

workflow.add_conditional_edges(
    "critic",              # source node: after critic finishes
    decide_next, {         # function that decides which node comes next
    "writer": "writer",    # if decide_next function returns "writer", go to writer node
    "end": END             # if decide_next function returns "end", stop the graph
})

# Compile
app = workflow.compile()

# ------------------ Run Function ------------------

def run_research(topic: str) -> str:
    """Run the research workflow and return the final answer."""
    logger.info(f"🚀 Starting research for topic: {topic}")
    initial_state: AgentState = {"topic": topic}
    final_state = app.invoke(initial_state)
    logger.info("🏁 Research complete")
    return final_state["final_answer"]