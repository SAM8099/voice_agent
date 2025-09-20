from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END, START
from typing import List, Dict
from dotenv import load_dotenv
import os
load_dotenv()
# --------------------------
# State definition
# --------------------------
class State(Dict):
    query: str
    context: List[str]
    draft_answer: str
    feedback: str
    approved: bool

# --------------------------
# Agents
# --------------------------
groq_api_key = os.getenv("GROQ_API_KEY")

# Retriever agent (mock: replace with vectorDB retriever)
def retriever_agent(state: State) -> State:
    print("\n[Retriever Agent] Fetching relevant chunks...")
    # (Here you would query your vector store)
    state["context"] = [
        "The paper used CIFAR-10 and MNIST datasets.",
        "They achieved 92% accuracy on CIFAR-10 and 99% on MNIST."
    ]
    return state

# Answer agent
llm = ChatGroq(temperature=0,model_name="llama3-70b-8192",api_key=groq_api_key)  # or your chosen model
answer_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an assistant answering based only on the given context."),
    ("human", "Question: {query}\n\nContext:\n{context}\n\nDraft an answer.")
])

def answer_agent(state: State) -> State:
    print("\n[Answer Agent] Drafting an answer...")
    resp = llm.invoke(answer_prompt.format_messages(
        query=state["query"],
        context="\n".join(state["context"])
    ))
    state["draft_answer"] = resp.content
    print(f"Draft Answer: {state['draft_answer']}")
    return state

# Critic agent
critic_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a strict fact-checker. Compare the draft answer to the context."),
    ("human", 
     "Question: {query}\n\nContext:\n{context}\n\nAnswer:\n{draft}\n\n"
     "Does the answer cover all information from context relevant to the question? "
     "Reply with either 'APPROVED' or give feedback on missing/incorrect parts.")
])

def critic_agent(state: State) -> State:
    print("\n[Critic Agent] Verifying the answer...")
    resp = llm.invoke(critic_prompt.format_messages(
        query=state["query"],
        context="\n".join(state["context"]),
        draft=state["draft_answer"]
    ))
    feedback = resp.content
    state["feedback"] = feedback
    print(f"Critic Feedback: {feedback}")

    if "APPROVED" in feedback.upper():
        state["approved"] = True
    else:
        state["approved"] = False
    return state

# Refiner agent (if critic disapproves)
def refiner_agent(state: State) -> State:
    if state["approved"]:
        return state
    print("\n[Refiner Agent] Updating answer with critic feedback...")
    refine_prompt = ChatPromptTemplate.from_messages([
        ("system", "Refine the draft answer based on feedback."),
        ("human", 
         "Draft: {draft}\n\nFeedback: {feedback}\n\n"
         "Produce an improved answer.")
    ])
    resp = llm.invoke(refine_prompt.format_messages(
        draft=state["draft_answer"],
        feedback=state["feedback"]
    ))
    state["draft_answer"] = resp.content
    print(f"Refined Answer: {state['draft_answer']}")
    return state

# --------------------------
# LangGraph definition
# --------------------------
workflow = StateGraph(State)

workflow.add_node("Retriever", retriever_agent)
workflow.add_node("Answer", answer_agent)
workflow.add_node("Critic", critic_agent)
workflow.add_node("Refiner", refiner_agent)

# edges
workflow.add_edge(START, "Retriever")
workflow.add_edge("Retriever", "Answer")
workflow.add_edge("Answer", "Critic")

# conditional edge: loop if not approved
def critic_condition(state: State):
    return "END" if state["approved"] else "Refiner"

workflow.add_conditional_edges("Critic", critic_condition, {"Refiner": "Refiner", "END": END})
workflow.add_edge("Refiner", "Critic")


app = workflow.compile()

if __name__ == "__main__":
    query = "What datasets did the paper use and what accuracy did they achieve?"
    state = {"query": query}
    final_state = app.invoke(state)
    print("\n✅ Final Answer:", final_state["draft_answer"])
