# Online Users & Session Tracking

## Overview
Added comprehensive real-time tracking of online users, their file uploads, and generated outputs. Admins can now monitor active sessions and user activity in the new **"🌐 Online Users"** tab.

## Features Added

### 1. **Session Management** 
- Tracks when users login/logout
- Records session duration
- Monitors last activity timestamp
- Automatically marks users offline after 15+ minutes of inactivity

**Files:**
- `.streamlit/sessions.json` - Stores active user sessions

**Functions in `admin_panel.py`:**
- `track_user_session(username, action)` - Records login, logout, and activity
- `get_online_users()` - Returns list of currently online users

### 2. **File Upload Tracking**
- Records all uploaded files per user
- Tracks file size and upload timestamp
- Records workflow type for each upload
- Keeps last 50 uploads per user

**Files:**
- `.streamlit/uploads.json` - Stores file upload history

**Functions in `admin_panel.py`:**
- `track_file_upload(username, filename, filesize_mb, workflow_type)` - Records uploads
- `get_user_uploads(username)` - Retrieves user's upload history

**Changes in `app.py`:**
- Modified `save_uploaded()` function to automatically call `track_file_upload()`
- Tracks username with each upload

### 3. **Output File Tracking**
- Monitors generated output files from workflows
- Records file size and creation timestamp
- Groups by workflow type

**Functions in `admin_panel.py`:**
- `get_output_files()` - Lists all generated output files

### 4. **New Admin Tab: "🌐 Online Users"**

The new tab displays:

#### **Dashboard Metrics**
- 👥 Number of online users
- 📤 Total uploads tracked
- 📥 Number of output files

#### **Currently Online Users**
Shows active users with:
- Username
- Login time (HH:MM format)
- Session duration (HH:MM:SS)
- Last activity timestamp
- Recent uploads (up to 5 most recent)

#### **Upload Summary**
- Bar chart showing upload count per user
- Expandable sections per user showing upload details
- Click to expand and see last 10 uploads with timestamps and file sizes

#### **Generated Output Files**
- Lists all generated output files
- Shows file size and creation timestamp
- Tracks the last 10 output files

## Session Tracking Logic

### Login Process
1. User enters credentials and clicks Login
2. `check_login()` validates credentials
3. `track_user_session(username, "login")` records the session
4. Session data stored: `{"username": {"login_time": "...", "last_activity": "...", "status": "online"}}`

### Activity Tracking
1. Every file upload updates `last_activity` timestamp
2. Action tracked: `track_user_session(username, "activity")`
3. Inactivity detection: Users offline after 15+ minutes without activity

### Logout Process
1. User clicks "Logout" button
2. `track_user_session(username, "logout")` records logout
3. Session status changed to "offline"
4. `logout_time` recorded

## File Upload Tracking Logic

When a user uploads a file:
1. File saved to temporary directory
2. File size calculated in MB
3. `track_file_upload()` called with:
   - Username (from `st.session_state.username`)
   - Filename (original upload name)
   - File size in MB
   - Workflow type (currently "workflow")

Upload data stored: `{"username": [{"timestamp": "...", "filename": "...", "size_mb": "...", "workflow": "..."}]}`

## Data Files

### `.streamlit/sessions.json`
```json
{
  "mabuzeid": {
    "login_time": "2025-01-17T14:23:45.123456",
    "last_activity": "2025-01-17T14:28:12.654321",
    "status": "online"
  },
  "user2": {
    "login_time": "2025-01-17T10:15:00.000000",
    "logout_time": "2025-01-17T11:30:22.000000",
    "status": "offline"
  }
}
```

### `.streamlit/uploads.json`
```json
{
  "mabuzeid": [
    {
      "timestamp": "2025-01-17T14:24:30.123456",
      "filename": "data.xlsx",
      "size_mb": "2.45",
      "workflow": "workflow"
    }
  ]
}
```

## Real-Time Updates

The admin panel automatically refreshes and shows:
- Live online user count
- Current session durations (updated in real-time)
- Upload activity as it happens
- Output file creation

Refresh interval is handled by Streamlit's built-in state management.

## Admin Panel Integration

The "🌐 Online Users" tab is accessible only to admin users and appears as the 8th tab in the admin panel alongside:
1. 👥 Users (user management)
2. 📊 Statistics (app statistics)
3. 📁 Files (uploaded files)
4. 📝 Logs (application logs)
5. 💻 System (system health)
6. 📈 Activity (activity log)
7. ⚙️ Tools (export/admin tools)
8. 🌐 Online Users (NEW - session tracking)

## Usage

### For Admins
1. Log in to the app
2. Navigate to the Admin Panel
3. Click on "🌐 Online Users" tab
4. View:
   - All currently online users
   - Their login times and session durations
   - Files they've uploaded
   - Output files they've created
   - Upload statistics charts

### For Regular Users
- Just use the app normally
- Session tracking happens automatically
- File uploads automatically recorded
- No manual configuration needed

## Benefits

✅ **Real-time Monitoring** - See who's working right now
✅ **Activity Audit Trail** - Track user actions and uploads
✅ **Performance Insights** - Identify heavy users
✅ **File Tracking** - Know what files were processed
✅ **Output Management** - Track generated results
✅ **Session Management** - Automatic inactivity detection
✅ **No Performance Impact** - Lightweight JSON storage

## Future Enhancements

Potential additions:
- Export session reports
- User activity graphs
- Workflow-specific file tracking
- Session timeout configuration
- Email notifications for important uploads
- User activity filtering by date/time
- Download history per user
