#!/usr/bin/env python3
"""Generate professional product cover images for Gumroad products."""
from PIL import Image, ImageDraw, ImageFont
import os, textwrap

OUT_DIR = os.path.expanduser("~/gumroad-covers")
os.makedirs(OUT_DIR, exist_ok=True)

products = [
    {
        "name": "Safety Compliance Pack",
        "tagline": "SWMS Templates & Checklists",
        "price": "$37",
        "bg": "#1a1a2e",
        "accent": "#e94560",
        "icon": "🛡️",
        "features": ["SWMS Templates", "Safety Checklists", "JSA Template", "State Regulations"]
    },
    {
        "name": "Quote & Invoice Bundle",
        "tagline": "Professional Templates for Tradies",
        "price": "$29",
        "bg": "#0f3460",
        "accent": "#16213e",
        "icon": "📄",
        "features": ["Quote Templates", "Tax Invoices", "Client Contracts", "Timesheets"]
    },
    {
        "name": "AI Tools for Tradies",
        "tagline": "Supercharge Your Trade Business",
        "price": "$27",
        "bg": "#2d1b69",
        "accent": "#7c3aed",
        "icon": "🧠",
        "features": ["50+ AI Prompts", "15K Word Guide", "Quick-Reference Cards", "Setup Guide"]
    },
    {
        "name": "Tax & BAS Prep Kit",
        "tagline": "EOFY Ready 2025-26",
        "price": "$22",
        "bg": "#064e3b",
        "accent": "#059669",
        "icon": "📊",
        "features": ["Deduction Checklist", "BAS Tracker", "Vehicle Logbook", "ATO Compliant"]
    },
    {
        "name": "AI Content Writer",
        "tagline": "Generate Content in Seconds",
        "price": "$14.99",
        "bg": "#1e1b4b",
        "accent": "#6366f1",
        "icon": "🤖",
        "features": ["Blog Posts", "Email Campaigns", "Social Media", "Browser-Based"]
    },
    {
        "name": "AI Image Pro",
        "tagline": "Edit Images in Your Browser",
        "price": "$12.99",
        "bg": "#1c1917",
        "accent": "#d97706",
        "icon": "🖼️",
        "features": ["Upscaling 2x-4x", "Remove Background", "AI Generation", "Batch Processing"]
    },
    {
        "name": "CSV Cleaner Pro",
        "tagline": "Clean 10,000+ Rows Instantly",
        "price": "$9.99",
        "bg": "#0c4a6e",
        "accent": "#0284c7",
        "icon": "📈",
        "features": ["Deduplicate", "Trim & Format", "Validate Columns", "Export to Excel"]
    },
    {
        "name": "Pro Reports Bundle",
        "tagline": "Printable PDF Reports & Templates",
        "price": "$2.99",
        "bg": "#27272a",
        "accent": "#71717a",
        "icon": "📋",
        "features": ["PDF Reports", "Quote Forms", "Invoice Designs", "Timesheets"]
    }
]

W, H = 1280, 720

try:
    font_big = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 56)
    font_mid = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 30)
    font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)
except:
    font_big = ImageFont.load_default()
    font_mid = font_big
    font_small = font_big

for p in products:
    img = Image.new("RGB", (W, H), p["bg"])
    draw = ImageDraw.Draw(img)
    
    # Accent bar at top
    draw.rectangle([(0, 0), (W, 8)], fill=p["accent"])
    
    # Bottom price bar
    draw.rectangle([(0, H-80), (W, H)], fill=(0, 0, 0, 80))
    
    # Icon
    draw.text((60, 50), p["icon"], font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 80) if font_big else font_big, fill="white")
    
    # Product name
    draw.text((60, 160), p["name"], font=font_big, fill="white")
    
    # Tagline
    draw.text((60, 230), p["tagline"], font=font_mid, fill=p["accent"])
    
    # Feature bullets
    y = 310
    for f in p["features"]:
        draw.text((60, y), f"✓  {f}", font=font_small, fill="#cccccc")
        y += 40
    
    # Price tag
    price_bg = "#ffffff" 
    draw.rounded_rectangle([(W-220, H-140), (W-40, H-100)], radius=8, fill=p["accent"])
    draw.text((W-130, H-130), p["price"], font=font_big, fill="white", anchor="mm")
    
    # "ONE-TIME" label
    draw.text((W-130, H-65), "ONE-TIME PAYMENT", font=font_small, fill="#999999", anchor="mm")
    
    # Footer line
    draw.text((60, H-50), "gumroad.com/edinsonmipc", font=font_small, fill="#666666")
    
    path = os.path.join(OUT_DIR, f"{p['name'].lower().replace(' ', '-').replace('&', 'and')}.png")
    img.save(path)
    print(f"✅ {p['name']:30s} → {path}")

print(f"\nAll covers saved to {OUT_DIR}/")
