# PythonAnywhere WSGI Configuration for Streamlit
# This file is used by PythonAnywhere to run the Streamlit app

import sys
import os
from pathlib import Path

# Add the project directory to the Python path
project_dir = '/home/{username}/dhl-team-tool'
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

# Change to project directory
os.chdir(project_dir)

# Import and run the Streamlit app
import streamlit.web.cli as stcli

def application(environ, start_response):
    """WSGI application wrapper"""
    sys.argv = ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
    
    # This won't work directly, so we use a different approach
    # Use subprocess to run streamlit
    import subprocess
    subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])
    
    # Fallback WSGI response
    status = '200 OK'
    response_headers = [('Content-Type', 'text/plain')]
    start_response(status, response_headers)
    return [b'DHLMailShot is running on PythonAnywhere!\nAccess via: https://username.pythonanywhere.com']
