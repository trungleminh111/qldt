function capNhatDongHo() {
  const el = document.getElementById("liveTime");
  if (!el) return;
  const now = new Date();
  const gio = String(now.getHours()).padStart(2, "0");
  const phut = String(now.getMinutes()).padStart(2, "0");
  const giay = String(now.getSeconds()).padStart(2, "0");
  const ngay = String(now.getDate()).padStart(2, "0");
  const thang = String(now.getMonth() + 1).padStart(2, "0");
  const nam = now.getFullYear();
  el.textContent = `${gio}:${phut}:${giay} · ${ngay}/${thang}/${nam}`;
}

setInterval(capNhatDongHo, 1000);
document.addEventListener("DOMContentLoaded", capNhatDongHo);

function moModal(id) {
  const modal = document.getElementById(id);
  if (modal) {
    modal.style.display = "flex";
    document.body.style.overflow = "hidden";
  }
}

function dongModal(id) {
  const modal = document.getElementById(id);
  if (modal) {
    modal.style.display = "none";
    const remainingOpen = document.querySelectorAll(".modal-backdrop[style*='display: flex'], .modal-backdrop[style*='display: block']");
    if (remainingOpen.length === 0) {
      document.body.style.overflow = "";
    }
  }
}

window.addEventListener("click", function(event) {
  if (event.target.classList.contains("modal-backdrop")) {
    event.target.style.display = "none";
    const remainingOpen = document.querySelectorAll(".modal-backdrop[style*='display: flex'], .modal-backdrop[style*='display: block']");
    if (remainingOpen.length === 0) {
      document.body.style.overflow = "";
    }
  }
  const goiY = document.getElementById("danhSachGoiYNhanh");
  const inputTimKiem = document.getElementById("oTimKiemNhanh");
  if (goiY && goiY.style.display !== "none") {
    if (event.target !== inputTimKiem && !goiY.contains(event.target)) {
      goiY.style.display = "none";
    }
  }
});

window.addEventListener("keydown", function(event) {
  if (event.key === "Escape") {
    const openModals = document.querySelectorAll(".modal-backdrop");
    let closedAny = false;
    openModals.forEach(m => {
      if (m.style.display === "flex" || m.style.display === "block") {
        m.style.display = "none";
        closedAny = true;
      }
    });
    if (closedAny) {
      document.body.style.overflow = "";
    }
    const goiY = document.getElementById("danhSachGoiYNhanh");
    if (goiY) {
      goiY.style.display = "none";
    }
  }
});

let cheDoRealTimeGiaoNhan = true;

function layChuoiThoiGianHienTai() {
  const now = new Date();
  const nam = now.getFullYear();
  const thang = String(now.getMonth() + 1).padStart(2, "0");
  const ngay = String(now.getDate()).padStart(2, "0");
  const gio = String(now.getHours()).padStart(2, "0");
  const phut = String(now.getMinutes()).padStart(2, "0");
  return {
    ngay: `${nam}-${thang}-${ngay}`,
    gio: `${gio}:${phut}`
  };
}

function dongBoGiaTriThoiGian(ngay, gio) {
  const ngayGiaoInput = document.getElementById("ngayGiaoInput");
  const gioGiaoInput = document.getElementById("gioGiaoInput");
  const ngayNgoaiLe = document.getElementById("ngayGiaoNgoaiLeInput");
  const gioNgoaiLe = document.getElementById("gioGiaoNgoaiLeInput");
  const ngayNopInput = document.getElementById("ngayNopInput");
  const gioNopInput = document.getElementById("gioNopInput");

  if (ngayGiaoInput) ngayGiaoInput.value = ngay;
  if (gioGiaoInput) gioGiaoInput.value = gio;
  if (ngayNgoaiLe) ngayNgoaiLe.value = ngay;
  if (gioNgoaiLe) gioNgoaiLe.value = gio;
  if (ngayNopInput) ngayNopInput.value = ngay;
  if (gioNopInput) gioNopInput.value = gio;
}

function capNhatThoiGianGiaoNhanRealTime() {
  const inputNgay = document.getElementById("transNgay");
  const inputGio = document.getElementById("transGio");
  if (!inputNgay || !inputGio) return;
  if (!cheDoRealTimeGiaoNhan) return;

  const thoiGian = layChuoiThoiGianHienTai();
  let coThayDoi = false;

  if (inputNgay.value !== thoiGian.ngay) {
    inputNgay.value = thoiGian.ngay;
    coThayDoi = true;
  }
  if (inputGio.value !== thoiGian.gio) {
    inputGio.value = thoiGian.gio;
    coThayDoi = true;
  }

  dongBoGiaTriThoiGian(inputNgay.value, inputGio.value);

  if (coThayDoi) {
    kiemTraGioDong();
  }
}

