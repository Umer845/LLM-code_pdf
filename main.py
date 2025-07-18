import streamlit as st
import psycopg2
from werkzeug.security import generate_password_hash, check_password_hash
from app import run_app  # ✅ Make sure app.py has: def run_app(): ...

# ---- DB CONNECTION ----
conn = psycopg2.connect(
    dbname="Surveyor",
    user="postgres",
    password="United2025",
    host="localhost",
    port="5432"
)
cur = conn.cursor()

# ---- SESSION STATE ----
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'page' not in st.session_state:
    st.session_state.page = "login"

# ---- LOGIN PAGE ----
def login():
    st.title("🔐 Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        cur.execute("SELECT password FROM authentication WHERE username = %s", (username,))
        result = cur.fetchone()

        if result and check_password_hash(result[0], password):
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success(f"✅ Welcome, {username}!")
        else:
            st.error("❌ Invalid username or password.")

    if st.button("Register instead"):
        st.session_state.page = "register"

# ---- REGISTRATION PAGE ----
def register():
    st.title("📝 Register")

    username = st.text_input("Username")
    age = st.number_input("Age", min_value=1)
    phone_no = st.text_input("Phone Number")
    password = st.text_input("Password", type="password")

    if st.button("Register"):
        hashed_pw = generate_password_hash(password)
        try:
            cur.execute(
                "INSERT INTO authentication (username, age, phone_no, password) VALUES (%s, %s, %s, %s)",
                (username, age, phone_no, hashed_pw)
            )
            conn.commit()
            st.success("✅ Registration successful! You can now log in.")
            st.session_state.page = "login"
        except Exception as e:
            st.error(f"❌ Error: {e}")

    if st.button("Back to Login"):
        st.session_state.page = "login"

# ---- APP ROUTER ----
if not st.session_state.logged_in:
    if st.session_state.page == "login":
        login()
    elif st.session_state.page == "register":
        register()
else:
    run_app()  # ✅ Run your real app here after login
