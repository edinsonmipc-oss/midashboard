#!/bin/bash
# daily-site-maint.sh — Corre todos los días a las 8am
# Verifica emails, health de sitios, mejora continua

cd /home/edinsonmipc/midashboard

DATE=$(date '+%Y-%m-%d %H:%M')
echo "[$DATE] 🌅 Daily Site Maintenance - Starting..."

# 1. Email verification de leads nuevos
python3 email_verify.py 2>&1 | tail -3

# 2. Health check de todos los sitios
python3 healthcheck.py 2>&1 | tail -3

# 3. SEO quick check (homepage + sitemap)
python3 seo_agent.py --quick 2>&1 | tail -5

# 4. Auto-email dry-run (send batch if password configured)
python3 auto_send.py --dry-run 2>&1 | tail -3

# 5. Verificar HTTP status de los sitios principales
for site in "https://toolshubpro.com.au" "https://antoniopaving.com" "https://primepropertymaintenance.au"; do
    status=$(curl -s -o /dev/null -w "%{http_code}" "$site")
    echo "  $site -> $status"
done

# 6. Regenerar dashboard + push
python3 generate.py 2>&1 | tail -1
cd /home/edinsonmipc/midashboard
git add -A
git commit -m "auto: daily maint $(date +%Y-%m-%d)" 2>/dev/null || true
git pull --rebase 2>/dev/null || true
git push 2>/dev/null || true

echo "[$DATE] ✅ Mantenimiento diario completo"
