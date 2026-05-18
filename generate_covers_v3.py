#!/usr/bin/env python3
from PIL import Image, ImageDraw, ImageFont
import os

OUT = "/home/edinsonmipc/gumroad-covers/v3"
os.makedirs(OUT, exist_ok=True)

BLACK = "#0a0a0a"
SURFACE = "#1a1a1a"
YELLOW = "#f5a623"
WHITE = "#ffffff"
GRAY = "#666666"

try:
    f_big = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 72)
    f_mid = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28)
    f_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
    f_tiny = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
    f_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 100)
except:
    f_big = ImageFont.load_default()
    f_mid = f_big; f_small = f_big; f_tiny = f_big; f_large = f_big

products = [
    ("ai-content-writer", "AI CONTENT\nWRITER", "Writing Tool\nin Your Browser", "$14.99", "🤖"),
    ("ai-image-pro", "AI IMAGE\nPRO", "Image Editing\nin Your Browser", "$12.99", "🖼️"),
    ("csv-cleaner-pro", "CSV CLEANER\nPRO", "Clean 10,000+ Rows\nin Seconds", "$9.99", "📈"),
    ("pro-reports-bundle", "PRO REPORTS\nBUNDLE", "Printable PDFs\n& Templates", "$2.99", "📋"),
]

for pid, name, tagline, price, icon in products:
    img = Image.new("RGB", (1280, 720), BLACK)
    draw = ImageDraw.Draw(img)
    
    draw.rectangle((0, 0, 10, 720), fill=YELLOW)
    draw.rounded_rectangle(((1280-200, 30), (1280-30, 66)), radius=6, fill=YELLOW)
    draw.text((1280-115, 48), "PREMIUM TOOLKIT", fill=BLACK, font=f_tiny, anchor="mm")
    
    y = 140
    for line in name.split("\n"):
        draw.text((60, y), line, fill=WHITE, font=f_large)
        y += 110
    
    for line in tagline.split("\n"):
        draw.text((60, y), line, fill=GRAY, font=f_mid)
        y += 34
    
    draw.text((60, 500), icon, fill=WHITE, font=f_large)
    
    draw.rectangle((0, 620, 1280, 720), fill=SURFACE)
    draw.text((60, 665), price, fill=YELLOW, font=f_big)
    draw.text((220, 670), "ONE-TIME PAYMENT", fill="#999999", font=f_small)
    draw.text((1260, 670), "BUILT FOR AUSTRALIAN TRADIES", fill=GRAY, font=f_tiny, anchor="rm")
    draw.rectangle((0, 716, 1280, 720), fill=YELLOW)
    
    path = f"{OUT}/{pid}.png"
    img.save(path)
    print(f"✅ {pid}.png")

print(f"\nAll saved to {OUT}/")
