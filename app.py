from flask import Flask, request, render_template
from PyPDF2 import PdfReader
import ollama

app = Flask(__name__)

# Embedding model
EMBEDDING_MODEL = 'hf.co/CompendiumLabs/bge-base-en-v1.5-gguf'

# Load and process PDF
dataset = []
with open('text.pdf', 'rb') as file:
    reader = PdfReader(file)
    for page in reader.pages:
        text = page.extract_text()
        if text:
            lines = text.split('\n')
            dataset.extend([line.strip() for line in lines if line.strip()])

print(f"✅ Loaded {len(dataset)} lines from PDF")

# Vector DB
VECTOR_DB = []

def add_chunk_to_database(chunk):
    embedding = ollama.embed(model=EMBEDDING_MODEL, input=chunk)['embeddings'][0]
    VECTOR_DB.append((chunk, embedding))

# Precompute embeddings
for chunk in dataset:
    add_chunk_to_database(chunk)

# Cosine similarity
def cosine_similarity(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x ** 2 for x in a) ** 0.5
    norm_b = sum(y ** 2 for y in b) ** 0.5
    return dot / (norm_a * norm_b)

# Retrieve top N relevant chunks
def retrieve(query, top_n=3):
    query_embedding = ollama.embed(model=EMBEDDING_MODEL, input=query)['embeddings'][0]
    similarities = [(chunk, cosine_similarity(query_embedding, emb)) for chunk, emb in VECTOR_DB]
    similarities.sort(key=lambda x: x[1], reverse=True)
    return similarities[:top_n]

@app.route('/', methods=['GET', 'POST'])
def index():
    response = ''
    retrieved_chunks = []

    if request.method == 'POST':
        input_query = request.form['query']
        retrieved_chunks = retrieve(input_query)

        # Build response only from the PDF chunks
        response = "\n\n".join([f"{i+1}. {chunk}" for i, (chunk, _) in enumerate(retrieved_chunks)])

    return render_template('index.html', response=response, retrieved=retrieved_chunks)

if __name__ == '__main__':
    app.run(debug=True)
