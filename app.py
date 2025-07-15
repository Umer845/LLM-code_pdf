# import streamlit as st
# from pypdf import PdfReader
# import ollama

# # === CONFIG ===
# EMBEDDING_MODEL = 'hf.co/CompendiumLabs/bge-base-en-v1.5-gguf'

# # === Load and process PDF ===
# @st.cache_resource
# def load_pdf():
#     dataset = []
#     with open('text.pdf', 'rb') as file:
#         reader = PdfReader(file)
#         for page in reader.pages:
#             text = page.extract_text()
#             if text:
#                 lines = text.split('\n')
#                 dataset.extend([line.strip() for line in lines if line.strip()])
#     return dataset

# dataset = load_pdf()
# st.info(f"✅ Loaded {len(dataset)} lines from PDF")

# # === Build vector DB ===
# @st.cache_resource
# def build_vector_db(dataset):
#     vector_db = []
#     for chunk in dataset:
#         embedding = ollama.embed(model=EMBEDDING_MODEL, input=chunk)['embeddings'][0]
#         vector_db.append((chunk, embedding))
#     return vector_db

# VECTOR_DB = build_vector_db(dataset)

# # === Cosine similarity ===
# def cosine_similarity(a, b):
#     dot = sum(x * y for x, y in zip(a, b))
#     norm_a = sum(x ** 2 for x in a) ** 0.5
#     norm_b = sum(y ** 2 for y in b) ** 0.5
#     return dot / (norm_a * norm_b)

# # === Retrieve relevant chunks ===
# def retrieve(query, top_n=3):
#     query_embedding = ollama.embed(model=EMBEDDING_MODEL, input=query)['embeddings'][0]
#     similarities = [(chunk, cosine_similarity(query_embedding, emb)) for chunk, emb in VECTOR_DB]
#     similarities.sort(key=lambda x: x[1], reverse=True)
#     return similarities[:top_n]

# # === Streamlit UI ===
# st.title("📄 PDF AnswerBot")
# st.write("Ask something from your PDF!")

# query = st.text_input("Your question:", placeholder="Type your question here...")

# if st.button("Search") and query:
#     with st.spinner("Searching..."):
#         results = retrieve(query)
#         # Join all retrieved chunks into a single paragraph
#         answer = " ".join(chunk for chunk, _ in results)
#         st.success("Answer:")
#         st.write(answer)



#############New  Code #################
import streamlit as st
import psycopg2
import pandas as pd  # needed for displaying results as DataFrame
from PyPDF2 import PdfReader

# === Streamlit UI ===
st.title("📄 Upload PDF or Excel and Insert to DB")

uploaded_file = st.file_uploader(
    "Upload a PDF or Excel file",
    type=["pdf", "xls", "xlsx"]
)

if uploaded_file is not None:
    if uploaded_file.name.endswith(".pdf"):
        st.success("✅ PDF uploaded!")
        reader = PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()

        # Dummy parse
        insured_name = "PDF_INSURED"
        age = 30
        number_of_claims = 1

        st.write("**Extracted text from PDF:**")
        st.text(text)

    elif uploaded_file.name.endswith((".xls", ".xlsx")):
        st.success("✅ Excel uploaded!")
        df = pd.read_excel(uploaded_file)

        st.write("**Preview Excel:**")
        st.dataframe(df)

        # Dummy values — you could map your Excel columns:
        insured_name = "EXCEL_INSURED"
        age = 40
        number_of_claims = 2

    # Insert button for both
    if st.button("Insert to PostgreSQL"):
        try:
            conn = psycopg2.connect(
                dbname="Surveyor",
                user="postgres",
                password="United2025",
                host="localhost",
                port="5432"
            )
            cur = conn.cursor()

            cur.execute("""
                INSERT INTO vehicle_inspection (
                    insured_name,
                    age,
                    number_of_claims
                ) VALUES (%s, %s, %s)
            """, (
                insured_name,
                age,
                number_of_claims
            ))

            conn.commit()
            cur.close()
            conn.close()
            st.success("✅ Inserted into PostgreSQL!")

        except Exception as e:
            st.error(f"❌ Error: {e}")

# ✅ === New: Ask DB section ===
import streamlit as st
import psycopg2
import pandas as pd

st.header("🔍 Ask your database")

question = st.text_input("Your Query (e.g. a name, age, number of claims, etc.):")

if st.button("Search"):
    if not question.strip():
        st.warning("⚠️ Please type something to search.")
    else:
        try:
            with psycopg2.connect(
                dbname="Surveyor",
                user="postgres",
                password="United2025",
                host="localhost",
                port="5432"
            ) as conn:
                with conn.cursor() as cur:

                    sql = """
                        SELECT * FROM vehicle_inspection
                        WHERE
                            insured_name ILIKE %s OR
                            address ILIKE %s OR
                            vehicle_make ILIKE %s OR
                            vehicle_model ILIKE %s OR
                            vehicle_reg ILIKE %s OR
                            chassis_no ILIKE %s OR
                            engine_no ILIKE %s OR
                            colour ILIKE %s OR
                            branch ILIKE %s OR
                            remarks ILIKE %s OR
                            CAST(age AS TEXT) ILIKE %s OR
                            CAST(number_of_claims AS TEXT) ILIKE %s
                    """

                    search_pattern = f"%{question}%"

                    cur.execute(sql, (
                        search_pattern,
                        search_pattern,
                        search_pattern,
                        search_pattern,
                        search_pattern,
                        search_pattern,
                        search_pattern,
                        search_pattern,
                        search_pattern,
                        search_pattern,
                        search_pattern,  # age
                        search_pattern   # number_of_claims
                    ))

                    rows = cur.fetchall()
                    colnames = [desc[0] for desc in cur.description]

                    if rows:
                        df = pd.DataFrame(rows, columns=colnames)
                        st.dataframe(df)
                    else:
                        st.info("🔍 No matching records found.")

        except Exception as e:
            st.error(f"❌ Error: {e}")



age = 35  # example age, extract properly if you have it
number_of_claims = 1  # example