# ====================
# 🚦 Risk Profile Block
# ====================
import streamlit as st
import psycopg2
import pandas as pd
from PyPDF2 import PdfReader

st.header("🚦 Calculate Risk Profile")

age = st.number_input("Driver Age", min_value=16, max_value=100, value=30)
vehicle_capacity = st.number_input("Vehicle Capacity (cc)", min_value=500, max_value=5000, value=1500)
num_claims = st.number_input("Number of Claims", min_value=0, max_value=50, value=2)

if st.button("Calculate Risk"):
    # AGE risk
    if age < 25:
        age_score = 3
        age_risk = "High"
    elif age < 35:
        age_score = 2
        age_risk = "Moderate"
    elif age < 55:
        age_score = 1
        age_risk = "Low"
    else:
        age_score = 3
        age_risk = "High"

    # VEHICLE CAPACITY risk
    if vehicle_capacity < 1000:
        cap_score = 1
        cap_risk = "Low"
    elif vehicle_capacity <= 1800:
        cap_score = 2
        cap_risk = "Moderate"
    elif vehicle_capacity <= 3000:
        cap_score = 3
        cap_risk = "High"
    else:
        cap_score = 3
        cap_risk = "High"

    # CLAIMS risk
    if num_claims < 3:
        claim_score = 1
        claim_risk = "Low"
    elif num_claims <= 7:
        claim_score = 2
        claim_risk = "Moderate"
    else:
        claim_score = 3
        claim_risk = "High"

    total_score = age_score + cap_score + claim_score

    if total_score <= 4:
        final_risk = "Low"
    elif total_score <= 6:
        final_risk = "Moderate"
    else:
        final_risk = "High"

    st.success(f"✅ Age Risk: {age_risk} | Capacity Risk: {cap_risk} | Claims Risk: {claim_risk}")
    st.info(f"📌 Final Risk Profile: **{final_risk}**")

    # Show DB records matching same AGE + CLAIMS
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
            WHERE MODEL_YEAR = %s AND NO_OF_CLAIMS = %s
        """
        cur.execute(sql, (age, num_claims))
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
        st.error(f"❌ DB Error: {e}")
