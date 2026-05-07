#!/bin/bash
# daily-site-maint.sh — Corre a las 7am todos los días
# Mantiene toolshubpro, antoniopaving, primeproperty pulidos

cd /home/edinsonmipc/midashboard

# 1. Email verification
python3 email_verify.py 2>&1 | tail -5

# 2. Health check
python3 healthcheck.py 2>&1 | tail -3

# 3. Tips for improvement (check for issues)
echo "=== HEALTH CHECK ==="
for site in "https://toolshubpro.com.au" "https://antoniopaving.com.au" "https://primepropertymaintenance.au"; do
    status=$(curl -s -o /dev/null -w "%{http_code}" "$site")
    echo "$site -> $status"
done

# 4. Check sitemap health
curl -s https://toolshubpro.com.au/sitemap.xml | grep -oP '<loc>\K[^<]+' | wc -l
echo "urls en sitemap toolshubpro"

# 5. Regenerate dashboard
python3 generate.py 2>&1 | tail -2

# 6. Push to GitHub
git add -A && git commit -m "auto: daily maintenance $(date +%Y-%m-%d)" && git push
echo "Done: $(date)"
