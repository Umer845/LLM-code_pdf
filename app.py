from flask import Flask, request, render_template
import ollama
import streamlit as st

app = Flask(__name__)

# Embedding and LLM models
EMBEDDING_MODEL = 'hf.co/CompendiumLabs/bge-base-en-v1.5-gguf'
LANGUAGE_MODEL = 'hf.co/bartowski/Llama-3.2-1B-Instruct-GGUF'

# Load dataset
with open('cat-facts.txt', 'r', encoding='utf-8') as file:
    dataset = [line.strip() for line in file if line.strip()]

# Build vector DB
VECTOR_DB = []

def add_chunk_to_database(chunk):
    embedding = ollama.embed(model=EMBEDDING_MODEL, input=chunk)['embeddings'][0]
    VECTOR_DB.append((chunk, embedding))

# Load embeddings only once
for i, chunk in enumerate(dataset):
    add_chunk_to_database(chunk)

# Cosine similarity
def cosine_similarity(a, b):
    dot_product = sum([x * y for x, y in zip(a, b)])
    norm_a = sum([x ** 2 for x in a]) ** 0.5
    norm_b = sum([x ** 2 for x in b]) ** 0.5
    return dot_product / (norm_a * norm_b)

# Retrieve top N relevant chunks
def retrieve(query, top_n=3):
    query_embedding = ollama.embed(model=EMBEDDING_MODEL, input=query)['embeddings'][0]
    similarities = []
    for chunk, embedding in VECTOR_DB:
        similarity = cosine_similarity(query_embedding, embedding)
        similarities.append((chunk, similarity))
    similarities.sort(key=lambda x: x[1], reverse=True)
    return similarities[:top_n]

# Route
@app.route('/', methods=['GET', 'POST'])
def index():
    response = ''
    retrieved_chunks = []
    if request.method == 'POST':
        input_query = request.form['query']
        retrieved_chunks = retrieve(input_query)

        instruction_prompt = (
            "You are a helpful chatbot.\n"
            "Use only the following pieces of context to answer the question. Don't make up any new information:\n" +
            "\n".join([f" - {chunk}" for chunk, _ in retrieved_chunks])
        )

        # Run chatbot
        stream = ollama.chat(
            model=LANGUAGE_MODEL,
            messages=[
                {'role': 'system', 'content': instruction_prompt},
                {'role': 'user', 'content': input_query},
            ],
            stream=True,
        )

        for chunk in stream:
            response += chunk['message']['content']

    return render_template('index.html', response=response, retrieved=retrieved_chunks)

if __name__ == '__main__':
    app.run(debug=True)
