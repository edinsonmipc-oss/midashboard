#!/usr/bin/env python3
"""downloader-server.py — API de descarga de YouTube usando yt-dlp"""
import http.server
import json
import urllib.parse
import subprocess
import re
import os

PORT = 8081
DIR = os.path.dirname(os.path.abspath(__file__))
DOWNLOAD_DIR = os.path.join(DIR, "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def extract_video_id(url):
    patterns = [
        r'youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})',
        r'youtu\.be/([a-zA-Z0-9_-]{11})',
        r'youtube\.com/embed/([a-zA-Z0-9_-]{11})',
        r'youtube\.com/shorts/([a-zA-Z0-9_-]{11})',
    ]
    for p in patterns:
        m = re.search(p, url)
        if m:
            return m.group(1)
    return None

def get_download_url(video_url, quality="480"):
    """Get downloadable URL from yt-dlp"""
    format_map = {"360": "best[height<=360]", "480": "best[height<=480]", 
                  "720": "best[height<=720]", "1080": "best[height<=1080]"}
    fmt = format_map.get(quality, "best[height<=480]")
    
    result = subprocess.run(
        ["yt-dlp", "-f", fmt, "--get-url", video_url],
        capture_output=True, text=True, timeout=30
    )
    if result.returncode != 0:
        raise Exception(result.stderr.strip())
    return result.stdout.strip()

def get_video_info(video_url):
    """Get video info using yt-dlp"""
    result = subprocess.run(
        ["yt-dlp", "--print", "%(title)s|%(uploader)s|%(thumbnail)s", video_url],
        capture_output=True, text=True, timeout=30
    )
    if result.returncode != 0:
        raise Exception(result.stderr.strip())
    parts = result.stdout.strip().split("|", 2)
    return {
        "title": parts[0] if len(parts) > 0 else "Video",
        "author": parts[1] if len(parts) > 1 else "YouTube",
        "thumbnail": parts[2] if len(parts) > 2 else f"https://img.youtube.com/vi/{extract_video_id(video_url)}/mqdefault.jpg"
    }

class Handler(http.server.BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/info":
            # GET /api/info?url=https://...
            qs = urllib.parse.parse_qs(parsed.query)
            url = qs.get("url", [""])[0]
            video_id = extract_video_id(url)
            if not video_id:
                self.send_json({"error": "Invalid YouTube URL"}, 400)
                return
            try:
                info = get_video_info(url)
                info["video_id"] = video_id
                info["thumbnail"] = f"https://img.youtube.com/vi/{video_id}/mqdefault.jpg"
                self.send_json(info)
            except Exception as e:
                # Fallback
                self.send_json({
                    "video_id": video_id,
                    "title": "YouTube Video",
                    "author": "YouTube",
                    "thumbnail": f"https://img.youtube.com/vi/{video_id}/mqdefault.jpg"
                })
        else:
            self.send_json({"error": "Not found"}, 404)

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length > 0 else b"{}"
        data = json.loads(body) if body else {}
        
        parsed = urllib.parse.urlparse(self.path)
        
        if parsed.path == "/api/download":
            url = data.get("url", "")
            quality = data.get("quality", "480")
            video_id = extract_video_id(url)
            
            if not video_id:
                self.send_json({"error": "Invalid YouTube URL"}, 400)
                return
            
            try:
                download_url = get_download_url(url, quality)
                info = get_video_info(url)
                self.send_json({
                    "success": True,
                    "download_url": download_url,
                    "video_id": video_id,
                    "title": info["title"],
                    "author": info["author"]
                })
            except Exception as e:
                self.send_json({"error": str(e)}, 500)
        else:
            self.send_json({"error": "Not found"}, 404)

    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def log_message(self, format, *args):
        print(f"[{self.log_date_time_string()}] {args[0]} {args[1]} {args[2]}")

os.chdir(DIR)
print(f"⚡ Downloader API corriendo en http://0.0.0.0:{PORT}")
with http.server.HTTPServer(("0.0.0.0", PORT), Handler) as httpd:
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nDetenido.")
