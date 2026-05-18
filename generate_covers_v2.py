#!/usr/bin/env python3
"""Generate premium Gumroad covers - Black/Yellow/White tradie branding."""
from PIL import Image, ImageDraw, ImageFont
import os

OUT_DIR = os.path.expanduser("~/gumroad-covers/v2")
os.makedirs(OUT_DIR, exist_ok=True)

# Design System
BLACK = "#0f0f0f"
DARK = "#1a1a1a"
YELLOW = "#f5a623"
WHITE = "#ffffff"
GRAY = "#888888"
LIGHT_GRAY = "#e0e0e0"

products = [
    {
        "name": "SAFETY\nCOMPLIANCE\nPACK",
        "subtitle": "SWMS Templates & Checklists",
        "price": "$37",
        "tag": "BEST SELLER",
        "accent": YELLOW,
    },
    {
        "name": "QUOTE &\nINVOICE\nBUNDLE",
        "subtitle": "Professional Templates for Tradies",
        "price": "$29",
        "tag": "ATO COMPLIANT",
        "accent": YELLOW,
    },
    {
        "name": "TAX &\nBAS\nPREP KIT",
        "subtitle": "EOFY Ready 2025-26",
        "price": "$22",
        "tag": "ATO RATES",
        "accent": YELLOW,
    },
    {
        "name": "AI TOOLS\nFOR\nTRADIES",
        "subtitle": "50+ Prompts & 15K Word Guide",
        "price": "$27",
        "tag": "GUIDE",
        "accent": YELLOW,
    },
    {
        "name": "AI\nCONTENT\nWRITER",
        "subtitle": "Writing Tool in Your Browser",
        "price": "$14.99",
        "tag": "TOOL",
        "accent": YELLOW,
    },
    {
        "name": "AI\nIMAGE\nPRO",
        "subtitle": "Image Editing in Your Browser",
        "price": "$12.99",
        "tag": "TOOL",
        "accent": YELLOW,
    },
    {
        "name": "CSV\nCLEANER\nPRO",
        "subtitle": "Clean 10,000+ Rows Instantly",
        "price": "$9.99",
        "tag": "TOOL",
        "accent": YELLOW,
    },
    {
        "name": "PRO\nREPORTS\nBUNDLE",
        "subtitle": "Printable PDFs & Templates",
        "price": "$2.99",
        "tag": "BUNDLE",
        "accent": YELLOW,
    },
]

W, H = 1280, 720

try:
    font_big = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 72)
    font_mid = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 30)
    font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)
    font_tag = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
except:
    font_big = ImageFont.load_default()
    font_mid = font_big
    font_small = font_big
    font_tag = font_big

for p in products:
    img = Image.new("RGB", (W, H), BLACK)
    draw = ImageDraw.Draw(img)
    
    # Darker top band
    draw.rectangle([(0, 0), (W, H)], fill=BLACK)
    
    # Yellow accent bar on left
    draw.rectangle([(0, 0), (12, H)], fill=p["accent"])
    
    # Diagonal yellow stripe accent (subtle)
    # Not doing complex geometry - keep it clean
    
    # Tag badge top right
    if p["tag"]:
        tag_w = 180
        tag_h = 36
        draw.rounded_rectangle([(W - tag_w - 30, 30), (W - 30, 30 + tag_h)], radius=4, fill=p["accent"])
        draw.text((W - 30 - tag_w//2, 30 + tag_h//2), p["tag"], font=font_tag, fill=BLACK, anchor="mm")
    
    # Product name (large, bold, left-aligned)
    lines = p["name"].split("\n")
    y = 140
    for line in lines:
        draw.text((60, y), line, font=font_big, fill=WHITE)
        y += 76
    
    # Subtitle
    draw.text((60, y + 20), p["subtitle"], font=font_small, fill=GRAY)
    
    # Bottom bar with price
    draw.rectangle([(0, H - 100), (W, H)], fill=DARK)
    
    # Price on left
    draw.text((60, H - 55), p["price"], font=font_mid, fill=YELLOW)
    
    # "ONE-TIME" label
    draw.text((170, H - 48), "ONE-TIME PAYMENT", font=font_small, fill=GRAY)
    
    # "BUILT FOR AUSTRALIAN TRADIES" on right
    draw.text((W - 60, H - 48), "BUILT FOR AUSTRALIAN TRADIES", font=font_small, fill=GRAY, anchor="rm")
    
    # Bottom yellow line
    draw.rectangle([(0, H - 4), (W, H)], fill=p["accent"])
    
    path = os.path.join(OUT_DIR, p["name"].replace("\n", "-").lower() + ".png")
    img.save(path)
    print(f"✅ Saved: {path}")

print(f"\nAll covers saved to {OUT_DIR}/")
