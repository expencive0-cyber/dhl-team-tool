import streamlit as st
from user_management import create_user, delete_user, list_all_users
from pathlib import Path
import os
from datetime import datetime, timedelta
import json
import psutil
import subprocess

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

def get_system_health():
    """Get system health metrics"""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "memory_used_gb": memory.used / (1024**3),
            "memory_total_gb": memory.total / (1024**3),
            "disk_percent": disk.percent,
            "disk_used_gb": disk.used / (1024**3),
            "disk_total_gb": disk.total / (1024**3),
        }
    except:
        return None

def get_process_info():
    """Get current process info"""
    try:
        process = psutil.Process(os.getpid())
        return {
            "pid": process.pid,
            "memory_mb": process.memory_info().rss / (1024**2),
            "cpu_percent": process.cpu_percent(interval=0.1),
            "threads": process.num_threads(),
            "create_time": datetime.fromtimestamp(process.create_time()).strftime("%Y-%m-%d %H:%M:%S")
        }
    except:
        return None

def get_activity_log():
    """Get user activity log"""
    activity_file = Path(".streamlit/activity.json")
    if activity_file.exists():
        try:
            with open(activity_file, 'r') as f:
                return json.load(f)
        except:
            return []
    return []

def log_activity(action, user, details=""):
    """Log user activity"""
    activity_file = Path(".streamlit/activity.json")
    Path(".streamlit").mkdir(exist_ok=True)
    
    activities = get_activity_log()
    activities.append({
        "timestamp": datetime.now().isoformat(),
        "user": user,
        "action": action,
        "details": details
    })
    
    # Keep only last 100 activities
    if len(activities) > 100:
        activities = activities[-100:]
    
    try:
        with open(activity_file, 'w') as f:
            json.dump(activities, f, indent=2)
    except:
        pass

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

def export_data():
    """Export all application data"""
    export_data = {
        "export_time": datetime.now().isoformat(),
        "users": list_all_users(),
        "activity_log": get_activity_log(),
        "system_health": get_system_health(),
    }
    return json.dumps(export_data, indent=2)


def show_admin_panel():
    """Admin panel for user management and monitoring"""
    st.write("### 👨‍💼 Admin Panel")
    
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "👥 Users", 
        "📊 Statistics", 
        "📁 Files", 
        "📝 Logs",
        "💻 System",
        "📈 Activity",
        "⚙️ Tools"
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
    
    # TAB 6: System Health & Performance
    with tab6:
        st.write("**System Health Monitoring**")
        
        health = get_system_health()
        
        if health:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("CPU Usage", f"{health['cpu_percent']}%", delta="Live")
            
            with col2:
                st.metric("Memory Usage", 
                         f"{health['memory_percent']}%", 
                         f"{health['memory_used_gb']:.2f}/{health['memory_total_gb']:.2f}GB")
            
            with col3:
                st.metric("Disk Usage", 
                         f"{health['disk_percent']}%",
                         f"{health['disk_used_gb']:.2f}/{health['disk_total_gb']:.2f}GB")
            
            # Charts
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Resource Usage**")
                resource_data = {
                    "CPU": health['cpu_percent'],
                    "Memory": health['memory_percent'],
                    "Disk": health['disk_percent']
                }
                st.bar_chart(resource_data)
            
            with col2:
                st.write("**Process Information**")
                process_info = get_process_info()
                if process_info:
                    st.write(f"**Process ID:** {process_info['pid']}")
                    st.write(f"**Memory:** {process_info['memory_mb']:.2f} MB")
                    st.write(f"**CPU:** {process_info['cpu_percent']:.1f}%")
                    st.write(f"**Threads:** {process_info['threads']}")
                    st.write(f"**Started:** {process_info['create_time']}")
        else:
            st.warning("⚠️ Could not retrieve system metrics")
    
    # TAB 7: Activity Log
    with tab7:
        st.write("**User Activity Log**")
        
        activities = get_activity_log()
        
        if activities:
            # Show last activities first
            for activity in reversed(activities[-20:]):
                timestamp = activity.get('timestamp', 'Unknown')
                user = activity.get('user', 'Unknown')
                action = activity.get('action', 'Unknown')
                details = activity.get('details', '')
                
                with st.container():
                    col1, col2, col3 = st.columns([2, 2, 2])
                    with col1:
                        st.write(f"**{user}**")
                    with col2:
                        st.write(f"*{action}*")
                    with col3:
                        st.write(f"⏰ {timestamp[:19]}")
                    if details:
                        st.caption(f"📝 {details}")
                    st.divider()
        else:
            st.info("📭 No activity recorded yet")
        
        # Export activity
        if st.button("📥 Download Activity Log", use_container_width=True):
            activity_json = json.dumps(activities, indent=2)
            st.download_button(
                label="Download JSON",
                data=activity_json,
                file_name=f"activity_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    # TAB 8: Tools & Utilities
    with tab5:
        st.write("**Admin Tools**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Application Info**")
            st.info("""
            **DHLMailShot v1.0**
            
            - Framework: Streamlit
            - Deployment: Streamlit Cloud
            - Repository: GitHub
            - Status: ✅ Active
            """)
        
        with col2:
            st.write("**Quick Actions**")
            if st.button("🔄 Refresh Dashboard", use_container_width=True):
                st.rerun()
            
            if st.button("📋 System Information", use_container_width=True):
                st.write(f"**Python Version:** {__import__('sys').version}")
                st.write(f"**Streamlit Version:** {__import__('streamlit').__version__}")
                st.write(f"**Current Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                st.write(f"**Platform:** {__import__('platform').system()}")
        
        st.divider()
        st.write("**Data Management**")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📤 Export All Data", use_container_width=True):
                data = export_data()
                st.download_button(
                    label="Download JSON Export",
                    data=data,
                    file_name=f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
        
        with col2:
            if st.button("🔐 Export Users", use_container_width=True):
                users_data = json.dumps(list_all_users(), indent=2)
                st.download_button(
                    label="Download Users JSON",
                    data=users_data,
                    file_name=f"users_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
        
        with col3:
            if st.button("📊 Export Logs", use_container_width=True):
                logs = "\n".join(get_app_logs(200))
                st.download_button(
                    label="Download Logs TXT",
                    data=logs,
                    file_name=f"logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain"
                )
        
        st.divider()
        st.write("**⚠️ Danger Zone**")
        st.warning("Advanced operations - use with caution!")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🗑️ Clear Logs", use_container_width=True):
                try:
                    import shutil
                    if Path("logs").exists():
                        shutil.rmtree("logs")
                        Path("logs").mkdir()
                    st.success("✅ Logs cleared")
                except Exception as e:
                    st.error(f"❌ Error: {e}")
        
        with col2:
            if st.button("🗑️ Clear Activity", use_container_width=True):
                try:
                    activity_file = Path(".streamlit/activity.json")
                    if activity_file.exists():
                        activity_file.unlink()
                    st.success("✅ Activity log cleared")
                except Exception as e:
                    st.error(f"❌ Error: {e}")
        
        with col3:
            if st.button("🔄 Restart App", use_container_width=True):
                st.warning("⚠️ App will restart. This will disconnect all users.")
                if st.button("Confirm Restart", key="confirm_restart"):
                    st.rerun()

