#!/usr/bin/env python3
"""Generate realistic product mockup images for Gumroad products."""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os

OUT = os.path.expanduser("~/gumroad-mockups")
os.makedirs(f"{OUT}/laptop", exist_ok=True)
os.makedirs(f"{OUT}/ipad", exist_ok=True)
os.makedirs(f"{OUT}/phone", exist_ok=True)
os.makedirs(f"{OUT}/stack", exist_ok=True)
os.makedirs(f"{OUT}/social", exist_ok=True)

try:
    f_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
    f_body = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
    f_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
    f_big = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
except:
    f_title = ImageFont.load_default()
    f_body = f_title
    f_small = f_title
    f_big = f_title

products = [
    ("safety", "SAFETY COMPLIANCE PACK", "SWMS Templates & Checklists", "#dc2626", "$37", [
        "SWMS - Concreting", "SWMS - Roofing", "SWMS - Electrical",
        "Daily Safety Checklist", "JSA Template"
    ]),
    ("quote", "QUOTE & INVOICE BUNDLE", "Professional Templates", "#2563eb", "$29", [
        "Quote Template", "Tax Invoice", "Client Contract",
        "Weekly Timesheet", "Change Order"
    ]),
    ("tax", "TAX & BAS PREP KIT", "EOFY Ready 2025-26", "#059669", "$22", [
        "Deduction Checklist", "BAS Tracker", "Vehicle Logbook",
        "Asset Calculator"
    ]),
    ("ai-guide", "AI TOOLS FOR TRADIES", "50+ Prompts & Guide", "#7c3aed", "$27", [
        "50+ AI Prompts", "15K Word Guide", "Quick Reference Cards",
        "Setup Guide"
    ]),
    ("ai-writer", "AI CONTENT WRITER", "Writing Tool in Browser", "#ea580c", "$14.99", [
        "Blog Posts", "Email Campaigns", "Social Media",
        "Tone Controls"
    ]),
    ("ai-image", "AI IMAGE PRO", "Image Editing in Browser", "#0891b2", "$12.99", [
        "AI Upscaling", "Remove Background", "Style Transfer",
        "AI Generation"
    ]),
    ("csv", "CSV CLEANER PRO", "Clean 10K+ Rows", "#4f46e5", "$9.99", [
        "Deduplicate", "Trim & Format", "Validate Columns",
        "Export to Excel"
    ]),
    ("reports", "PRO REPORTS BUNDLE", "PDFs & Templates", "#78716c", "$2.99", [
        "PDF Reports", "Quote Forms", "Invoice Templates",
        "Timesheets"
    ]),
]

def make_laptop_mockup(pid, name, tagline, color, price, items):
    """Laptop screen showing product template."""
    W, H = 1280, 720
    img = Image.new("RGB", (W, H), "#1a1a1a")
    draw = ImageDraw.Draw(img)
    
    # Laptop screen area
    screen_x, screen_y, screen_w, screen_h = 140, 40, 1000, 560
    draw.rounded_rectangle([(screen_x, screen_y), (screen_x+screen_w, screen_y+screen_h)], radius=12, fill="#0a0a0a")
    draw.rounded_rectangle([(screen_x+2, screen_y+2), (screen_x+screen_w-2, screen_y+screen_h-2)], radius=10, fill="#f8f8f8")
    
    # Browser bar
    draw.rectangle([(screen_x+2, screen_y+2), (screen_x+screen_w-2, screen_y+36)], fill="#e8e8e8")
    # Dots
    for dx in [12, 28, 44]:
        draw.ellipse([(screen_x+dx, screen_y+12), (screen_x+dx+8, screen_y+20)], fill="#ff5f56")
    # URL bar
    draw.rounded_rectangle([(screen_x+70, screen_y+10), (screen_x+screen_w-30, screen_y+28)], radius=4, fill="#fff")
    draw.text((screen_x+180, screen_y+13), f"gumroad.com/l/{pid}", fill="#999", font=f_small)
    
    # Product content inside screen
    content_y = screen_y + 50
    # Title
    draw.text((screen_x+30, content_y), name, fill="#111", font=f_big)
    # Tagline
    draw.text((screen_x+30, content_y+42), tagline, fill="#666", font=f_body)
    # Color bar
    draw.rectangle([(screen_x+30, content_y+75), (screen_x+400, content_y+80)], fill=color)
    
    # Features list
    y = content_y + 95
    for item in items[:4]:
        draw.text((screen_x+30, y), f"✓  {item}", fill="#333", font=f_body)
        y += 28
    
    # Price tag
    draw.rounded_rectangle([(screen_x+screen_w-160, content_y+90), (screen_x+screen_w-30, content_y+130)], radius=6, fill=color)
    draw.text((screen_x+screen_w-95, content_y+110), price, fill="#fff", font=f_title, anchor="mm")
    
    # Laptop base
    base_y = screen_y + screen_h
    draw.rounded_rectangle([(screen_x+80, base_y), (screen_x+screen_w-80, base_y+40)], radius=8, fill="#2a2a2a")
    draw.rounded_rectangle([(screen_x+120, base_y+40), (screen_x+screen_w-120, base_y+45)], radius=4, fill="#333")
    
    # Shadow
    draw.ellipse([(screen_x+60, base_y+50), (screen_x+screen_w-60, base_y+65)], fill="#111111")
    
    img.save(f"{OUT}/laptop/{pid}-laptop.png")
    print(f"✅ Laptop: {pid}")

