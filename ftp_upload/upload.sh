#!/usr/bin/env lftp
set ftp:ssl-allow no
set ssl:verify-certificate no
open -u "u228844205.toolshubpro","K7!mQ2#vL9@pX4$z" 153.92.8.188
mkdir -p /dashboard
mkdir -p /dashboard/data
cd /dashboard
put -O / index.html
put -O / data.js
cd data
mput -O / ~/midashboard/data/*.json
quit
