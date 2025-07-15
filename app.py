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
st.title("📄 PDF Vehicle Inspection Uploader")

uploaded_file = st.file_uploader("Upload a PDF", type="pdf")

if uploaded_file is not None:
    st.success("✅ PDF uploaded!")

    # === Read PDF ===
    reader = PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()

    # === Dummy parse (replace with regex if needed) ===
    insured_name = "EUROBIZ CORPORATION"
    address = "170-CCA, PHASE-VI, DHA, LAHORE"
    vehicle_make = "Model"
    vehicle_model = "2025"
    vehicle_reg = "N.A"
    horse_power = 2755
    chassis_no = "GUN156R-1106989"
    engine_no = "IGD5774029"
    speedometer = 0
    colour = "STELLAR WHITE"
    estimated_market_value = 18093000
    is_owner = True
    is_hire_purchase = False
    last_insured_with = None
    declaration = "I/WE desire to insure the above vehicle U.I.C of Pakistan Ltd.and I/WE here declare that the particulars given above are in all respect. This Inspection from shall be the basis of the contract between me/us & the Insurer. Any untrue/incorrect statment in this from will result in the policy being null & void from Inception."
    signature_name = "SHAHID.RASHEED"
    branch = "UNITED INSURANCE CO. OF PAKISTAN LTD."
    remarks = "Complete Survey"

    # === Show the extracted data ===
    st.subheader("Extracted Data")
    st.write(f"**Insured:** {insured_name}")
    st.write(f"**Address:** {address}")
    st.write(f"**Chassis No:** {chassis_no}")
    st.write(f"**Engine No:** {engine_no}")
    st.write(f"**Vehicle Model:** {vehicle_model}")
    st.write(f"**Colour:** {colour}")
    st.write(f"**Horse_power:** {horse_power}")
    st.write(f"**Estimated_market_value:** {estimated_market_value}")
    st.write(f"**Declaration:** {declaration}")
    st.write(f"**Remarks:** {remarks}")

    # === Insert button ===
    if st.button("Insert into PostgreSQL"):
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
                    insured_name, address, vehicle_make, vehicle_model, vehicle_reg,
                    horse_power, chassis_no, engine_no, speedometer, colour,
                    estimated_market_value, is_owner, is_hire_purchase,
                    last_insured_with, declaration, signature_name, branch, remarks
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                insured_name, address, vehicle_make, vehicle_model, vehicle_reg,
                horse_power, chassis_no, engine_no, speedometer, colour,
                estimated_market_value, is_owner, is_hire_purchase,
                last_insured_with, declaration, signature_name, branch, remarks
            ))
            conn.commit()
            cur.close()
            conn.close()
            st.success("✅ Inserted into PostgreSQL database!")
        except Exception as e:
            st.error(f"❌ Error: {e}")

# ✅ === New: Ask DB section ===
import streamlit as st
import psycopg2
import pandas as pd

st.header("🔍 Ask your database")

question = st.text_input("Your Query (e.g. a name, color, model year, etc.):")

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
                            remarks ILIKE %s
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
                        search_pattern
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
