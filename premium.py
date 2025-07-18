# =============================
# 🚗 Estimated Premium Rate Block
# =============================
import streamlit as st
import psycopg2
import pandas as pd

def run_premium_block():
 st.header("💰 Premium Calculation Block")

# User inputs
MODEL_YEAR = st.number_input("Enter Latest Model Year", min_value=1980, max_value=2050, value=2024)
MAKE_NAME = st.text_input("Enter Vehicle Make Name")
SUB_MAKE_NAME = st.text_input("Enter Vehicle Variant")

if st.button("Calculate Premium Rate"):
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
            SELECT SUMINSURED, NETPREMIUM, TRACKER_ID
            FROM vehicle_inspection
            WHERE MODEL_YEAR = %s
              AND MAKE_NAME = %s
              AND SUB_MAKE_NAME = %s
            LIMIT 1
        """
        cur.execute(sql, (MODEL_YEAR, MAKE_NAME, SUB_MAKE_NAME))
        row = cur.fetchone()

        if row:
            suminsured = row[0]
            netpremium = row[1]
            tracker_id = row[2]

            if suminsured and suminsured > 0:
                premium_rate = netpremium / suminsured
                premium_rate_percent = premium_rate * 100

                st.success(f"✅ Sum Insured: {suminsured}")
                st.success(f"✅ Net Premium: {netpremium}")
                st.info(f"📌 Base Estimated Premium Rate: **{premium_rate_percent:.2f}%**")

                # Get risk profile
                final_risk = st.session_state.get("final_risk")
                if final_risk is None:
                    st.warning("⚠️ Please calculate the driver risk profile first!")

                adjusted_premium_rate_percent = premium_rate_percent

                if "Low" in final_risk:
                    adjusted_premium_rate_percent += premium_rate_percent * 0.10
                elif "Moderate" in final_risk:
                    adjusted_premium_rate_percent += premium_rate_percent * 0.20
                elif "High" in final_risk:
                    adjusted_premium_rate_percent += premium_rate_percent * 0.50

                # Add tracker adjustment
                if tracker_id and tracker_id > 0:
                    adjusted_premium_rate_percent += premium_rate_percent * 0.05  # installed → +5%
                    st.info("🚗 Tracker installed: Added 5% to base premium.")
                else:
                    adjusted_premium_rate_percent += premium_rate_percent * 0.10  # not installed → +10%
                    st.info("🚗 Tracker NOT installed: Added 10% to base premium.")

                st.info(f"📌 Final Adjusted Premium Rate: **{adjusted_premium_rate_percent:.2f}%**")
                st.info(f"📌 Driver Risk Profile: **{final_risk}**")

            else:
                st.warning("⚠️ Sum insured is zero or missing. Cannot calculate premium rate.")
        else:
            st.info("🔍 No matching vehicle record found.")

        cur.close()
        conn.close()

    except Exception as e:
        st.error(f"❌ DB Error: {e}")



# =====================================
# 🚗 END Estimated Premium Rate Block
# =====================================