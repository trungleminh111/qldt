import os
import sys
import socket
import threading
import time
import urllib.request
import webbrowser

from app import tao_ung_dung
import config

_single_instance_socket = None

def kiem_tra_va_khoa_don_tien_trinh(lock_port=52938):
    global _single_instance_socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind(("127.0.0.1", lock_port))
        s.listen(1)
        _single_instance_socket = s
        return True
    except OSError:
        return False

def tim_cong_app_dang_chay(cong_khoi_dau=5000):
    for c in range(cong_khoi_dau, cong_khoi_dau + 5):
        try:
            req = urllib.request.Request(f"http://127.0.0.1:{c}/dang-nhap", headers={"User-Agent": "QLDT-Detector"})
            with urllib.request.urlopen(req, timeout=0.6) as resp:
                if resp.status in (200, 302):
                    return c
        except Exception:
            pass
    return None

def tim_cong_trong(cong_khoi_dau=5000):
    for c in range(cong_khoi_dau, cong_khoi_dau + 50):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.bind(("127.0.0.1", c))
            s.close()
            return c
        except OSError:
            continue
    return cong_khoi_dau

def mo_cua_so_ung_dung(url):
    time.sleep(1.0)
    edge_path_64 = r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
    edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    chrome_path_x86 = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"

    trinh_duyet = None
    if os.path.exists(edge_path_64):
        trinh_duyet = edge_path_64
    elif os.path.exists(edge_path):
        trinh_duyet = edge_path
    elif os.path.exists(chrome_path):
        trinh_duyet = chrome_path
    elif os.path.exists(chrome_path_x86):
        trinh_duyet = chrome_path_x86

    if trinh_duyet:
        os.system(f'start "" "{trinh_duyet}" --app={url}')
    else:
        webbrowser.open(url)

if __name__ == "__main__":
    if not kiem_tra_va_khoa_don_tien_trinh(52938):
        for _ in range(10):
            cong = tim_cong_app_dang_chay(5000)
            if cong is not None:
                mo_cua_so_ung_dung(f"http://127.0.0.1:{cong}/")
                sys.exit(0)
            time.sleep(0.5)
        sys.exit(0)

    ung_dung = tao_ung_dung()
    cong = tim_cong_trong(5000)
    dia_chi = f"http://127.0.0.1:{cong}/"

    luong_mo_app = threading.Thread(target=mo_cua_so_ung_dung, args=(dia_chi,))
    luong_mo_app.daemon = True
    luong_mo_app.start()

    ung_dung.run(host="127.0.0.1", port=cong, debug=False, threaded=True)
