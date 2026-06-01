#!/usr/bin/env bash
# regenerate-and-push.sh — genera leads, regenera el dashboard y lo sube a GitHub Pages
set -e
cd /home/edinsonmipc/midashboard

# 1. Generar nuevos leads (10 por ejecución)
python3 leadgen.py

# 2. Generar health check
python3 healthcheck.py || true

# 3. Regenerar HTML desde los datos JSON
python3 generate.py

# 4. Hacer commit y push a GitHub
git add -A
git commit -m "auto: dashboard actualizado $(date '+%Y-%m-%d %H:%M')" || true
git push 2>&1 || echo "⚠️ Push falló (puede ser por merge) - intentando pull+push..."
git pull --rebase 2>&1 || true
git push 2>&1 || echo "⚠️ Segundo push también falló"

echo "✅ Dashboard actualizado y publicado: $(date)"
