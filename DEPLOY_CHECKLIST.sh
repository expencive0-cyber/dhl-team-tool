#!/bin/bash
# Quick PythonAnywhere Setup Script

cat << 'EOF'

╔════════════════════════════════════════════════╗
║   🚀 DHLMailShot PythonAnywhere Deployment      ║
╚════════════════════════════════════════════════╝

📋 DEPLOYMENT CHECKLIST:

1️⃣  CREATE ACCOUNT
   └─ Go to: https://www.pythonanywhere.com
   └─ Sign up (FREE account)
   └─ Verify email

2️⃣  UPLOAD CODE
   └─ Log in → Files tab
   └─ Create folder: dhl-team-tool
   └─ Upload all files from workspace

3️⃣  SETUP ENVIRONMENT
   Run in PythonAnywhere Bash Console:
   
   cd ~/dhl-team-tool
   python3.11 -m venv venv
   source venv/bin/activate
   pip install -r requirements-deploy.txt

4️⃣  CREATE WEB APP
   └─ Go to Web tab
   └─ Add new web app
   └─ Choose Python 3.11
   └─ Choose "Streamlit" option
   └─ Set source path: /home/USERNAME/dhl-team-tool

5️⃣  START THE APP
   Run in PythonAnywhere Bash Console:
   
   cd ~/dhl-team-tool
   source venv/bin/activate
   python -m streamlit run app.py --server.port=8501 &

6️⃣  ACCESS YOUR APP
   🌐 https://USERNAME.pythonanywhere.com:8501

═══════════════════════════════════════════════════

💡 PRO TIPS:

✅ For DHL API (requires internet access):
   └─ Upgrade to Beginner Plan ($5/month)

✅ To make app permanent:
   └─ Add to startup script in Web tab

✅ Monitor performance:
   └─ Check "CPU seconds used" in Dashboard

✅ Enable error logging:
   └─ Check logs in Web tab dashboard

═══════════════════════════════════════════════════

FILES READY FOR DEPLOYMENT:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ app.py
✓ auth.py
✓ admin_panel.py
✓ user_management.py
✓ requirements-deploy.txt
✓ .streamlit/config.toml
✓ workflows/
✓ PYTHONANYWHERE_DEPLOY.md (full guide)

═══════════════════════════════════════════════════

🎯 NEXT STEPS:

1. Create PythonAnywhere free account
2. Follow PYTHONANYWHERE_DEPLOY.md for detailed steps
3. Upload files to /home/USERNAME/dhl-team-tool
4. Run setup commands in Bash console
5. Your app will be live!

═══════════════════════════════════════════════════

Questions? See PYTHONANYWHERE_DEPLOY.md

EOF
