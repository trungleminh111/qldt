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

let daXacNhanBanGiao = false;

function chuyenBuocCaTruc(buoc) {
  const b1 = document.getElementById("wizardStep1");
  const b2 = document.getElementById("wizardStep2");
  const b3 = document.getElementById("wizardStep3");
  const s1 = document.getElementById("stepperStep1");
  const s2 = document.getElementById("stepperStep2");
  const s3 = document.getElementById("stepperStep3");
  const l1 = document.getElementById("stepperLine1");
  const l2 = document.getElementById("stepperLine2");

  if (!b1 || !b2 || !b3) return;

  if (buoc === 2) {
    const chkKiemDem = document.getElementById("chkKiemDem");
    const chkKhoa = document.getElementById("chkKhoa");
    const chkChiaKhoa = document.getElementById("chkChiaKhoa");
    if (chkKiemDem && !chkKiemDem.checked) {
      alert("Đồng chí vui lòng xác nhận đã kiểm đếm thực tế đủ số máy trong tủ.");
      chkKiemDem.focus();
      return;
    }
    if (chkKhoa && !chkKhoa.checked) {
      alert("Đồng chí vui lòng xác nhận ổ khóa và tem niêm phong còn nguyên vẹn.");
      chkKhoa.focus();
      return;
    }
    if (chkChiaKhoa && !chkChiaKhoa.checked) {
      alert("Đồng chí vui lòng xác nhận đã bàn giao đủ bộ chìa khóa tủ.");
      chkChiaKhoa.focus();
      return;
    }
  } else if (buoc === 3) {
    const chonNguoiNhan = document.getElementById("chonNguoiNhan");
    const chonCaTruc = document.getElementById("chonCaTruc");
    if (chonNguoiNhan && !chonNguoiNhan.value) {
      alert("Đồng chí vui lòng chọn cán bộ tiếp nhận ca trực.");
      chonNguoiNhan.focus();
      return;
    }
    if (chonCaTruc && !chonCaTruc.value) {
      alert("Đồng chí vui lòng chọn ca trực tiếp nhận.");
      chonCaTruc.focus();
      return;
    }

    const revNguoiNhan = document.getElementById("reviewNguoiNhan");
    const revCaTruc = document.getElementById("reviewCaTruc");
    if (revNguoiNhan && chonNguoiNhan.selectedOptions.length > 0) {
      revNguoiNhan.innerText = chonNguoiNhan.selectedOptions[0].getAttribute("data-ho-ten") || chonNguoiNhan.selectedOptions[0].text;
    }
    if (revCaTruc && chonCaTruc.selectedOptions.length > 0) {
      revCaTruc.innerText = chonCaTruc.selectedOptions[0].getAttribute("data-ten-ca") || chonCaTruc.selectedOptions[0].text;
    }
  }

  b1.style.display = (buoc === 1) ? "block" : "none";
  b2.style.display = (buoc === 2) ? "block" : "none";
  b3.style.display = (buoc === 3) ? "block" : "none";

  if (s1) {
    s1.classList.toggle("active", buoc >= 1);
    s1.classList.toggle("completed", buoc > 1);
  }
  if (l1) {
    l1.classList.toggle("completed", buoc > 1);
  }
  if (s2) {
    s2.classList.toggle("active", buoc >= 2);
    s2.classList.toggle("completed", buoc > 2);
  }
  if (l2) {
    l2.classList.toggle("completed", buoc > 2);
  }
  if (s3) {
    s3.classList.toggle("active", buoc === 3);
  }

  window.scrollTo({ top: 0, behavior: "smooth" });
}

function kiemTraXacNhanBanGiao(event) {
  return kichHoatBanGiao(event);
}

