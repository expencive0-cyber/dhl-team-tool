import streamlit as st
import hashlib
import json
import os
from datetime import datetime

USERS_FILE = ".streamlit/users.json"

def hash_password(password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    """Load users from JSON file"""
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    """Save users to JSON file"""
    os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=4)

def create_user(username, password, role="user"):
    """Create a new user"""
    users = load_users()
    
    if username in users:
        return False, "User already exists"
    
    users[username] = {
        "password_hash": hash_password(password),
        "role": role,
        "created_at": datetime.now().isoformat()
    }
    
    save_users(users)
    return True, "User created successfully"

def verify_user(username, password):
    """Verify user credentials"""
    users = load_users()
    
    if username not in users:
        return False
    
    password_hash = hash_password(password)
    return users[username]["password_hash"] == password_hash

def get_user_role(username):
    """Get user role"""
    users = load_users()
    return users.get(username, {}).get("role", "user")

def delete_user(username):
    """Delete a user"""
    users = load_users()
    
    if username not in users:
        return False, "User not found"
    
    del users[username]
    save_users(users)
    return True, "User deleted successfully"

def list_all_users():
    """List all users (for admin only)"""
    users = load_users()
    return {username: user.get("role") for username, user in users.items()}