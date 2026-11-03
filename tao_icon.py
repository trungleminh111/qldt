import os
import shutil
from PIL import Image, ImageDraw

def tao_icon():
    src_path = "static/img/logo_goc.jpg"
    if not os.path.exists(src_path):
        return

    os.makedirs("static/img", exist_ok=True)
    os.makedirs("static/icons", exist_ok=True)

    src = Image.open(src_path).convert("RGBA")
    w, h = src.size

    mask = Image.new("L", (w, h), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse([512 - 501, 503 - 501, 512 + 501, 503 + 501], fill=255)

    logo = src.copy()
    for y in range(h):
        for x in range(w):
            r, g, b, a = logo.getpixel((x, y))
            m = mask.getpixel((x, y))
            if m == 0 or (r < 15 and g < 15 and b < 15 and ((x - 512) ** 2 + (y - 503) ** 2 > 470 ** 2)):
                logo.putpixel((x, y), (0, 0, 0, 0))

    logo.save("static/img/logo.png", "PNG")

    logo512 = logo.resize((512, 512), Image.Resampling.LANCZOS)
    logo512.save("static/icons/icon-512x512.png", "PNG")

    logo192 = logo.resize((192, 192), Image.Resampling.LANCZOS)
    logo192.save("static/icons/icon-192x192.png", "PNG")

    logo48 = logo.resize((48, 48), Image.Resampling.LANCZOS)
    logo48.save("static/icons/icon-48x48.png", "PNG")

    logo32 = logo.resize((32, 32), Image.Resampling.LANCZOS)
    logo32.save("static/icons/icon-32x32.png", "PNG")

    logo16 = logo.resize((16, 16), Image.Resampling.LANCZOS)
    logo16.save("static/icons/icon-16x16.png", "PNG")

    ico_sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    logo.save("static/favicon.ico", format="ICO", sizes=ico_sizes)
    logo.save("app_icon.ico", format="ICO", sizes=ico_sizes)

if __name__ == "__main__":
    tao_icon()