function kichHoatBanGiao(event) {
  if (event) event.preventDefault();
  const form = document.getElementById("formBanGiaoCa");
  if (!form) return;

  if (!form.checkValidity()) {
    form.reportValidity();
    return;
  }

  const chkCamKet = document.getElementById("chkCamKet");
  if (chkCamKet && !chkCamKet.checked) {
    alert("Đồng chí vui lòng tích cam kết trách nhiệm quân sự trước khi bàn giao.");
    chkCamKet.focus();
    return;
  }

  const canhBao = document.getElementById("canhBaoChuaNop");
  if (canhBao && !daXacNhanBanGiao) {
    moModal("modalCanhBaoBanGiao");
    return;
  }

  form.submit();
}

function xacNhanGuiFormBanGiao() {
  daXacNhanBanGiao = true;
  dongModal("modalCanhBaoBanGiao");
  const form = document.getElementById("formBanGiaoCa");
  if (form) {
    form.submit();
  }
}

function thuHoiNhanhCaTruc(qnId, hoTen) {
  if (!confirm(`Đồng chí có chắc chắn muốn thu hồi nhanh điện thoại của ${hoTen} nộp về tủ bảo quản không?`)) {
    return;
  }
  const form = document.getElementById("formThuHoiNhanh");
  const input = document.getElementById("thuHoiKhoaQn");
  if (form && input) {
    input.value = qnId;
    form.submit();
  }
}

function truyenAnToan(s) {
  if (s === null || s === undefined) return "";
  const d = document.createElement("div");
  d.textContent = String(s);
  return d.innerHTML;
}

