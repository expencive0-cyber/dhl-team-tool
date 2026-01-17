import streamlit as st
from user_management import create_user, delete_user, list_all_users
from pathlib import Path
import os
from datetime import datetime
import json

def get_app_logs(lines=50):
    """Get recent app logs"""
    log_files = list(Path("logs").glob("*.log")) if Path("logs").exists() else []
    if not log_files:
        return []
    
    # Get the most recent log file
    latest_log = max(log_files, key=os.path.getctime)
    try:
        with open(latest_log, 'r') as f:
            all_lines = f.readlines()
            return all_lines[-lines:]
    except:
        return []

def get_uploaded_files():
    """Get list of uploaded files"""
    uploaded_files = []
    if Path("logs").exists():
        # Check temp directories for uploaded files
        temp_dirs = list(Path("/tmp").glob("dhl_team_tool_*"))
        for temp_dir in temp_dirs[-10:]:  # Last 10 uploads
            files = list(temp_dir.glob("*"))
            for file in files:
                if file.is_file():
                    size_mb = file.stat().st_size / (1024 * 1024)
                    mod_time = datetime.fromtimestamp(file.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                    uploaded_files.append({
                        "name": file.name,
                        "size_mb": f"{size_mb:.2f}",
                        "uploaded": mod_time,
                        "path": str(file)
                    })
    return uploaded_files

def get_session_stats():
    """Get session statistics"""
    # Try to read from a stats file if it exists
    stats_file = Path(".streamlit/session_stats.json")
    if stats_file.exists():
        try:
            with open(stats_file, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def show_admin_panel():
    """Admin panel for user management and monitoring"""
    st.write("### 👨‍💼 Admin Panel")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "👥 Users", 
        "📊 Statistics", 
        "📁 Uploaded Files", 
        "📝 Logs",
        "⚙️ Settings"
    ])
    
    # TAB 1: User Management
    with tab1:
        st.write("**Manage Users**")
        subtab1, subtab2, subtab3 = st.columns(3)
        
        with subtab1:
            st.write("#### Create User")
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
        
        with subtab2:
            st.write("#### Delete User")
            users = list_all_users()
            if users:
                user_to_delete = st.selectbox("Select user to delete:", list(users.keys()))
                
                if st.button("Delete User", use_container_width=True, key="delete_btn"):
                    success, message = delete_user(user_to_delete)
                    if success:
                        st.success(f"✅ {message}")
                    else:
                        st.error(f"❌ {message}")
            else:
                st.info("No users found")
        
        with subtab3:
            st.write("#### All Users")
            users = list_all_users()
            if users:
                for username, user_data in users.items():
                    role = user_data if isinstance(user_data, str) else user_data.get("role", "user")
                    st.write(f"👤 **{username}** - Role: `{role}`")
            else:
                st.info("No users found")
    
    # TAB 2: Statistics
    with tab2:
        st.write("**Application Statistics**")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            users = list_all_users()
            st.metric("Total Users", len(users))
        
        with col2:
            uploaded_files = get_uploaded_files()
            st.metric("Files Processed", len(uploaded_files))
        
        with col3:
            # Check if log files exist
            log_files = list(Path("logs").glob("*.log")) if Path("logs").exists() else []
            st.metric("Log Files", len(log_files))
        
        with col4:
            # Get current session info
            if "username" in st.session_state:
                st.metric("Current User", st.session_state.username)
            else:
                st.metric("Current User", "Guest")
        
        # Session details
        st.write("**Session Details**")
        session_info = {
            "Session User": st.session_state.get("username", "Unknown"),
            "User Role": st.session_state.get("user_role", "Unknown"),
            "Login Status": "✅ Logged In" if st.session_state.get("logged_in") else "❌ Not Logged In",
            "Session Started": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        for key, value in session_info.items():
            st.write(f"**{key}:** {value}")
    
    # TAB 3: Uploaded Files
    with tab3:
        st.write("**Recently Uploaded Files**")
        uploaded_files = get_uploaded_files()
        
        if uploaded_files:
            # Create dataframe-like display
            for file_info in uploaded_files:
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.write(f"📄 {file_info['name']}")
                with col2:
                    st.write(f"Size: {file_info['size_mb']} MB")
                with col3:
                    st.write(f"⏰ {file_info['uploaded']}")
        else:
            st.info("📭 No uploaded files yet")
        
        # File statistics
        st.write("**File Statistics**")
        if uploaded_files:
            total_size = sum(float(f['size_mb']) for f in uploaded_files)
            st.write(f"Total Files: {len(uploaded_files)}")
            st.write(f"Total Size: {total_size:.2f} MB")
            st.write(f"Average Size: {total_size/len(uploaded_files):.2f} MB")
    
    # TAB 4: Logs
    with tab4:
        st.write("**Application Logs**")
        
        log_level = st.selectbox("Filter by type:", ["All", "Errors", "Info", "Debug"])
        lines_to_show = st.slider("Number of lines to display:", 10, 200, 50)
        
        logs = get_app_logs(lines_to_show)
        
        if logs:
            log_text = "".join(logs)
            
            # Filter logs
            if log_level != "All":
                log_text = "\n".join([
                    line for line in log_text.split("\n") 
                    if log_level.lower() in line.lower()
                ])
            
            st.code(log_text, language="text")
            
            # Download logs button
            if st.button("📥 Download Logs"):
                st.download_button(
                    label="Download as TXT",
                    data=log_text,
                    file_name=f"app_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain"
                )
        else:
            st.info("📭 No logs available")
    
    # TAB 5: Settings
    with tab5:
        st.write("**Admin Settings**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Application Info**")
            st.info("""
            **DHLMailShot v1.0**
            
            - Framework: Streamlit
            - Platform: Streamlit Cloud
            - Deployment: GitHub
            - Status: ✅ Active
            """)
        
        with col2:
            st.write("**Quick Actions**")
            if st.button("🔄 Refresh Statistics", use_container_width=True):
                st.rerun()
            
            if st.button("📋 View System Info", use_container_width=True):
                st.write(f"Python Version: {__import__('sys').version}")
                st.write(f"Streamlit Version: {__import__('streamlit').__version__}")
                st.write(f"Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Danger Zone
        st.write("**⚠️ Danger Zone**")
        st.warning("Advanced operations that may affect the application")
        
        if st.button("Clear All Logs", use_container_width=True):
            try:
                import shutil
                if Path("logs").exists():
                    shutil.rmtree("logs")
                    Path("logs").mkdir()
                st.success("✅ Logs cleared")
            except Exception as e:
                st.error(f"❌ Error: {e}")
