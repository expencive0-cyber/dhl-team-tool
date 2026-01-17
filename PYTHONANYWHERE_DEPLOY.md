# DHLMailShot - PythonAnywhere Deployment Guide

## 📋 Quick Setup (10 minutes)

### Step 1: Create PythonAnywhere Account
1. Visit: https://www.pythonanywhere.com/register/free/
2. Sign up with email
3. Verify email

### Step 2: Download Your Code

```bash
# Clone or download your repo
git clone <your-repo-url> dhl-team-tool
cd dhl-team-tool
```

### Step 3: Upload to PythonAnywhere

**Option A: Via Web Interface (Easiest)**
1. Log in to PythonAnywhere Dashboard
2. Click "Files" tab
3. Create folder: `/home/username/dhl-team-tool`
4. Upload all files

**Option B: Via Git (Recommended)**
1. Go to "Consoles" → "Bash"
2. Run:
```bash
cd ~
git clone <your-repo-url> dhl-team-tool
cd dhl-team-tool
```

### Step 4: Install Dependencies

```bash
# In PythonAnywhere Bash Console:
cd ~/dhl-team-tool

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install packages
pip install --upgrade pip
pip install -r requirements-deploy.txt
```

### Step 5: Start Your App

**Option A: Run as Web App (Recommended)**
1. Go to "Web" tab
2. Add new web app
3. Choose "Python 3.11"
4. Choose "Streamlit" or "Manual"
5. When asked for path, enter: `/home/username/dhl-team-tool`

**Option B: Run in Background**
```bash
# In PythonAnywhere Bash Console:
cd ~/dhl-team-tool
source venv/bin/activate
nohup python -m streamlit run app.py --server.port=8501 --server.address=0.0.0.0 > app.log 2>&1 &
```

### Step 6: Access Your App

**Your URL:**
```
https://username.pythonanywhere.com:8501
```

Or use PythonAnywhere's port forwarding to access it on standard port 443.

---

## 🔧 Detailed Configuration

### Configure Streamlit Config
Create `.streamlit/config.toml`:

```toml
[server]
port = 8501
address = 0.0.0.0
runOnSave = true
maxUploadSize = 200

[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#F8F9FA"

[logger]
level = "info"
```

### Set Secrets (for DHL API Key)
Create `.streamlit/secrets.toml`:

```toml
DHL_API_KEY = "your-api-key-here"
```

---

## 📊 PythonAnywhere Account Types

| Feature | Free | Beginner ($5/mo) | Hacker ($25/mo) |
|---------|------|-----------------|-----------------|
| CPU Seconds/day | 100 | Unlimited | Unlimited |
| Disk Space | 512 MB | 1 GB | 1 GB |
| Web Apps | 1 | 1 | 2 |
| Internet Access | ❌ | ✅ | ✅ |
| SSL Certificate | ✅ | ✅ | ✅ |

**Recommendation:** Upgrade to Beginner tier for production use (enables internet access for DHL API).

---

## 🚨 Troubleshooting

### App Not Starting
```bash
# Check logs in PythonAnywhere Web tab
# Or manually check:
tail -f ~/dhl-team-tool/nohup.out
```

### Import Errors
```bash
# Verify venv is activated:
source ~/dhl-team-tool/venv/bin/activate

# Verify packages installed:
pip list

# Check specific package:
python -c "import streamlit; print(streamlit.__version__)"
```

### Permission Denied
```bash
# Fix permissions:
chmod +x ~/dhl-team-tool/app.py
chmod -R 755 ~/dhl-team-tool/
```

### Database/Log Errors
```bash
# Create logs directory if missing:
mkdir -p ~/dhl-team-tool/logs

# Check database:
sqlite3 ~/dhl-team-tool/users.db ".tables"
```

---

## 🌐 Custom Domain (Optional)

1. Go to "Web" tab
2. Click "Add domain"
3. Enter your domain
4. Update DNS records with PythonAnywhere settings
5. Enable HTTPS

---

## 📈 Performance Tips

1. **Optimize uploads:** Limit file size in `config.toml`
2. **Cache results:** Store processed files
3. **Monitor CPU:** Check "Consoles" for usage
4. **Clean logs:** Periodically delete `logs/` folder contents
5. **Restart app weekly:** Prevent memory leaks

---

## 🔐 Security

- ✅ Store sensitive keys in `.streamlit/secrets.toml`
- ✅ Use HTTPS (automatic)
- ✅ Enable 2FA on PythonAnywhere account
- ✅ Keep dependencies updated
- ✅ Monitor access logs

---

## 📞 Support

- **PythonAnywhere Docs:** https://help.pythonanywhere.com
- **Streamlit Docs:** https://docs.streamlit.io
- **GitHub Issues:** Create issue in your repo

---

**Your DHLMailShot App is now live! 🎉**

Permanent URL: `https://username.pythonanywhere.com:8501`