def make_ipad_mockup(pid, name, tagline, color, price, items):
    """iPad showing the product."""
    W, H = 800, 800
    img = Image.new("RGB", (W, H), "#222222")
    draw = ImageDraw.Draw(img)
    
    # iPad body
    pad_x, pad_y, pad_w, pad_h = 100, 60, 600, 680
    draw.rounded_rectangle([(pad_x, pad_y), (pad_x+pad_w, pad_y+pad_h)], radius=40, fill="#333")
    draw.rounded_rectangle([(pad_x+10, pad_y+10), (pad_x+pad_w-10, pad_y+pad_h-10)], radius=35, fill="#f0f0f0")
    
    # Screen content
    cx, cy = pad_x + 50, pad_y + 60
    draw.text((cx, cy), name[:20], fill="#111", font=f_big)
    draw.text((cx, cy+42), tagline, fill="#666", font=f_body)
    draw.rectangle([(cx, cy+65), (cx+250, cy+68)], fill=color)
    
    y = cy + 85
    for item in items[:3]:
        draw.text((cx, y), f"✓ {item}", fill="#333", font=f_body)
        y += 32
    
    draw.rounded_rectangle([(cx+300, cy+40), (cx+450, cy+80)], radius=6, fill=color)
    draw.text((cx+375, cy+60), price, fill="#fff", font=f_title, anchor="mm")
    
    img.save(f"{OUT}/ipad/{pid}-ipad.png")
    print(f"✅ iPad: {pid}")

def make_phone_mockup(pid, name, color):
    """Phone showing mobile view."""
    W, H = 400, 600
    img = Image.new("RGB", (W, H), "#1a1a1a")
    draw = ImageDraw.Draw(img)
    
    # Phone body
    ph_x, ph_y, ph_w, ph_h = 40, 20, 320, 560
    draw.rounded_rectangle([(ph_x, ph_y), (ph_x+ph_w, ph_y+ph_h)], radius=30, fill="#222")
    draw.rounded_rectangle([(ph_x+6, ph_y+6), (ph_x+ph_w-6, ph_y+ph_h-6)], radius=25, fill="#f8f8f8")
    
    # Content
    cx, cy = ph_x + 30, ph_y + 60
    draw.text((cx, cy), name[:15], fill="#111", font=f_title)
    draw.rectangle([(cx, cy+35), (cx+150, cy+38)], fill=color)
    
    # Sample list items
    for i in range(5):
        y = cy + 55 + i * 45
        draw.rounded_rectangle([(cx, y), (cx+250, y+35)], radius=4, fill="#eee")
        draw.text((cx+12, y+9), f"Template {i+1}", fill="#555", font=f_small)
    
    img.save(f"{OUT}/phone/{pid}-phone.png")
    print(f"✅ Phone: {pid}")

def make_stack_mockup(pid, name, color, price):
    """Stack of printed documents."""
    W, H = 800, 800
    img = Image.new("RGB", (W, H), "#2a2a2a")
    draw = ImageDraw.Draw(img)
    
    # Paper stack with perspective (simplified as overlapping rectangles)
    offsets = [(0, 0), (8, -4), (16, -8), (24, -12)]
    for i, (dx, dy) in enumerate(offsets):
        sx, sy = 200 + dx, 280 + dy
        sw, sh = 400, 280
        paper_color = (250 - i*5, 250 - i*5, 250 - i*5)
        draw.rounded_rectangle([(sx, sy), (sx+sw, sy+sh)], radius=4, fill=paper_color)
        # Line effect
        for line in range(3):
            ly = sy + 50 + line * 40
            draw.rectangle([(sx+30, ly), (sx+sw-30, ly+2)], fill="#ddd")
    
    # Top document shows name
    tx, ty = 200 + offsets[-1][0], 280 + offsets[-1][1]
    draw.text((tx+30, ty+30), name, fill="#111", font=f_big)
    draw.rectangle([(tx+30, ty+80), (tx+200, ty+83)], fill=color)
    
    # Price label
    draw.rounded_rectangle([(tx+sw-120, ty+30), (tx+sw-30, ty+70)], radius=6, fill=color)
    draw.text((tx+sw-75, ty+50), price, fill="#fff", font=f_title, anchor="mm")
    
    img.save(f"{OUT}/stack/{pid}-stack.png")
    print(f"✅ Stack: {pid}")

def make_social_mockup(pid, name, color):
    """Instagram-style product showcase."""
    W, H = 1080, 1080
    img = Image.new("RGB", (W, H), "#111")
    draw = ImageDraw.Draw(img)
    
    # Product card
    draw.rounded_rectangle([(40, 200), (1040, 880)], radius=24, fill="#1a1a1a")
    draw.rectangle([(0, 0), (W, 4)], fill=color)
    
    # Product name
    draw.text((540, 400), name, fill="#fff", font=f_big, anchor="mm")
    
    # Price pill
    draw.rounded_rectangle([(390, 480), (690, 540)], radius=30, fill=color)
    draw.text((540, 510), "SHOP NOW →", fill="#fff", font=f_title, anchor="mm")
    
    # Bottom info
    draw.text((540, 700), "BUILT FOR AUSTRALIAN TRADIES", fill="#555", font=f_body, anchor="mm")
    draw.text((540, 725), "Instant Download • Editable Files", fill="#444", font=f_small, anchor="mm")
    
    draw.rectangle([(0, 1076), (W, 1080)], fill=color)
    
    img.save(f"{OUT}/social/{pid}-social.png")
    print(f"✅ Social: {pid}")

print("Generating product mockups...")
for pid, name, tagline, color, price, items in products:
    make_laptop_mockup(pid, name, tagline, color, price, items)
    make_ipad_mockup(pid, name, tagline, color, price, items)
    make_phone_mockup(pid, name, color)
    make_stack_mockup(pid, name, color, price)
    make_social_mockup(pid, name, color)

print(f"\nAll mockups saved to {OUT}/")
for root, dirs, files in os.walk(OUT):
    print(f"  {os.path.relpath(root, OUT)}/ → {len(files)} files")
