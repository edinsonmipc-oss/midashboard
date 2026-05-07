#!/bin/bash
# daily-site-maint.sh — Corre todos los días a las 8am
# Verifica emails, health de sitios, mejora continua

cd /home/edinsonmipc/midashboard

# 1. Email verification de leads nuevos
python3 email_verify.py 2>&1 | tail -3

# 2. Health check de todos los sitios
python3 healthcheck.py 2>&1 | tail -3

# 3. Verificar HTTP status de los 3 sitios principales
for site in "https://toolshubpro.com.au" "https://antoniopaving.com.au" "https://primepropertymaintenance.au"; do
    status=$(curl -s -o /dev/null -w "%{http_code}" "$site")
    echo "  $site -> $status"
done

# 4. Verificar sitemaps
curl -s https://toolshubpro.com.au/sitemap.xml | grep -oP '<loc>\K[^<]+' | wc -l | xargs echo "  toolshubpro sitemap:"

# 5. Regenerar dashboard + push
python3 generate.py 2>&1 | tail -1
git add -A && git commit -m "auto: daily maint $(date +%Y-%m-%d)" && git push

echo "✅ Mantenimiento diario completo: $(date)"