function xemChiTietBanGiao(id) {
  const modalNoiDung = document.getElementById("modalChiTietNoiDung");
  const modalTieuDe = document.getElementById("modalChiTietTieuDe");
  const btnIn = document.getElementById("modalBtnInBienBan");

  if (btnIn) {
    btnIn.href = `/ca-truc/bien-ban/${id}`;
  }
  if (modalTieuDe) {
    modalTieuDe.innerText = `Biên bản bàn giao ca trực #${id}`;
  }
  if (modalNoiDung) {
    modalNoiDung.innerHTML = `<div style="text-align: center; color: #64748b; padding: 20px;">Đang tải thông tin biên bản...</div>`;
  }
  moModal("modalChiTietBanGiao");

  fetch(`/ca-truc/api/chi-tiet/${id}`)
    .then(res => res.json())
    .then(data => {
      if (!data.thanh_cong || !data.ban_giao) {
        if (modalNoiDung) modalNoiDung.innerHTML = `<div style="color: #dc2626; text-align: center;">Không tải được dữ liệu biên bản.</div>`;
        return;
      }
      const bg = data.ban_giao;
      const snap = data.snapshot || {};
      const dsChuaNop = snap.danh_sach_chua_nop || [];

      let rowsHtml = "";
      if (dsChuaNop.length > 0) {
        dsChuaNop.forEach((item, idx) => {
          const mucDoClass = item.muc_do === "QUA_HAN" ? "badge-red" : (item.muc_do === "SAP_DEN_HAN" ? "badge-amber" : "badge-green");
          rowsHtml += `<tr style="border-bottom: 1px solid #e2e8f0;">
            <td style="padding: 6px 8px; text-align: center;">${idx + 1}</td>
            <td style="padding: 6px 8px;"><b>${truyenAnToan(item.ho_ten)}</b> (${truyenAnToan(item.ten_cap_bac)})</td>
            <td style="padding: 6px 8px;">${truyenAnToan(item.ten_don_vi)}</td>
            <td style="padding: 6px 8px;">${truyenAnToan(item.ten_dien_thoai)}</td>
            <td style="padding: 6px 8px; text-align: center;">${truyenAnToan(item.vi_tri_ngan || item.ten_ngan || "")}</td>
            <td style="padding: 6px 8px; text-align: center;"><span class="badge ${mucDoClass}">${truyenAnToan(item.nhan_trang_thai)}</span></td>
          </tr>`;
        });
      } else {
        rowsHtml = `<tr><td colspan="6" style="padding: 10px; text-align: center; color: #166534; font-style: italic;">✓ Tất cả thiết bị đã được thu hồi đầy đủ tại thời điểm bàn giao.</td></tr>`;
      }

      if (modalNoiDung) {
        modalNoiDung.innerHTML = `
          <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 12px; margin-bottom: 14px; font-size: 13px;">
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 8px;">
              <div><span style="color: #64748b;">Ca trực:</span> <b>${truyenAnToan(bg.ten_ca)} (${truyenAnToan(bg.gio_bat_dau)} - ${truyenAnToan(bg.gio_ket_thuc)})</b></div>
              <div><span style="color: #64748b;">Thời gian:</span> <b>${truyenAnToan(bg.thoi_gian_ban_giao)}</b></div>
              <div><span style="color: #64748b;">Bên bàn giao:</span> <b>${truyenAnToan(bg.ten_nguoi_ban_giao)}</b></div>
              <div><span style="color: #64748b;">Bên tiếp nhận:</span> <b>${truyenAnToan(bg.ten_nguoi_nhan)}</b></div>
            </div>
            <div style="border-top: 1px solid #e2e8f0; padding-top: 8px; display: flex; justify-content: space-around; text-align: center;">
              <div><small style="color: #64748b;">Tổng máy</small><b style="display: block; font-size: 16px;">${Number(bg.tong_thiet_bi) || 0}</b></div>
              <div><small style="color: #166534;">Trong tủ</small><b style="display: block; font-size: 16px; color: #166534;">${Number(bg.dang_trong_tu) || 0}</b></div>
              <div><small style="color: #b45309;">Đang mượn</small><b style="display: block; font-size: 16px; color: #b45309;">${Number(bg.da_lay) || 0}</b></div>
              <div><small style="color: #dc2626;">Quá hạn</small><b style="display: block; font-size: 16px; color: #dc2626;">${Number(bg.so_qua_han) || 0}</b></div>
            </div>
          </div>
          <div style="margin-bottom: 12px;">
            <div style="font-weight: 700; font-size: 12.5px; color: #0f2438; margin-bottom: 6px;">DANH SÁCH THIẾT BỊ NỢ TẠI THỜI ĐIỂM BÀN GIAO (SNAPSHOT):</div>
            <div style="max-height: 200px; overflow-y: auto; border: 1px solid #e2e8f0; border-radius: 6px;">
              <table style="width: 100%; border-collapse: collapse; font-size: 11.5px;">
                <thead>
                  <tr style="background: #f1f5f9; color: #334155;">
                    <th style="padding: 6px 8px; text-align: center;">STT</th>
                    <th style="padding: 6px 8px; text-align: left;">Quân nhân</th>
                    <th style="padding: 6px 8px; text-align: left;">Đơn vị</th>
                    <th style="padding: 6px 8px; text-align: left;">Thiết bị</th>
                    <th style="padding: 6px 8px; text-align: center;">Ngăn</th>
                    <th style="padding: 6px 8px; text-align: center;">Tình trạng</th>
                  </tr>
                </thead>
                <tbody>${rowsHtml}</tbody>
              </table>
            </div>
          </div>
          ${bg.ghi_chu_ban_giao ? `<div style="background: #fffbeb; border: 1px solid #fde68a; border-radius: 4px; padding: 8px 10px; font-size: 12px; font-style: italic; color: #92400e;">Ghi chú: "${truyenAnToan(bg.ghi_chu_ban_giao)}"</div>` : ""}
        `;
      }
    })
    .catch(() => {
      if (modalNoiDung) {
        modalNoiDung.innerHTML = `<div style="color: #dc2626; text-align: center; padding: 14px;">Lỗi kết nối khi tải chi tiết biên bản.</div>`;
      }
    });
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

document.addEventListener("click", function(e) {
  const link = e.target.closest("a");
  if (!link) return;
  if (link.target === "_blank") return;
  const href = link.getAttribute("href");
  if (!href || href.startsWith("#") || href.startsWith("javascript:")) return;
  if (link.origin === window.location.origin || href.startsWith("/")) {
    e.preventDefault();
    window.location.href = link.href;
  }
});
