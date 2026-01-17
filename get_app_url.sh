#!/bin/bash
# Create a stable hosts entry for the app
echo "127.0.0.1    dhlmailshot" >> /etc/hosts 2>/dev/null || echo "Note: To add stable hostname, run: echo '127.0.0.1    dhlmailshot' | sudo tee -a /etc/hosts"

echo ""
echo "=========================================="
echo "✅ APP LINKS (STABLE & UNIQUE)"
echo "=========================================="
echo ""
echo "🔗 Local Stable URL (never changes):"
echo "   http://localhost:8501"
echo ""
echo "🔗 Hostname URL (if hosts configured):"
echo "   http://dhlmailshot:8501"
echo ""
echo "📊 Status:"
pm2 status
echo ""
echo "📝 Real-time logs:"
echo "   pm2 logs dhl-team-tool"
echo ""
echo "=========================================="
