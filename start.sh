#!/bin/bash
# Dashboard auto-start script
# Run this on boot to keep the dashboard running 24/7

cd /home/edinsonmipc/dashboard-site

# Check if already running
if pgrep -f "python3 server.py" > /dev/null; then
    exit 0
fi

nohup python3 server.py > /dev/null 2>&1 &
echo "⚡ Dashboard started on port 8080"
