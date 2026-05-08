#!/usr/bin/env python3
"""Generate FULL visual asset suite for all Gumroad products.
Creates: covers, social posts, ads, mockups, hero banners, Pinterest pins"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os, math

OUT = os.path.expanduser("~/gumroad-assets")
BLACK = "#0a0a0a"
DARK = "#111111"
SURFACE = "#1a1a1a"
YELLOW = "#f5a623"
WHITE = "#ffffff"
GRAY = "#666666"
GRAY_LIGHT = "#999999"

try:
    f_bold = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
    f_big = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 72)
    f_mid = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
    f_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
    f_tiny = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
    f_med_bold = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
    f_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 100)
except:
    f_bold = ImageFont.load_default()
    f_big = f_bold
    f_mid = f_bold
    f_small = f_bold
    f_tiny = f_bold
    f_med_bold = f_bold
    f_large = f_bold

products = [
    {"id": "safety", "name": "SAFETY COMPLIANCE\nPACK", "tagline": "SWMS Templates\n& Checklists", "price": "$37", "icon": "🛡️", "colors": ["#1a1a2e", "#e94560"]},
    {"id": "quote", "name": "QUOTE &\nINVOICE\nBUNDLE", "tagline": "Professional Templates\nfor Tradies", "price": "$29", "icon": "📄", "colors": ["#0f3460", "#16213e"]},
    {"id": "tax", "name": "TAX & BAS\nPREP KIT", "tagline": "EOFY Ready\n2025-26", "price": "$22", "icon": "📊", "colors": ["#064e3b", "#059669"]},
    {"id": "ai-guide", "name": "AI TOOLS\nFOR TRADIES", "tagline": "50+ Prompts\n& Guide", "price": "$27", "icon": "🧠", "colors": ["#2d1b69", "#7c3aed"]},
]

def draw_rounded_box(draw, xy, radius, fill):
    x0, y0, x1, y1 = xy
    r = min(radius, (x1-x0)//2, (y1-y0)//2)
    draw.rounded_rectangle(xy, radius=r, fill=fill)

def make_cover(p):
    img = Image.new("RGB", (1280, 720), BLACK)
    draw = ImageDraw.Draw(img)
    
    # Left accent bar
    draw.rectangle([(0, 0), (10, 720)], fill=YELLOW)
    
    # Top badge
    draw_rounded_box(draw, (1280-200, 30, 1280-30, 66), 6, YELLOW)
    draw.text((1280-115, 48), "PREMIUM TOOLKIT", fill=BLACK, font=f_tiny, anchor="mm")
    
    # Product name
    lines = p["name"].split("\n")
    y = 140
    for line in lines:
        draw.text((60, y), line, fill=WHITE, font=f_large)
        y += 110
    
    # Tagline
    t_lines = p["tagline"].split("\n")
    for line in t_lines:
        draw.text((60, y), line, fill=GRAY, font=f_mid)
        y += 32
    
    # Icon
    draw.text((60, 500), p["icon"], fill=WHITE, font=f_large)
    
    # Bottom bar
    draw.rectangle([(0, 620), (1280, 720)], fill=SURFACE)
    
    # Price
    draw.text((60, 665), p["price"], fill=YELLOW, font=f_big)
    
    # One time
    draw.text((200, 670), "ONE-TIME PAYMENT", fill=GRAY_LIGHT, font=f_small)
    
    # Brand
    draw.text((1280-60, 670), "BUILT FOR AUSTRALIAN TRADIES", fill=GRAY, font=f_tiny, anchor="rm")
    
    # Bottom accent line
    draw.rectangle([(0, 716), (1280, 720)], fill=YELLOW)
    
    os.makedirs(f"{OUT}/covers", exist_ok=True)
    path = f"{OUT}/covers/{p['id']}-cover.png"
    img.save(path)
    print(f"✅ Cover: {p['id']}")

def make_instagram(p):
    img = Image.new("RGB", (1080, 1080), BLACK)
    draw = ImageDraw.Draw(img)
    
    # Yellow accent top
    draw.rectangle([(0, 0), (1080, 8)], fill=YELLOW)
    
    # Icon large
    draw.text((540, 320), p["icon"], fill=WHITE, font=f_large, anchor="mm")
    
    # Name
    name = p["name"].replace("\n", " ")[:30]
    draw.text((540, 440), name, fill=WHITE, font=f_bold, anchor="mm")
    
    # Tagline
    draw.text((540, 490), p["tagline"].replace("\n", " "), fill=GRAY, font=f_small, anchor="mm")
    
    # Price pill
    draw_rounded_box(draw, (440, 550, 640, 600), 25, YELLOW)
    draw.text((540, 575), f"${p['price'].replace('$','')}", fill=BLACK, font=f_bold, anchor="mm")
    
    # Bottom text
    draw.text((540, 700), "BUILT FOR AUSTRALIAN TRADIES", fill=GRAY, font=f_tiny, anchor="mm")
    draw.text((540, 720), "Instant Download • Editable Files", fill=GRAY, font=f_tiny, anchor="mm")
    
    # Bottom accent
    draw.rectangle([(0, 1072), (1080, 1080)], fill=YELLOW)
    
    os.makedirs(f"{OUT}/instagram", exist_ok=True)
    path = f"{OUT}/instagram/{p['id']}-ig.png"
    img.save(path)
    print(f"✅ Instagram: {p['id']}")

def make_facebook_ad(p):
    img = Image.new("RGB", (1200, 628), BLACK)
    draw = ImageDraw.Draw(img)
    
    # Split layout
    draw.rectangle([(0, 0), (600, 628)], fill=DARK)
    draw.rectangle([(600, 0), (1200, 628)], fill=BLACK)
    
    # Left: Product
    draw.text((300, 200), p["icon"], fill=WHITE, font=f_big, anchor="mm")
    name = p["name"].replace("\n", " ")[:30]
    draw.text((300, 280), name, fill=WHITE, font=f_bold, anchor="mm")
    draw.text((300, 330), p["tagline"].replace("\n", " "), fill=GRAY, font=f_small, anchor="mm")
    
    # Right: CTA
    draw.text((900, 200), "STOP LOSING", fill=WHITE, font=f_bold, anchor="mm")
    draw.text((900, 240), "MONEY ON BAD", fill=WHITE, font=f_bold, anchor="mm")
    draw.text((900, 280), "PAPERWORK", fill=YELLOW, font=f_bold, anchor="mm")
    
    draw_rounded_box(draw, (780, 340, 1020, 390), 25, YELLOW)
    draw.text((900, 365), f"Shop {p['price']} →", fill=BLACK, font=f_bold, anchor="mm")
    
    # Yellow accent bottom
    draw.rectangle([(0, 624), (1200, 628)], fill=YELLOW)
    
    os.makedirs(f"{OUT}/facebook", exist_ok=True)
    path = f"{OUT}/facebook/{p['id']}-fb.png"
    img.save(path)
    print(f"✅ Facebook: {p['id']}")

def make_pinterest(p):
    img = Image.new("RGB", (1000, 1500), BLACK)
    draw = ImageDraw.Draw(img)
    
    draw.rectangle([(0, 0), (1000, 8)], fill=YELLOW)
    
    draw.text((500, 500), p["icon"], fill=WHITE, font=f_large, anchor="mm")
    name = p["name"].replace("\n", " ")[:35]
    draw.text((500, 600), name, fill=WHITE, font=f_bold, anchor="mm")
    draw.text((500, 650), p["tagline"].replace("\n", " "), fill=GRAY, font=f_mid, anchor="mm")
    
    # CTA pill
    draw_rounded_box(draw, (350, 720, 650, 780), 30, YELLOW)
    draw.text((500, 750), f"${p['price'].replace('$','')}", fill=BLACK, font=f_bold, anchor="mm")
    
    draw.text((500, 850), "🔽 INSTANT DOWNLOAD", fill=GRAY, font=f_small, anchor="mm")
    draw.text((500, 880), "BUILT FOR AUSTRALIAN TRADIES", fill=GRAY, font=f_tiny, anchor="mm")
    
    draw.rectangle([(0, 1496), (1000, 1500)], fill=YELLOW)
    
    os.makedirs(f"{OUT}/pinterest", exist_ok=True)
    path = f"{OUT}/pinterest/{p['id']}-pin.png"
    img.save(path)
    print(f"✅ Pinterest: {p['id']}")

def make_hero(p):
    img = Image.new("RGB", (1920, 800), BLACK)
    draw = ImageDraw.Draw(img)
    
    # Radial gradient effect (simplified)
    for i in range(800):
        alpha = int(30 * (1 - i/800))
        draw.rectangle([(800, i), (1920, i+1)], fill=(245, 166, 35, 0))
    
    # Left side: text
    draw.text((100, 200), p["icon"], fill=WHITE, font=f_large)
    
    y = 320
    for line in p["name"].split("\n"):
        draw.text((100, y), line, fill=WHITE, font=f_big)
        y += 80
    
    draw.text((100, y+20), p["tagline"].replace("\n", " "), fill=GRAY, font=f_mid)
    
    draw_rounded_box(draw, (100, y+80, 300, y+130), 25, YELLOW)
    draw.text((200, y+105), f"${p['price'].replace('$','')}", fill=BLACK, font=f_bold, anchor="mm")
    
    # Right side: visual area
    draw.rectangle([(1200, 0), (1920, 800)], fill=DARK)
    draw.text((1560, 400), p["icon"], fill=WHITE, font=f_large, anchor="mm")
    
    # Bottom bar
    draw.rectangle([(0, 796), (1920, 800)], fill=YELLOW)
    
    os.makedirs(f"{OUT}/hero", exist_ok=True)
    path = f"{OUT}/hero/{p['id']}-hero.png"
    img.save(path)
    print(f"✅ Hero: {p['id']}")

def make_tiktok(p):
    img = Image.new("RGB", (1080, 1920), BLACK)
    draw = ImageDraw.Draw(img)
    
    draw.rectangle([(0, 0), (1080, 8)], fill=YELLOW)
    
    draw.text((540, 700), p["icon"], fill=WHITE, font=f_large, anchor="mm")
    name = p["name"].replace("\n", " ")[:25]
    draw.text((540, 800), name, fill=WHITE, font=f_bold, anchor="mm")
    
    draw_rounded_box(draw, (390, 880, 690, 940), 30, YELLOW)
    draw.text((540, 910), p["price"], fill=BLACK, font=f_bold, anchor="mm")
    
    draw.text((540, 1000), "⬇️ LINK IN BIO", fill=GRAY, font=f_mid, anchor="mm")
    
    draw.rectangle([(0, 1916), (1080, 1920)], fill=YELLOW)
    
    os.makedirs(f"{OUT}/tiktok", exist_ok=True)
    path = f"{OUT}/tiktok/{p['id']}-tt.png"
    img.save(path)
    print(f"✅ TikTok: {p['id']}")

for p in products:
    make_cover(p)
    make_instagram(p)
    make_facebook_ad(p)
    make_pinterest(p)
    make_hero(p)
    make_tiktok(p)

print(f"\nAll assets generated in {OUT}/")
print(f"Total: {len(products)} products × 6 assets = {len(products)*6} files")

# List all files
for root, dirs, files in os.walk(OUT):
    for f in sorted(files):
        path = os.path.join(root, f)
        size = os.path.getsize(path)
        print(f"  {os.path.relpath(path, OUT):50s} {size//1024:4d}KB")
