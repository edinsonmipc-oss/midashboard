#!/usr/bin/env bash
# regenerate-and-push.sh — regenera el dashboard y lo sube a GitHub Pages
set -e
cd /home/edinsonmipc/dashboard-site

# Regenerar HTML desde los datos JSON
python3 generate.py

# Hacer commit y push a GitHub
git add -A
git commit -m "auto: dashboard actualizado $(date '+%Y-%m-%d %H:%M')" || true
git push

echo "✅ Dashboard actualizado y publicado: $(date)"
