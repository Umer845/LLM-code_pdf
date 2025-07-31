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

# ---- CUSTOM CSS ----
st.markdown(
    """
    <style>
    .button-row {
        display: flex;
        gap: 8px;
    }
    .top-right {
        position: absolute;
        top: -43px;
        right: -540px;
        background-color: rgb(19, 23, 32);
        border-radius: 4px;
        padding: 5px 29px;
        border: 1px solid rgba(250, 250, 250, 0.2);
    }
    .top-right > a {
        text-decoration: none;
        color: white;
    }
    div.stButton > button {
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ---- LOGOUT BUTTON ----
if st.session_state.logged_in:
    st.markdown(
        '<div class="top-right">'
        '<a href="?logout">Logout</a>'
        '</div>',
        unsafe_allow_html=True
    )
    if st.query_params.get('logout') is not None:
        st.session_state.logged_in = False
        st.session_state.page = "login"
        st.rerun()

# ---- LOGIN PAGE ----
def login():
    st.title("🔐 Login")

    username = st.text_input("Username", placeholder="Enter your username")
    password = st.text_input("Password", type="password", placeholder="Enter your password")

    st.markdown('<div class="button-row">', unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1])

    with col1:
        if st.button("Login"):
            cur.execute("SELECT password FROM authentication WHERE username = %s", (username,))
            result = cur.fetchone()

            if result and check_password_hash(result[0], password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success(f"✅ Welcome, {username}!")
            else:
                st.error("❌ Invalid username or password.")

    with col2:
        if st.button("Register instead"):
            st.session_state.page = "register"
    st.markdown('</div>', unsafe_allow_html=True)

# ---- REGISTRATION PAGE ----
def register():
    st.title("📝 Register")

    username = st.text_input("Username", placeholder="Enter your Username")
    age = st.number_input("Age", min_value=1, placeholder="Enter your Age")
    phone_no = st.text_input("Phone Number", placeholder="Enter your Phone_no")
    password = st.text_input("Password", type="password", placeholder="Enter your Password")

    st.markdown('<div class="button-row">', unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1])

    with col1:
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
            
    with col2:
     if st.button("Back to Login"):
        st.session_state.page = "login"
        st.markdown('</div>', unsafe_allow_html=True)

# ---- APP ROUTER ----
if not st.session_state.logged_in:
    if st.session_state.page == "login":
        login()
    elif st.session_state.page == "register":
        register()
else:
    run_app()  # ✅ Run your real app here after login
