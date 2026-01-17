import streamlit as st
from user_management import verify_user, get_user_role

def login():
    """Login page"""
    st.write("### 🔐 Login to DHL Team Tool")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        username = st.text_input("Username:")
        password = st.text_input("Password:", type="password")
        
        if st.button("Login", use_container_width=True):
            if verify_user(username, password):
                st.session_state.username = username
                st.session_state.user_role = get_user_role(username)
                st.session_state.logged_in = True
                st.success(f"✅ Welcome, {username}!")
                st.rerun()
            else:
                st.error("❌ Invalid username or password")
    
    with col2:
        st.write("**Demo Credentials:**")
        st.info("""
        - Username: `admin`
        - Password: `admin123`
        
        - Username: `user`
        - Password: `user123`
        """)

def check_login():
    """Check if user is logged in"""
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    
    if not st.session_state.logged_in:
        login()
        st.stop()

def logout():
    """Logout user"""
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.user_role = None
    st.rerun()