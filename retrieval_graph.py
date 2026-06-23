import os
import math
from typing import Annotated, Literal, Sequence, TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph import END, StateGraph, START
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langchain_openai import ChatOpenAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import SupabaseVectorStore
from langchain_core.tools import tool  # <-- Manual tool decorator

from app.database import get_db

# ==========================================
# 1. GRAPH STATE (Memory)
# ==========================================
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

# ==========================================
# 2. SETUP VECTOR STORE
# ==========================================
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vectorstore = SupabaseVectorStore(
    client=get_db(),
    embedding=embeddings,
    table_name="documents",
    query_name="match_documents"
)

# ==========================================
# 3. MANUALLY CREATE THE TOOL
# ==========================================
# Yeh decorator LLM ko function ka naam, input (query), aur docstring bhejta hai
# ==========================================
# 3. MANUALLY CREATE THE TOOL
# ==========================================
# ==========================================
# 3. MANUALLY CREATE THE TOOL
# ==========================================
@tool
def pdf_search_tool(query: str) -> str:
    """Search the uploaded PDF documents for information. Use this tool if the user asks about any documents, certificates, or specific facts."""
    
    docs = vectorstore.similarity_search(query, k=3)
    
    if not docs:
        return "No relevant information found in the database."
        
    context = "\n\n".join([f"Document Content: {doc.page_content}" for doc in docs])
    return context


@tool
def calculater_tool(query: str) -> str:
    """A calculator tool for basic math operations. 
    WARNING: NEVER pass algebraic variables like 'x' or '=' signs. 
    You must do the algebra yourself and ONLY pass strict numbers (e.g., '24 / 4', 'math.sqrt(25)', '5 ** 2')."""
    try:
        allowed_names = {k: v for k, v in math.__dict__.items() if not k.startswith("__")}
        result = eval(query, {"__builtins__": None}, allowed_names)
        return f"Calculation Result: {result}"
    except Exception as e:
        return f"Error: {str(e)}. You passed an invalid expression. Remove any letters or '=' signs."

tools = [pdf_search_tool, calculater_tool]
tool_node = ToolNode(tools)

# ==========================================
# 4. SETUP LLM & BIND TOOLS
# ==========================================
llm = ChatOpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
    # FIXED: Added the 'openai/' prefix!
    model="openai/gpt-4o-mini" 
)

llm_with_tools = llm.bind_tools(tools)

# ==========================================
# 5. DEFINE NODES (The Workers)
# ==========================================
def agent_node(state: AgentState):
    """Yeh node LLM ko call karta hai poori history ke saath."""
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}

# ==========================================
# 6. DEFINE EDGES (The Routing Logic)
# ==========================================
def should_continue(state: AgentState) -> Literal["tools", "__end__"]:
    """Yeh function decide karta hai ki database search karna hai ya nahi."""
    messages = state["messages"]
    last_message = messages[-1]
    
    # Agar LLM ne decide kiya ki usko tool use karna hai
    if last_message.tool_calls:
        return "tools"
    
    # Warna seedha chat complete kardo
    return "__end__"

# ==========================================
# 7. BUILD AND COMPILE THE GRAPH
# ==========================================
workflow = StateGraph(AgentState)

workflow.add_node("agent", agent_node)
workflow.add_node("tools", tool_node)

workflow.add_edge(START, "agent")
workflow.add_conditional_edges("agent", should_continue)
workflow.add_edge("tools", "agent") 

# Humara Agent tayyar hai!
app_graph = workflow.compile()