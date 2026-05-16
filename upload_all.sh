#!/bin/bash
HOST="153.92.8.188"
USER="u228844205.toolshubpro"
PASS="P8c$J5v#M2uX7aQ4"
BASE="ftp://$HOST"

# Create directories
curl -s --user "$USER:$PASS" ftp://$HOST/ -X "MKD dashboard" 2>/dev/null || true
curl -s --user "$USER:$PASS" ftp://$HOST/ -X "MKD dashboard/data" 2>/dev/null || true

# Upload index.html
echo "=== Uploading index.html ==="
curl -s --user "$USER:$PASS" -T index.html "$BASE/dashboard/index.html" --ftp-create-dirs
echo ""

# Upload data.js
echo "=== Uploading data.js ==="
curl -s --user "$USER:$PASS" -T data.js "$BASE/dashboard/data.js" --ftp-create-dirs
echo ""

# Upload all JSON files
echo "=== Uploading data/*.json ==="
for f in data/*.json; do
  echo -n "  $f -> /dashboard/$f ... "
  curl -s --user "$USER:$PASS" -T "$f" "$BASE/dashboard/$f" --ftp-create-dirs
  echo "OK"
done
echo "=== Done uploading ==="
