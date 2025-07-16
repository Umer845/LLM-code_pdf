
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
        client_name,
        address1,
        city_id,
        city_name,
        region_id,
        bus_class_name,
        src_income_title,
        active_tax_payer,
        driving_style,
        make_name,
        sub_make_name,
        model_year,
        reg_number,
        tracker_id,
        policy_type_name,
        suminsured,
        grosspremium,
        netpremium,
        no_of_claims,
        clm_amount
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
""", (
    client_name,
    address1,
    city_id,
    city_name,
    region_id,
    bus_class_name,
    src_income_title,
    active_tax_payer,
    driving_style,
    make_name,
    sub_make_name,
    model_year,
    reg_number,
    tracker_id,
    policy_type_name,
    suminsured,
    grosspremium,
    netpremium,
    no_of_claims,
    clm_amount
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

question = st.text_input("Your Query (e.g. client name, city, make, age, number of claims, etc.):")

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
                            client_name ILIKE %s OR
                            address1 ILIKE %s OR
                            CAST(city_id AS TEXT) ILIKE %s OR
                            city_name ILIKE %s OR
                            CAST(region_id AS TEXT) ILIKE %s OR
                            bus_class_name ILIKE %s OR
                            src_income_title ILIKE %s OR
                            CAST(active_tax_payer AS TEXT) ILIKE %s OR
                            driving_style ILIKE %s OR
                            make_name ILIKE %s OR
                            sub_make_name ILIKE %s OR
                            CAST(model_year AS TEXT) ILIKE %s OR
                            reg_number ILIKE %s OR
                            tracker_id ILIKE %s OR
                            policy_type_name ILIKE %s OR
                            CAST(suminsured AS TEXT) ILIKE %s OR
                            CAST(grosspremium AS TEXT) ILIKE %s OR
                            CAST(netpremium AS TEXT) ILIKE %s OR
                            CAST(no_of_claims AS TEXT) ILIKE %s OR
                            CAST(clm_amount AS TEXT) ILIKE %s OR
                            CAST(age AS TEXT) ILIKE %s OR
                            CAST(number_of_claims AS TEXT) ILIKE %s
                    """

                    search_pattern = f"%{question}%"

                    cur.execute(sql, (
                        search_pattern,  # client_name
                        search_pattern,  # address1
                        search_pattern,  # city_id
                        search_pattern,  # city_name
                        search_pattern,  # region_id
                        search_pattern,  # bus_class_name
                        search_pattern,  # src_income_title
                        search_pattern,  # active_tax_payer
                        search_pattern,  # driving_style
                        search_pattern,  # make_name
                        search_pattern,  # sub_make_name
                        search_pattern,  # model_year
                        search_pattern,  # reg_number
                        search_pattern,  # tracker_id
                        search_pattern,  # policy_type_name
                        search_pattern,  # suminsured
                        search_pattern,  # grosspremium
                        search_pattern,  # netpremium
                        search_pattern,  # no_of_claims
                        search_pattern,  # clm_amount
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
