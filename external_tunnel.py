#!/usr/bin/env python3
"""
Creates a permanent external URL for the Streamlit app using ngrok
Run this ONCE to get your permanent public link!
"""
import os
import json
import subprocess
import time
from pathlib import Path

# Config file to store the public URL
CONFIG_FILE = Path(__file__).parent / "app_config.json"

def setup_ngrok():
    """Setup ngrok tunnel"""
    try:
        from pyngrok import ngrok
        from pyngrok.exception import PyngrokNgrokError
        
        # Get or prompt for auth token
        config = {}
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
        
        auth_token = config.get('ngrok_token', '').strip()
        
        if not auth_token:
            print("\n" + "="*60)
            print("🔗 SETUP EXTERNAL TUNNEL")
            print("="*60)
            print("\n⚠️  To create a permanent external URL, you need ngrok:")
            print("\n1. Go to: https://dashboard.ngrok.com/signup")
            print("2. Create a FREE account")
            print("3. Copy your Auth Token from: https://dashboard.ngrok.com/auth")
            print("\nPaste your ngrok auth token here:")
            auth_token = input(">>> ").strip()
            
            # Clean the token
            auth_token = auth_token.strip()
            
            if auth_token:
                config['ngrok_token'] = auth_token
                with open(CONFIG_FILE, 'w') as f:
                    json.dump(config, f, indent=2)
                print("✅ Token saved!")
            else:
                print("❌ No token provided. Skipping external tunnel.")
                return None
        
        # Set auth token
        ngrok.set_auth_token(auth_token)
        
        # Create tunnel
        print("\n🌐 Creating permanent external URL...")
        public_url = ngrok.connect(8501, "http")
        
        # Save to config
        config['public_url'] = str(public_url)
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        
        print("\n" + "="*60)
        print("✅ PERMANENT EXTERNAL LINK CREATED!")
        print("="*60)
        print(f"\n🔗 External URL: {public_url}")
        print("\n📌 This URL is PERMANENT and won't change!")
        print("   Share this with anyone to access your app!")
        print("\n" + "="*60)
        
        return public_url
        
    except Exception as e:
        print(f"\n❌ Tunnel setup failed: {e}")
        print("\nAlternative: Use localhost:8501 for local access")
        return None

def show_saved_url():
    """Show saved external URL"""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                if 'public_url' in config:
                    print("\n" + "="*60)
                    print("✅ YOUR PERMANENT EXTERNAL LINK")
                    print("="*60)
                    print(f"\n🔗 {config['public_url']}")
                    print("\n" + "="*60)
                    return config['public_url']
        except:
            pass
    
    return None

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "show":
        show_saved_url()
    else:
        setup_ngrok()
