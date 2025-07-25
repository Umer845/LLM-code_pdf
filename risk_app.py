
# =======================================
# 🚦 Risk Assesment Block (SAFE ✅)
# =======================================

import streamlit as st
import psycopg2
import pandas as pd
from premium import run_premium_block


def get_db_connection():
    return psycopg2.connect(
        dbname="Surveyor",
        user="postgres",
        password="United2025",
        host="localhost",
        port="5432"
    )


def fetch_num_claims():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT no_of_claims 
            FROM vehicle_inspection 
            LIMIT 1
        """)
        result = cur.fetchone()
        cur.close()
        conn.close()
        if result:
            return result[0]
        return None
    except Exception as e:
        st.error(f"❌ Could not fetch number of claims: {e}")
        return None


def calculate_risk(age, vehicle_capacity, num_claims):
    age_score = (
        1.0 if age < 25 else
        0.6 if age <= 35 else
        0.4 if age <= 55 else
        1.0
    )

    cap_score = (
        0.4 if vehicle_capacity <= 1000 else
        0.6 if vehicle_capacity <= 1600 else
        0.8 if vehicle_capacity <= 2000 else
        1.0
    )

    claim_score = (
        0.4 if num_claims < 2 else
        0.6 if num_claims <= 3 else
        0.8 if num_claims <= 5 else
        1.0
    )

    total_score = age_score + cap_score + claim_score

    if total_score <= 1.8:
        risk = "Low (Green)"
    elif total_score <= 2.4:
        risk = "Low to Moderate (Purple)"
    elif total_score < 3.0:
        risk = "Moderate to High (Yellow)"
    else:
        risk = "High (Red)"

    return age_score, cap_score, claim_score, total_score, risk


def insert_risk_record(custom_id, username, cnic, age, vehicle_capacity, num_claims, final_risk, total_score):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO vehicle_risk
            (id, client_name, cnic, no_of_claims, vehicle_capacity, age, profile_risk, risk_profile_rate)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            custom_id, username, cnic, num_claims,
            vehicle_capacity, age, final_risk, total_score
        ))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        st.error(f"❌ DB Insert Error: {e}")
        return False


def run_risk_app():
    st.title("🚦 Risk Profile Page")
    st.write("Fill in the details below to calculate your risk profile:")

    username = st.text_input("Enter your username")
    cnic = st.text_input("Enter your CNIC (e.g., 12345-1234567-1)")
    age = st.number_input("Driver Age", 16, 100, 30)
    vehicle_capacity = st.number_input("Vehicle Capacity (cc)", 500, 5000, 1500)

    if st.button("Calculate Risk"):
        if not username or not cnic:
            st.error("⚠️ Username and CNIC are required.")
            return

        num_claims = fetch_num_claims()
        if num_claims is None:
            st.error("❌ Could not find any number of claims in vehicle_inspection.")
            return

        age_score, cap_score, claim_score, total_score, final_risk = calculate_risk(
            age, vehicle_capacity, num_claims
        )

        st.success(
            f"✅ Age Score: {age_score} | Capacity Score: {cap_score} | "
            f"Claims Score: {claim_score} | Total Score: {total_score:.1f}"
        )

        bg_color = {
            "Low (Green)": "#32da32",
            "Low to Moderate (Purple)": "#8313ec",
            "Moderate to High (Yellow)": "#d4c926",
            "High (Red)": "#dd2c2c"
        }.get(final_risk, "#dddddd")

        st.markdown(
            f"""
            <div style="
                background-color: {bg_color};
                padding: 9px;
                border-radius: 8px;
                font-weight: bold;
                margin-bottom: 8px;
                margin-top: -8px;">
                📌 Final Risk Profile: {final_risk}
            </div>
            """,
            unsafe_allow_html=True
        )

        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM vehicle_risk")
            count = cur.fetchone()[0] + 1
            custom_id = f"ONL-USR-{count:03d}"
            cur.close()
            conn.close()
        except Exception as e:
            st.error(f"❌ ID Generation Error: {e}")
            return

        if insert_risk_record(custom_id, username, cnic, age, vehicle_capacity, num_claims, final_risk, total_score):
            st.success(f"✅ Data saved! Assigned ID: {custom_id}")

            try:
                conn = get_db_connection()
                df = pd.read_sql(
                    "SELECT * FROM vehicle_risk WHERE age = %s AND no_of_claims = %s",
                    conn,
                    params=(age, num_claims)
                )
                conn.close()

                if not df.empty:
                    st.dataframe(df)
                else:
                    st.info("🔍 No matching records found for this age + claims combination.")
            except Exception as e:
                st.error(f"❌ Error fetching similar records: {e}")

    if st.button("Next ➡️ Premium"):
        st.session_state.page = "premium"
        st.rerun()

    if st.button("⬅️ Back to Main"):
        st.session_state.page = "main"
        st.rerun()

    if st.session_state.get("page") == "premium":
        run_premium_block()


# =======================================
# 🚦 END Risk Assesment Block (SAFE ✅)
# =======================================