#!/bin/bash
# Quick setup for DHLMailShot external tunnel

echo ""
echo "=========================================="
echo "🚀 DHLMailShot - External Tunnel Setup"
echo "=========================================="
echo ""
echo "Step 1: Get your ngrok auth token"
echo "   → Go to: https://dashboard.ngrok.com/auth"
echo "   → Copy your AUTH TOKEN"
echo ""
echo "Step 2: Run this command:"
echo '   export NGROK_TOKEN="your_token_here"'
echo "   python3 external_tunnel.py"
echo ""
echo "Or simply run:"
echo "   python3 -c \"from external_tunnel import setup_ngrok; setup_ngrok()\""
echo ""
echo "=========================================="
