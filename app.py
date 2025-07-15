import streamlit as st
from pypdf import PdfReader
import ollama

# === CONFIG ===
EMBEDDING_MODEL = 'hf.co/CompendiumLabs/bge-base-en-v1.5-gguf'

# === Load and process PDF ===
@st.cache_resource
def load_pdf():
    dataset = []
    with open('text.pdf', 'rb') as file:
        reader = PdfReader(file)
        for page in reader.pages:
            text = page.extract_text()
            if text:
                lines = text.split('\n')
                dataset.extend([line.strip() for line in lines if line.strip()])
    return dataset

dataset = load_pdf()
st.info(f"✅ Loaded {len(dataset)} lines from PDF")

# === Build vector DB ===
@st.cache_resource
def build_vector_db(dataset):
    vector_db = []
    for chunk in dataset:
        embedding = ollama.embed(model=EMBEDDING_MODEL, input=chunk)['embeddings'][0]
        vector_db.append((chunk, embedding))
    return vector_db

VECTOR_DB = build_vector_db(dataset)

# === Cosine similarity ===
def cosine_similarity(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x ** 2 for x in a) ** 0.5
    norm_b = sum(y ** 2 for y in b) ** 0.5
    return dot / (norm_a * norm_b)

# === Retrieve relevant chunks ===
def retrieve(query, top_n=3):
    query_embedding = ollama.embed(model=EMBEDDING_MODEL, input=query)['embeddings'][0]
    similarities = [(chunk, cosine_similarity(query_embedding, emb)) for chunk, emb in VECTOR_DB]
    similarities.sort(key=lambda x: x[1], reverse=True)
    return similarities[:top_n]

# === Streamlit UI ===
st.title("📄 PDF AnswerBot")
st.write("Ask something from your PDF!")

query = st.text_input("Your question:", placeholder="Type your question here...")

if st.button("Search") and query:
    with st.spinner("Searching..."):
        results = retrieve(query)
        # Join all retrieved chunks into a single paragraph
        answer = " ".join(chunk for chunk, _ in results)
        st.success("Answer:")
        st.write(answer)
