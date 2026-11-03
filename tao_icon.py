import math
import os
from PIL import Image, ImageDraw

def ve_ngoi_sao(draw, tam_x, tam_y, ban_kinh_ngoai, ban_kinh_trong, mau_dien, mau_vien=None, do_day_vien=1):
    diem = []
    goc_khoi_dau = -math.pi / 2
    for i in range(10):
        r = ban_kinh_ngoai if i % 2 == 0 else ban_kinh_trong
        goc = goc_khoi_dau + i * math.pi / 5
        x = tam_x + r * math.cos(goc)
        y = tam_y + r * math.sin(goc)
        diem.append((x, y))
    draw.polygon(diem, fill=mau_dien, outline=mau_vien, width=do_day_vien)

def tao_icon_512():
    size = 512
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    draw.rounded_rectangle([16, 16, 496, 496], radius=110, fill=(15, 23, 42, 255), outline=(217, 119, 6, 255), width=10)
    draw.rounded_rectangle([32, 32, 480, 480], radius=96, fill=(30, 41, 59, 255), outline=(245, 158, 11, 200), width=4)

    dt_left = 146
    dt_top = 80
    dt_right = 366
    dt_bottom = 432
    draw.rounded_rectangle([dt_left, dt_top, dt_right, dt_bottom], radius=38, fill=(10, 15, 29, 255), outline=(148, 163, 184, 255), width=6)

    man_left = dt_left + 16
    man_top = dt_top + 40
    man_right = dt_right - 16
    man_bottom = dt_bottom - 44
    draw.rounded_rectangle([man_left, man_top, man_right, man_bottom], radius=22, fill=(14, 116, 144, 255))
    draw.rounded_rectangle([man_left + 4, man_top + 4, man_right - 4, man_bottom - 4], radius=18, fill=(3, 105, 161, 255))

    ve_ngoi_sao(draw, tam_x=256, tam_y=246, ban_kinh_ngoai=62, ban_kinh_trong=26, mau_dien=(251, 191, 36, 255), mau_vien=(217, 119, 6, 255), do_day_vien=3)

    loa_w = 48
    loa_left = (size - loa_w) // 2
    draw.rounded_rectangle([loa_left, dt_top + 16, loa_left + loa_w, dt_top + 22], radius=3, fill=(148, 163, 184, 255))
    draw.ellipse([dt_right - 40, dt_top + 15, dt_right - 32, dt_top + 23], fill=(56, 189, 248, 255))

    thanh_w = 64
    thanh_left = (size - thanh_w) // 2
    draw.rounded_rectangle([thanh_left, dt_bottom - 24, thanh_left + thanh_w, dt_bottom - 18], radius=3, fill=(148, 163, 184, 255))

    return img

def main():
    os.makedirs("static/icons", exist_ok=True)
    img512 = tao_icon_512()
    img512.save("static/icons/icon-512x512.png", "PNG")

    img192 = img512.resize((192, 192), Image.Resampling.LANCZOS)
    img192.save("static/icons/icon-192x192.png", "PNG")

    img48 = img512.resize((48, 48), Image.Resampling.LANCZOS)
    img48.save("static/icons/icon-48x48.png", "PNG")

    img32 = img512.resize((32, 32), Image.Resampling.LANCZOS)
    img32.save("static/icons/icon-32x32.png", "PNG")

    img16 = img512.resize((16, 16), Image.Resampling.LANCZOS)
    img16.save("static/icons/icon-16x16.png", "PNG")

    kich_thuoc_ico = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    img512.save("static/favicon.ico", format="ICO", sizes=kich_thuoc_ico)
    img512.save("app_icon.ico", format="ICO", sizes=kich_thuoc_ico)

if __name__ == "__main__":
    main()
