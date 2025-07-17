import streamlit as st
import psycopg2
import pandas as pd
from PyPDF2 import PdfReader

st.title("📄 Upload PDF or Excel and Insert to DB")

uploaded_file = st.file_uploader(
    "Upload a PDF or Excel file",
    type=["pdf", "xls", "xlsx"]
)

data_to_insert = []

# Helper to safely handle int-like fields
def safe_int(val):
    try:
        if val is None:
            return 0
        if isinstance(val, str) and val.strip().lower() in ["nan", "inf", "-inf"]:
            return 0
        if pd.isna(val):
            return 0
        val = int(float(val))
        if abs(val) > 9_000_000_000_000_000_000:
            return 0
        return val
    except:
        return 0

if uploaded_file is not None:
    if uploaded_file.name.endswith(".pdf"):
        st.success("✅ PDF uploaded!")
        reader = PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        st.write("**Extracted text:**")
        st.text(text)
        st.warning("⚠️ You must parse real fields from PDF and map them here!")

    elif uploaded_file.name.endswith((".xls", ".xlsx")):
        st.success("✅ Excel uploaded!")
        df = pd.read_excel(uploaded_file)
        st.dataframe(df)
        st.info("✅ Processing rows from Excel...")

        for _, row in df.iterrows():
            client_name = row.get('CLIENT_NAME')
            address1 = row.get('ADDRESS1')
            city_id = safe_int(row.get('CITY_ID'))
            city_name = row.get('CITY_NAME')
            region_id = safe_int(row.get('REGION_ID'))
            bus_class_name = row.get('BUS_CLASS_NAME')
            src_income_title = row.get('SRC_INCOME_TITLE')
            active_tax_payer = bool(row.get('ACTIVE_TAX_PAYER'))
            driving_style = row.get('DRIVING_STYLE')
            make_name = row.get('MAKE_NAME')
            sub_make_name = row.get('SUB_MAKE_NAME')
            model_year = safe_int(row.get('MODEL_YEAR'))
            reg_number = str(row.get('REG_NUMBER')) if row.get('REG_NUMBER') else ""
            tracker_id = safe_int(row.get('TRACKER_ID'))
            policy_type_name = row.get('POLICY_TYPE_NAME')
            suminsured = safe_int(row.get('SUMINSURED'))
            grosspremium = safe_int(row.get('GROSSPREMIUM'))
            netpremium = safe_int(row.get('NETPREMIUM'))
            no_of_claims = bool(row.get('NO_OF_CLAIMS'))
            clm_amount = safe_int(row.get('CLM_AMOUNT'))

            data_to_insert.append((
                client_name, address1, city_id, city_name, region_id,
                bus_class_name, src_income_title, active_tax_payer, driving_style,
                make_name, sub_make_name, model_year, reg_number, tracker_id,
                policy_type_name, suminsured, grosspremium, netpremium,
                no_of_claims, clm_amount
            ))

        st.info(f"✅ Processed {len(data_to_insert)} rows ready for insert.")

if st.button("Insert to PostgreSQL"):
    if not data_to_insert:
        st.warning("⚠️ No data found to insert. Please upload valid data first.")
    else:
        try:
            conn = psycopg2.connect(
                dbname="Surveyor",
                user="postgres",
                password="United2025",
                host="localhost",
                port="5432"
            )
            cur = conn.cursor()
            rows_inserted = 0

            for record in data_to_insert:
                (
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
                ) = record

                active_tax_payer = '1' if active_tax_payer else '0'
                no_of_claims = '1' if no_of_claims else '0'

                cur.execute("""
                    INSERT INTO vehicle_inspection (
                        CLIENT_NAME,
                        ADDRESS1,
                        CITY_ID,
                        CITY_NAME,
                        REGION_ID,
                        BUS_CLASS_NAME,
                        SRC_INCOME_TITLE,
                        ACTIVE_TAX_PAYER,
                        DRIVING_STYLE,
                        MAKE_NAME,
                        SUB_MAKE_NAME,
                        MODEL_YEAR,
                        REG_NUMBER,
                        TRACKER_ID,
                        POLICY_TYPE_NAME,
                        SUMINSURED,
                        GROSSPREMIUM,
                        NETPREMIUM,
                        NO_OF_CLAIMS,
                        CLM_AMOUNT
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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

                rows_inserted += 1

            conn.commit()
            cur.close()
            conn.close()
            st.success(f"✅ Inserted {rows_inserted} rows into PostgreSQL!")

        except Exception as e:
            st.error(f"❌ Error: {e}")

# ====================
# 🔍 Search Block
# ====================
st.header("🔍 Search your database")

question = st.text_input("Your Query (e.g. client name, city, make, etc.):")

if st.button("Search"):
    if not question.strip():
        st.warning("⚠️ Please type something to search.")
    else:
        try:
            conn = psycopg2.connect(
                dbname="Surveyor",
                user="postgres",
                password="United2025",
                host="localhost",
                port="5432"
            )
            cur = conn.cursor()

            sql = """
                SELECT * FROM vehicle_inspection
                WHERE
                    CLIENT_NAME ILIKE %s OR
                    ADDRESS1 ILIKE %s OR
                    CAST(CITY_ID AS TEXT) ILIKE %s OR
                    CITY_NAME ILIKE %s OR
                    CAST(REGION_ID AS TEXT) ILIKE %s OR
                    BUS_CLASS_NAME ILIKE %s OR
                    SRC_INCOME_TITLE ILIKE %s OR
                    CAST(ACTIVE_TAX_PAYER AS TEXT) ILIKE %s OR
                    DRIVING_STYLE ILIKE %s OR
                    MAKE_NAME ILIKE %s OR
                    SUB_MAKE_NAME ILIKE %s OR
                    CAST(MODEL_YEAR AS TEXT) ILIKE %s OR
                    REG_NUMBER ILIKE %s OR
                    CAST(TRACKER_ID AS TEXT) ILIKE %s OR
                    POLICY_TYPE_NAME ILIKE %s OR
                    CAST(SUMINSURED AS TEXT) ILIKE %s OR
                    CAST(GROSSPREMIUM AS TEXT) ILIKE %s OR
                    CAST(NETPREMIUM AS TEXT) ILIKE %s OR
                    CAST(NO_OF_CLAIMS AS TEXT) ILIKE %s OR
                    CAST(CLM_AMOUNT AS TEXT) ILIKE %s
            """

            search_pattern = f"%{question}%"
            cur.execute(sql, tuple([search_pattern] * 20))

            rows = cur.fetchall()
            colnames = [desc[0] for desc in cur.description]

            if rows:
                df = pd.DataFrame(rows, columns=colnames)
                st.dataframe(df)
            else:
                st.info("🔍 No matching records found.")

            cur.close()
            conn.close()

        except Exception as e:
            st.error(f"❌ Error: {e}")


# ====================
# 🔍 END Search Block
# ====================
