import os
import sys
import socket
import threading
import time
import webbrowser

os.environ["DB_BACKEND"] = os.environ.get("DB_BACKEND", "sqlite")

from app import tao_ung_dung
import config

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
    ung_dung = tao_ung_dung()
    cong = tim_cong_trong(5000)
    dia_chi = f"http://127.0.0.1:{cong}/"

    luong_mo_app = threading.Thread(target=mo_cua_so_ung_dung, args=(dia_chi,))
    luong_mo_app.daemon = True
    luong_mo_app.start()

    ung_dung.run(host="127.0.0.1", port=cong, debug=False, threaded=True)
