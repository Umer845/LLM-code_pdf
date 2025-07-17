# ====================
# 🚦 Risk Profile Block
# ====================
import streamlit as st
import psycopg2
import pandas as pd

st.header("🚦 Calculate Risk Profile")

age = st.number_input("Driver Age", min_value=16, max_value=100, value=30)
vehicle_capacity = st.number_input("Vehicle Capacity (cc)", min_value=500, max_value=5000, value=1500)
num_claims = st.number_input("Number of Claims", min_value=0, max_value=50, value=2)

if st.button("Calculate Risk"):
    # AGE risk score
    if age < 25:
        age_score = 1.0
    elif 25 <= age <= 35:
        age_score = 0.6
    elif 36 <= age <= 55:
        age_score = 0.4
    else:
        age_score =1

    # VEHICLE CAPACITY risk score (FIXED)
    if vehicle_capacity <= 1000:
        cap_score = 0.4
    elif 1001 <= vehicle_capacity <= 1600:
        cap_score = 0.6
    elif 1601 <= vehicle_capacity <= 2000:
        cap_score = 0.8
    else:
        cap_score = 1.0

    # CLAIMS risk score
    if num_claims < 2:
        claim_score = 0.4
    elif 2 <= num_claims <= 3:
        claim_score = 0.6
    elif 4 <= num_claims <= 5:
        claim_score = 0.8
    else:
        claim_score = 1.0

    # Total aggregate score
    total_score = age_score + cap_score + claim_score

    # ✅ Risk level based on total score — INSIDE button block
    if total_score <= 1.8:
        final_risk = "Low (Green)"
    elif total_score <= 2.4:
        final_risk = "Low to Moderate (Purple)"
    elif total_score < 3.0:
        final_risk = "Moderate to High (Yellow)"
    else:
        final_risk = "High (Red)"

    st.success(
        f"✅ Age Score: {age_score} | Capacity Score: {cap_score} | Claims Score: {claim_score} | Total Score: {total_score:.1f}"
    )

    st.session_state["final_risk"] = final_risk


    # ✅ ✅ ✅ Keep this INSIDE the button block!
    # Define background color based on risk
    if "Low (Green)" in final_risk:
        bg_color = "#32da32"  # light green
    elif "Low to Moderate" in final_risk:
        bg_color = "#8313ec"  # light purple
    elif "Moderate to High" in final_risk:
        bg_color = "#d4c926"  # light yellow
    else:
        bg_color = "#dd2c2c"  # light red

    # Render final risk with custom background
    st.markdown(
        f"""
        <div style="
            background-color: {bg_color};
            padding: 1rem;
            border-radius: 8px;
            font-weight: bold;
            margin-bottom: 15px;
            ">
            📌 Final Risk Profile: {final_risk}
        </div>
        """,
        unsafe_allow_html=True
    )

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


# ===========================
# 🚦 END Risk Profile Block
# ===========================

