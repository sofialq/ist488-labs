import streamlit as st

docs = [
    "The midterm exam will be held on October 14 during class time.",
    "Homework 3 is due before the midterm review session.",
    "The final project rubric is posted on Blackboard.",
    "Office hours are Tuesdays from 3–5 PM.",
    "The midterm review session will cover Chapters 1 through 4.",
    "Quiz 2 covers retrieval, embeddings, and reranking."
    ]
query = "When is the midterm?"

# Show title and description.
st.title("Lab 8")
st.write(" ")
st.title("Retrieval vs Reranking in RAG")
st.write("Compare how reranking improves answer accuracy over retrieval alone.")
st.write(" ")

st.subheader("Query")
st.write(f"\"{query}\"")

# retrieval 
st.subheader("Retrieval")

def retrieval_score(query, doc):
    query_words = set(query.lower().split())
    doc_words = set(doc.lower().split())
    return len(query_words & doc_words)

scored_docs = [(doc, retrieval_score(query, doc)) for doc in docs]
scored_docs.sort(key=lambda x: x[1], reverse=True)
top3 = scored_docs[:3]
 
for rank, (doc, score) in enumerate(top3, 1):
    st.write(f"\nRank {rank} | Retrieval Score: {score}")
    st.write(f"  \"{doc}\"")

# reranking
st.subheader("Reranking")

def rerank_score(doc, score = 0):
    if "midterm" in doc.lower():
        score += 2
    if "exam" in doc.lower():
        score += 2
    if any(char.isdigit() for char in doc):
        score += 3
    return score

reranked = [(doc, rerank_score(doc)) for doc, _ in top3]
reranked.sort(key=lambda x: x[1], reverse=True)

# final answer
best_doc = reranked[0][0]
st.write(f"\n**Final Answer:** \"{best_doc}\"")