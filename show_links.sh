#!/bin/bash
# Setup external tunnel and display all app links

VENV_PYTHON="/workspaces/dhl-team-tool/.venv/bin/python"

echo ""
echo "=========================================="
echo "🚀 DHL MAILSHOT - COMPLETE SETUP"
echo "=========================================="
echo ""

# Show internal links
echo "📍 INTERNAL LINKS (Local Network):"
echo "   • http://localhost:8501"
echo "   • http://dhlmailshot:8501"
echo ""

# Check if external URL already exists
if [ -f "/workspaces/dhl-team-tool/app_config.json" ]; then
    EXTERNAL_URL=$(grep -o '"public_url": "[^"]*"' /workspaces/dhl-team-tool/app_config.json | cut -d'"' -f4)
    if [ ! -z "$EXTERNAL_URL" ]; then
        echo "🌐 EXTERNAL LINK (Share with anyone worldwide):"
        echo "   • $EXTERNAL_URL"
        echo ""
        echo "✅ Your permanent link is ready!"
    fi
else
    echo "🌐 EXTERNAL LINK:"
    echo "   To create a permanent external URL that you can share with anyone:"
    echo "   Run: python3 external_tunnel.py"
    echo ""
fi

echo "📊 APP STATUS:"
pm2 status dhl-team-tool
echo ""
echo "📝 VIEW LOGS:"
echo "   pm2 logs dhl-team-tool"
echo ""
echo "=========================================="
