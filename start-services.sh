#!/usr/bin/env bash
# start-services.sh — Inicia todos los servicios para ToolshubPro
# Ejecuta esto cada vez que enciendas el PC
set -e

echo "🚀 Iniciando servicios ToolshubPro..."
DIR="$(cd "$(dirname "$0")" && pwd)"

# 1. Dashboard server (port 8080)
echo "📊 Iniciando Dashboard en puerto 8080..."
kill $(lsof -t -i:8080) 2>/dev/null || true
python3 "$DIR/server.py" 8080 &
DASH_PID=$!
echo "   PID: $DASH_PID"

# 2. Downloader API server (port 8081)
echo "⬇️  Iniciando Downloader API en puerto 8081..."
kill $(lsof -t -i:8081) 2>/dev/null || true
python3 "$DIR/downloader-server.py" &
DL_PID=$!
echo "   PID: $DL_PID"

sleep 2

# 3. Cloudflare tunnels
echo "🔗 Iniciando Cloudflare Tunnels..."

# Tunnel for Dashboard (port 8080)
/tmp/cloudflared tunnel --url http://localhost:8080 2>/dev/null &
CF_DASH_PID=$!
echo "   Dashboard tunnel PID: $CF_DASH_PID"

sleep 3

# Tunnel for Downloader API (port 8081)
/tmp/cloudflared tunnel --url http://localhost:8081 2>/dev/null &
CF_DL_PID=$!
echo "   Downloader tunnel PID: $CF_DL_PID"

echo ""
echo "✅ Servicios iniciados. Espera 10 segundos y verifica en el dashboard."
echo ""
echo "📋 Para ver las URLs de los túneles:"
echo "   cat /tmp/cloudflared.log | grep -o 'https://[a-z-]*\.trycloudflare\.com'"
echo "   cat /tmp/cloudflared-downloader.log | grep -o 'https://[a-z-]*\.trycloudflare\.com'"
echo ""
echo "⚠️  Si las URLs cambian, actualiza TH_API_URL en:"
echo "   $DIR/../toolshubpro_site/tools/youtube-to-mp4.html"
echo "   $DIR/../toolshubpro_site/tools/youtube-to-mp3.html"
echo ""
echo "Presiona Ctrl+C para detener todo"
wait
