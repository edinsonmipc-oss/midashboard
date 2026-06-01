#!/usr/bin/env python3
import urllib.request
req = urllib.request.urlopen("http://toolshubpro.com.au/dashboard/", timeout=15)
html = req.read().decode()
count = html.count("PrimeHermes Dashboard")
print(f"Found {count} occurrences of 'PrimeHermes Dashboard'")
if count >= 1:
    print("VERIFICATION PASSED")
else:
    print("VERIFICATION FAILED")
