import streamlit as st
from user_management import create_user, delete_user, list_all_users

def show_admin_panel():
    """Admin panel for user management"""
    st.write("### 👨‍💼 Admin Panel - User Management")
    
    tab1, tab2, tab3 = st.tabs(["Create User", "Delete User", "View Users"])
    
    with tab1:
        st.write("**Create New User**")
        new_username = st.text_input("New Username:")
        new_password = st.text_input("New Password:", type="password")
        new_role = st.selectbox("User Role:", ["user", "admin"])
        
        if st.button("Create User", use_container_width=True):
            if new_username and new_password:
                success, message = create_user(new_username, new_password, new_role)
                if success:
                    st.success(f"✅ {message}")
                else:
                    st.error(f"❌ {message}")
            else:
                st.warning("⚠️ Please fill in all fields")
    
    with tab2:
        st.write("**Delete User**")
        users = list_all_users()
        user_to_delete = st.selectbox("Select user to delete:", list(users.keys()))
        
        if st.button("Delete User", use_container_width=True, key="delete_btn"):
            success, message = delete_user(user_to_delete)
            if success:
                st.success(f"✅ {message}")
            else:
                st.error(f"❌ {message}")
    
    with tab3:
        st.write("**All Users**")
        users = list_all_users()
        for username, role in users.items():
            st.write(f"👤 {username} - Role: **{role}**")