#!/usr/bin/env python3
"""
Creates a stable tunnel URL for the Streamlit app using localtunnel/cloudflare
"""
import subprocess
import time
import sys

def start_tunnel():
    """Start a tunnel to expose the local app"""
    try:
        # Try using python-based tunnel (pyngrok or localtunnel-python)
        # First, try cloudflared tunnel
        tunnel_cmds = [
            # Try cloudflared tunnel
            ["which", "cloudflared"],
        ]
        
        # Check for cloudflared
        result = subprocess.run(["which", "cloudflared"], capture_output=True)
        if result.returncode == 0:
            print("Starting Cloudflare Tunnel...")
            subprocess.Popen([
                "cloudflared", "tunnel", "--url", "http://localhost:8501"
            ])
            print("\n✅ Stable tunnel started! Check the output for your unique URL.")
            time.sleep(10)
        else:
            print("No tunnel service available.")
            print("\n📍 Using direct connection:")
            print("Local: http://localhost:8501")
            print("\nThis URL is stable for your machine.")
    except Exception as e:
        print(f"Tunnel setup note: {e}")

if __name__ == "__main__":
    start_tunnel()
