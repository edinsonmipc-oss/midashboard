#!/usr/bin/env python3
"""Dashboard server - runs 24/7 on port 8080"""
import http.server
import socketserver
import os

PORT = 8080
DIR = os.path.dirname(os.path.abspath(__file__))

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIR, **kwargs)
    
    def log_message(self, format, *args):
        print(f"[{self.log_date_time_string()}] {args[0]} {args[1]} {args[2]}")

os.chdir(DIR)
print(f"⚡ Dashboard corriendo en http://0.0.0.0:{PORT}")
print(f"📁 Sirviendo: {DIR}")
print(f"🌐 Accede desde tu celular: http://{PORT}")
print("Presiona Ctrl+C para detener")

with socketserver.TCPServer(("0.0.0.0", PORT), Handler) as httpd:
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nDetenido.")
