import os
import sys
import threading
import time
import webbrowser
from app import tao_ung_dung
import config

def mo_cua_so_ung_dung(url):
    time.sleep(1.2)
    edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    edge_path_64 = r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"

    if os.path.exists(edge_path):
        os.system(f'start "" "{edge_path}" --app={url}')
    elif os.path.exists(edge_path_64):
        os.system(f'start "" "{edge_path_64}" --app={url}')
    else:
        webbrowser.open(url)

if __name__ == "__main__":
    ung_dung = tao_ung_dung()
    cong = 5000
    dia_chi = f"http://127.0.0.1:{cong}"

    luong_mo_app = threading.Thread(target=mo_cua_so_ung_dung, args=(dia_chi,))
    luong_mo_app.daemon = True
    luong_mo_app.start()

    ung_dung.run(host="127.0.0.1", port=cong, debug=False)