function nguoiDungSuaThoiGian() {
  cheDoRealTimeGiaoNhan = false;
  const inputNgay = document.getElementById("transNgay");
  const inputGio = document.getElementById("transGio");
  const badge = document.getElementById("liveClockBadge");
  const btnReset = document.getElementById("btnResetLiveClock");

  if (badge) {
    badge.className = "badge badge-amber";
    badge.textContent = "✎ Giờ chỉnh tay";
    badge.title = "Đang ở chế độ chỉnh tay. Nhấn để bật lại đồng bộ thời gian thực";
  }
  if (btnReset) {
    btnReset.style.display = "inline-flex";
  }

  if (inputNgay && inputGio) {
    dongBoGiaTriThoiGian(inputNgay.value, inputGio.value);
  }
  kiemTraGioDong();
}

function batLaiRealTime() {
  cheDoRealTimeGiaoNhan = true;
  const badge = document.getElementById("liveClockBadge");
  const btnReset = document.getElementById("btnResetLiveClock");

  if (badge) {
    badge.className = "badge badge-green";
    badge.textContent = "● Thời gian thực (Live)";
    badge.title = "Đang đồng bộ tự động theo thời gian thực";
  }
  if (btnReset) {
    btnReset.style.display = "none";
  }

  const thoiGian = layChuoiThoiGianHienTai();
  const inputNgay = document.getElementById("transNgay");
  const inputGio = document.getElementById("transGio");
  if (inputNgay) inputNgay.value = thoiGian.ngay;
  if (inputGio) inputGio.value = thoiGian.gio;

  dongBoGiaTriThoiGian(thoiGian.ngay, thoiGian.gio);
  kiemTraGioDong();
}

function kiemTraGioDong() {
  const selectQn = document.getElementById("chonQuanNhan");
  const inputNgay = document.getElementById("transNgay");
  const inputGio = document.getElementById("transGio");
  const hopLuat = document.getElementById("hopKiemTraLuat");

  if (inputNgay && inputGio) {
    dongBoGiaTriThoiGian(inputNgay.value, inputGio.value);
  }

  if (!selectQn || !hopLuat) return;

  const khoaQn = selectQn.value;
  const ngay = inputNgay ? inputNgay.value : "";
  const gio = inputGio ? inputGio.value : "";

  fetch(`/api/kiem-tra-gio?khoa_qn=${khoaQn}&ngay=${ngay}&gio=${gio}`)
    .then(r => r.json())
    .then(data => {
      const hopLuatIcon = document.getElementById("hopLuatIcon");
      const hopLuatTieuDe = document.getElementById("hopLuatTieuDe");
      const hopLuatMoTa = document.getElementById("hopLuatMoTa");
      const btnGiaoThuong = document.getElementById("btnGiaoThuong");
      const btnNgoaiLe = document.getElementById("btnNgoaiLe");

      if (data.hop_le) {
        hopLuat.className = "rule-box ok";
        if (hopLuatIcon) hopLuatIcon.textContent = "✓";
        if (hopLuatTieuDe) hopLuatTieuDe.textContent = "ĐƯỢC PHÉP MƯỢN";
        if (hopLuatMoTa) hopLuatMoTa.textContent = `${data.doi_tuong} · ${data.thong_bao}`;
        if (btnGiaoThuong) btnGiaoThuong.style.display = "inline-flex";
        if (btnNgoaiLe) btnNgoaiLe.style.display = "none";
      } else {
        hopLuat.className = "rule-box error";
        if (hopLuatIcon) hopLuatIcon.textContent = "⚠";
        if (hopLuatTieuDe) hopLuatTieuDe.textContent = "NGOÀI KHUNG GIỜ QUY ĐỊNH";
        if (hopLuatMoTa) hopLuatMoTa.textContent = `${data.doi_tuong} · ${data.thong_bao}`;
        if (btnGiaoThuong) btnGiaoThuong.style.display = "none";
        if (btnNgoaiLe) btnNgoaiLe.style.display = "inline-flex";
      }
    })
    .catch(() => {});
}

let donViHienTai = "ALL";

function locTheoDonVi(btn, donVi) {
  donViHienTai = donVi;
  const btns = document.querySelectorAll(".btn-loc-don-vi");
  btns.forEach(b => {
    b.classList.remove("active");
  });
  if (btn) {
    btn.classList.add("active");
  }
  locDanhSachQuanNhan();
}

