#!/bin/bash
HOST="153.92.8.188"
USER="u228844205.toolshubpro"
PASS="K7!mQ2#vL9@pX4$z"
BASE="ftp://$HOST"

echo "=== Uploading index.html ==="
curl -s --user "$USER:$PASS" -T ~/midashboard/index.html "$BASE/dashboard/index.html" --ftp-create-dirs

echo "=== Uploading data.js ==="
curl -s --user "$USER:$PASS" -T ~/midashboard/data.js "$BASE/dashboard/data.js" --ftp-create-dirs

echo "=== Verify ==="
curl -sL https://toolshubpro.com.au/dashboard/ | grep -c "QA Scan"
