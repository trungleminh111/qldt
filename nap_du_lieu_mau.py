import sys
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from models.co_so_du_lieu import khoi_tao_co_so_du_lieu, kiem_tra_da_co_du_lieu
from models.du_lieu_mau import nap_du_lieu_mau

def thuc_thi_nap_du_lieu(ep_buoc=False):
    khoi_tao_co_so_du_lieu()
    if not ep_buoc and kiem_tra_da_co_du_lieu():
        print("Cơ sở dữ liệu đã có dữ liệu. Bỏ qua, không nạp lại dữ liệu mẫu.")
        return False
    da_nap = nap_du_lieu_mau(ep_buoc=ep_buoc)
    if da_nap:
        print("Đã khởi tạo và nạp dữ liệu mẫu ban đầu thành công.")
    else:
        print("Cơ sở dữ liệu đã có dữ liệu. Bỏ qua, không nạp lại dữ liệu mẫu.")
    return da_nap

if __name__ == "__main__":
    ep_buoc = ("--force" in sys.argv) or ("--khoi-tao-lai" in sys.argv)
    thuc_thi_nap_du_lieu(ep_buoc=ep_buoc)
