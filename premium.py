# premium.py

# =============================
# 🚗 Estimated Premium Rate Block
# =============================

# premium.py

import streamlit as st
import psycopg2
import pandas as pd

def run_premium_block():
    st.header("💰 Premium Calculation Block")

    # 🆕 Username for driver risk
    username = st.text_input("Enter your username to fetch risk rate")

    MODEL_YEAR = st.number_input("Enter Latest Model Year", min_value=1980, max_value=2050, value=2024)
    MAKE_NAME = st.text_input("Enter Vehicle Make Name", placeholder="Enter Vehicle Make Name")
    SUB_MAKE_NAME = st.text_input("Enter Vehicle Variant", placeholder="Enter Vehicle Sub-Make Name")

    if st.button("Calculate & Save Premium Rate"):
        try:
            conn = psycopg2.connect(
                dbname="Surveyor",
                user="postgres",
                password="United2025",
                host="localhost",
                port="5432"
            )
            cur = conn.cursor()

            # ✅ 1️⃣ JOIN: Get risk_profile_rate from vehicle_risk + premium data from vehicle_inspection
            query = """
                SELECT vr.risk_profile_rate, vi.suminsured, vi.netpremium, vi.tracker_id
                FROM vehicle_risk vr
                JOIN vehicle_inspection vi
                  ON vi.model_year = %s
                 AND LOWER(vi.make_name) = LOWER(%s)
                 AND LOWER(vi.sub_make_name) = LOWER(%s)
                WHERE LOWER(vr.client_name) = LOWER(%s)
                LIMIT 1
            """
            cur.execute(query, (MODEL_YEAR, MAKE_NAME, SUB_MAKE_NAME, username))
            row = cur.fetchone()

            if row:
                # ✅ SAFE CONVERSION: Decimal to float
                risk_rate = float(row[0]) if row[0] is not None else 0.0
                suminsured = float(row[1]) if row[1] is not None else 0.0
                netpremium = float(row[2]) if row[2] is not None else 0.0
                tracker_id = int(row[3]) if row[3] is not None else 0

                st.success(f"✅ Driver Risk Rate: {risk_rate}")
                st.success(f"✅ Sum Insured: {suminsured}")
                st.success(f"✅ Net Premium: {netpremium}")

                if suminsured > 0 and netpremium > 0:
                    base_premium_rate = netpremium / suminsured
                    base_percent = base_premium_rate * 100

                    st.info(f"📌 Base Premium Rate: **{base_percent:.2f}%**")

                    # ✅ Adjust with driver risk profile rate
                    adjusted_premium = base_percent * (1 + risk_rate)

                    # ✅ Add tracker adjustment
                    if tracker_id > 0:
                        adjusted_premium += base_percent * 0.05
                        st.info("🚗 Tracker installed: +5%")
                    else:
                        adjusted_premium += base_percent * 0.10
                        st.info("🚗 Tracker NOT installed: +10%")

                    st.info(f"📌 Final Adjusted Premium Rate: **{adjusted_premium:.2f}%**")

                    # ✅ Save back to vehicle_risk table
                    update_sql = """
                        UPDATE vehicle_risk
                        SET suminsured = %s,
                            netpremium = %s,
                            trackerid = %s,
                            model_year = %s,
                            make_name = %s,
                            sub_make_name = %s
                        WHERE LOWER(client_name) = LOWER(%s)
                    """
                    cur.execute(update_sql, (
                        suminsured,
                        netpremium,
                        tracker_id,
                        MODEL_YEAR,
                        MAKE_NAME,
                        SUB_MAKE_NAME,
                        username
                    ))
                    conn.commit()

                    st.success("✅ Vehicle risk table updated with premium info!")

                else:
                    st.warning("⚠️ Sum insured or net premium is zero. Cannot calculate premium rate.")
            else:
                st.warning("❌ No matching record found in both tables. Check your inputs.")

            cur.close()
            conn.close()

        except Exception as e:
            st.error(f"❌ DB Error: {e}")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ Back to Risk"):
            st.session_state.page = "risk_app"
            st.rerun()
    with col2:
        if st.button("⬅️ Back to Main"):
            st.session_state.page = "main"
            st.rerun()

# =====================================
# 🚗 END Premium Rate Block (SAFE ✅)
# =====================================
