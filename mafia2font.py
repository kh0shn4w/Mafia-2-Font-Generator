import os
import xml.etree.ElementTree as ET
from xml.dom import minidom
from PIL import Image, ImageDraw, ImageFont
import arabic_reshaper

INPUT_CHARS = (
    " !\"#$%&'()*+,-./0123456789:;<=>?@"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`"
    "abcdefghijklmnopqrstuvwxyz{|}~"
    "ئتجچحخدرزسشعغیە"
    "٠١٢٣٤٥٦٧٨٩"
    "،؛؟ـ"
    "©®™€£$¢¥•"
)

TEXTURE_SIZE = (1024, 1024)
DRAW_FONT_SIZE = 42 

SIDE_MARGIN = 6      
TOP_BOTTOM_MARGIN = 6
TEXTURE_PADDING = 2  

COLOR_TEXT = (0, 255, 0, 255)  
COLOR_BG   = (0, 0, 0, 0)      # Alpha 0 = Transparent

FONT_PATH = "font.ttf"
FILE_BASE_NAME = "fonttexture"

# Mafia 2 Engine
REQUIRED_SIZES = [10, 12, 14, 15, 16, 17, 18, 19, 20, 21, 22, 24, 26, 27, 29, 32, 36, 40]
REQUIRED_KEYS  = ["16777216", "33554432"]

def get_glyph_map(text, font):
    reshaper = arabic_reshaper.ArabicReshaper(configuration={'delete_harakat': True})
    mapping = {}
    
    chars = sorted(list(set(text)))
    
    print("Mapping Glyphs...")
    
    for char in chars:
        code = ord(char)
        
        if (0x0600 <= code <= 0x06FF) or (0x0750 <= code <= 0x077F) or (0xFB50 <= code <= 0xFEFF):
            try:
                iso = reshaper.reshape(char)
                if font.getlength(iso) > 0:
                    mapping[code] = iso

                forms = []

                ini = reshaper.reshape(char + "ـ")
                if ini: forms.append(ini[0])

                med = reshaper.reshape("ـ" + char + "ـ")
                if med: forms.append(med.replace("ـ", ""))

                fin = reshaper.reshape("ـ" + char)
                if fin: forms.append(fin.replace("ـ", ""))
                
                for form in forms:
                    if not form: continue
                    if font.getlength(form) > 0:
                        mapping[ord(form)] = form
                    else:
                        mapping[ord(form)] = char
                        
            except Exception as e:
                mapping[code] = char
        else:
            mapping[code] = char
            
    return mapping

def create_xml_node(root, keycode, x, y, width, height, advance, font_size):
    scale = float(font_size)
    norm_w = width / scale
    norm_h = height / scale
    
    norm_adv = (advance * 1.15) / scale 
    
    ascender = 0.875
    descender = -0.60625
    
    bearing_x_val = -1.0 * (SIDE_MARGIN / scale)
    bearing_y = 1.25

    for key in REQUIRED_KEYS:
        for size in REQUIRED_SIZES:
            ET.SubElement(root, "CharDescription", {
                "FontKey": key,
                "FontSize": str(size),
                "FontStyle": "0",
                "KeyCode": str(keycode),
                "XLeftTopPixel": str(int(x)),
                "YLeftTopPixel": str(int(y)),
                "XYSize": str(int(height)),
                "CharAdvanceX": f"{norm_adv:.6f}",
                "CharBearingX": f"{bearing_x_val:.6f}",
                "CharBearingY": f"{bearing_y}",
                "CharWidth": f"{norm_w:.6f}",
                "CharHeight": f"{norm_h:.6f}",
                "FontAscender": str(ascender),
                "FontDescender": str(descender)
            })

def main():
    if not os.path.exists(FONT_PATH):
        print(f"ERROR: '{FONT_PATH}' not found.")
        return

    try:
        font = ImageFont.truetype(FONT_PATH, DRAW_FONT_SIZE)
    except:
        print("Error loading font file.")
        return

    ascent, descent = font.getmetrics()
    box_height = ascent + descent + (TOP_BOTTOM_MARGIN * 2)
    

    img = Image.new("RGBA", TEXTURE_SIZE, COLOR_BG)
    draw = ImageDraw.Draw(img)
    root = ET.Element("FontTextureDescription")

    glyph_map = get_glyph_map(INPUT_CHARS, font)
    

    sorted_items = sorted(glyph_map.items(), key=lambda x: x[0])

    cur_x = TEXTURE_PADDING
    cur_y = TEXTURE_PADDING

    rendered_rects = {}

    for unicode_id, char_str in sorted_items:

        if char_str in rendered_rects:
            (rx, ry, rw, rh, radv) = rendered_rects[char_str]
            create_xml_node(root, unicode_id, rx, ry, rw, rh, radv, DRAW_FONT_SIZE)
            continue

        adv = font.getlength(char_str)
        bbox = font.getbbox(char_str)
        
        if bbox:
            ink_w = (bbox[2] - bbox[0]) + 2
            left_ink_offset = bbox[0]
        else:
            ink_w = max(adv, 10)
            left_ink_offset = 0
            
        box_width = int(ink_w + (SIDE_MARGIN * 2))

        if cur_x + box_width + TEXTURE_PADDING > TEXTURE_SIZE[0]:
            cur_x = TEXTURE_PADDING
            cur_y += box_height + TEXTURE_PADDING
            
        if cur_y + box_height > TEXTURE_SIZE[1]:
            print("Texture Full!")
            break

        draw_x = cur_x + SIDE_MARGIN - left_ink_offset
        draw.text((draw_x, cur_y + TOP_BOTTOM_MARGIN), char_str, font=font, fill=COLOR_TEXT)

        create_xml_node(root, unicode_id, cur_x, cur_y, box_width, box_height, adv, DRAW_FONT_SIZE)

        rendered_rects[char_str] = (cur_x, cur_y, box_width, box_height, adv)

        cur_x += box_width + TEXTURE_PADDING

    img.save(f"{FILE_BASE_NAME}.png")
    
    cap = ET.SubElement(root, "CapitalTable")
    for i in range(97, 123):
        ET.SubElement(cap, "code", {"lo": str(i), "up": str(i-32)})

    xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")
    with open(f"{FILE_BASE_NAME}.xml", "w", encoding="utf-8") as f:
        f.write(xml_str)
        
    print("DONE.")
    print("1. Open fonttexture.png in Paint.NET")
    print("2. Save as .DDS (DXT5, Interpolated Alpha)")
    print("   Make sure the background is checkered (Transparent) in Paint.NET before saving!")

if __name__ == "__main__":
    main()