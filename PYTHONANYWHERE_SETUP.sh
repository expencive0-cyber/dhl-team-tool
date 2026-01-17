#!/bin/bash
# PythonAnywhere Deployment Guide for DHLMailShot

cat << 'EOF'

========================================
🚀 DHLMailShot - PythonAnywhere Deployment
========================================

STEP 1: Create PythonAnywhere Account
=====================================
1. Go to: https://www.pythonanywhere.com
2. Sign up (FREE account available)
3. Confirm your email

STEP 2: Upload Your Code
========================
1. Log in to PythonAnywhere Dashboard
2. Go to "Files" tab
3. Create new folder: "dhl-team-tool"
4. Upload all files from your repo:
   - app.py
   - auth.py
   - admin_panel.py
   - user_management.py
   - requirements-deploy.txt
   - workflows/ (entire folder)
   - logs/ (create empty folder)

STEP 3: Create Virtual Environment
===================================
1. Go to "Web" tab → "Add a new web app"
2. Choose "Python 3.11"
3. Select "Manual configuration"
4. Choose "Streamlit" (if available) or "Python web framework"

STEP 4: Install Dependencies
============================
1. Go to "Consoles" tab
2. Click "Bash console"
3. Run these commands:

   cd /home/YOUR_USERNAME/dhl-team-tool
   python3.11 -m venv venv
   source venv/bin/activate
   pip install -r requirements-deploy.txt

STEP 5: Configure Web App
=========================
1. Go to "Web" tab → Edit configuration
2. Set "Source code:" to /home/YOUR_USERNAME/dhl-team-tool
3. Set "Working directory:" to /home/YOUR_USERNAME/dhl-team-tool
4. Set "Virtualenv path:" to /home/YOUR_USERNAME/dhl-team-tool/venv

STEP 6: Create WSGI File
=======================
1. In Web tab, click "WSGI configuration file"
2. Edit the file and add streamlit startup script

STEP 7: Run Streamlit as Background Task
========================================
1. Go to "Consoles" → "Bash console"
2. Run:
   
   cd /home/YOUR_USERNAME/dhl-team-tool
   source venv/bin/activate
   python -m streamlit run app.py --server.port=8501 --server.address=0.0.0.0 &

STEP 8: Access Your App
=======================
Your app will be available at:
🌐 https://YOUR_USERNAME.pythonanywhere.com:8501

Or forward the port through PythonAnywhere's web interface.

========================================
IMPORTANT NOTES:
========================================
✅ Free tier includes:
   - 1 web app
   - 100MB disk space (may need upgrade)
   - Monthly usage limits
   - 1 year validity

❌ Limitations:
   - Free account may need upgrade for larger files
   - Internet access requires paid account
   - Some background tasks may timeout

💡 Recommended:
   - Use Paid tier for production ($5+/month)
   - Set up domain name
   - Enable HTTPS automatically

========================================

EOF