function locDanhSachQuanNhan() {
  const input = document.getElementById("oTimKiemNhanh");
  const select = document.getElementById("chonQuanNhan");
  const goiY = document.getElementById("danhSachGoiYNhanh");
  if (!select) return;

  const tuKhoa = input ? input.value.trim().toLowerCase() : "";
  const options = select.querySelectorAll("option");
  let soKhop = 0;
  let goiYHtml = "";

  options.forEach(opt => {
    const hoTen = (opt.getAttribute("data-ho-ten") || "").toLowerCase();
    const maQn = (opt.getAttribute("data-ma-qn") || "").toLowerCase();
    const donVi = opt.getAttribute("data-don-vi") || "";
    const text = opt.textContent.toLowerCase();

    const khopDonVi = (donViHienTai === "ALL") || donVi.includes(donViHienTai);
    const khopTuKhoa = !tuKhoa || hoTen.includes(tuKhoa) || maQn.includes(tuKhoa) || text.includes(tuKhoa);

    if (khopDonVi && khopTuKhoa) {
      opt.hidden = false;
      opt.style.display = "";
      soKhop++;
      if (tuKhoa && soKhop <= 6) {
        goiYHtml += `<div onclick="chonNhanhQuanNhan('${opt.value}')" style="padding: 8px 12px; cursor: pointer; border-bottom: 1px solid #f1f5f9; font-size: 13px; display: flex; justify-content: space-between; align-items: center;" onmouseover="this.style.background='#f8fafc'" onmouseout="this.style.background='#ffffff'">
          <b>${opt.getAttribute("data-ho-ten") || opt.textContent}</b>
          <span style="font-size: 11px; color: #64748b;">${donVi}</span>
        </div>`;
      }
    } else {
      opt.hidden = true;
      opt.style.display = "none";
    }
  });

  if (goiY) {
    if (tuKhoa && soKhop > 0) {
      goiY.innerHTML = goiYHtml;
      goiY.style.display = "block";
    } else {
      goiY.style.display = "none";
    }
  }
}

function chonNhanhQuanNhan(id) {
  const select = document.getElementById("chonQuanNhan");
  if (!select) return;
  select.value = id;
  if (select.form) {
    select.form.submit();
  }
}

function xuLyPhimTimKiem(event) {
  if (event.key === "Enter") {
    event.preventDefault();
    const select = document.getElementById("chonQuanNhan");
    if (!select) return;
    const options = Array.from(select.querySelectorAll("option"));
    const firstMatch = options.find(opt => !opt.hidden && opt.style.display !== "none");
    if (firstMatch) {
      select.value = firstMatch.value;
      if (select.form) {
        select.form.submit();
      }
    }
  }
}

function truyenAnToan(s) {
  if (s === null || s === undefined) return "";
  const d = document.createElement("div");
  d.textContent = String(s);
  return d.innerHTML;
}

function khoiTaoSidebarResponsive() {
  const btnToggle = document.getElementById("btnToggleSidebar");
  const btnClose = document.getElementById("btnCloseSidebar");
  const sidebar = document.getElementById("sidebarMenu");
  const overlay = document.getElementById("sidebarOverlay");

  function moSidebar() {
    if (sidebar) sidebar.classList.add("is-open");
    if (overlay) overlay.classList.add("is-open");
    document.body.style.overflow = "hidden";
  }

  function dongSidebar() {
    if (sidebar) sidebar.classList.remove("is-open");
    if (overlay) overlay.classList.remove("is-open");
    document.body.style.overflow = "";
  }

  if (btnToggle) {
    btnToggle.addEventListener("click", function(e) {
      e.stopPropagation();
      if (sidebar && sidebar.classList.contains("is-open")) {
        dongSidebar();
      } else {
        moSidebar();
      }
    });
  }

  if (btnClose) {
    btnClose.addEventListener("click", dongSidebar);
  }

  if (overlay) {
    overlay.addEventListener("click", dongSidebar);
  }

  window.addEventListener("keydown", function(e) {
    if (e.key === "Escape" && sidebar && sidebar.classList.contains("is-open")) {
      dongSidebar();
    }
  });

  window.addEventListener("resize", function() {
    if (window.innerWidth > 1024 && sidebar && sidebar.classList.contains("is-open")) {
      dongSidebar();
    }
  });
}

document.addEventListener("DOMContentLoaded", function() {
  khoiTaoSidebarResponsive();
  const inputNgay = document.getElementById("transNgay");
  if (inputNgay) {
    capNhatThoiGianGiaoNhanRealTime();
    kiemTraGioDong();
    setInterval(capNhatThoiGianGiaoNhanRealTime, 1000);
  }
});

let dangChuyenTrang = false;
document.addEventListener("click", function(e) {
  const link = e.target.closest("a");
  if (!link) return;
  const href = link.getAttribute("href");
  if (!href || href.startsWith("#") || href.startsWith("javascript:") || href.startsWith("mailto:") || href.startsWith("tel:")) return;
  if (link.target === "_blank") return;
  if (link.origin === window.location.origin || href.startsWith("/")) {
    if (dangChuyenTrang) {
      e.preventDefault();
      return;
    }
    dangChuyenTrang = true;
    setTimeout(function() {
      dangChuyenTrang = false;
    }, 3000);
  }
});
