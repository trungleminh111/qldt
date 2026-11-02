# Project: Quản lý điện thoại đại đội (QLDT) - Full System Evolution

## Architecture
- **Framework**: Flask MVC (Python 3.12, Jinja2, SQLite3 standard library)
- **Database**: `qldt.db` (Relational tables: `don_vi`, `tai_khoan`, `vai_tro`, `quyen_han`, `vai_tro_quyen`, `tai_khoan_vai_tro`, `quan_nhan`, `dien_thoai`, `tu`, `ngan`, `lich_su_giao_nhan`, `ca_truc`, `ban_giao_ca`)
- **Controllers / Blueprints (8)**:
  - `auth`: Đăng nhập, đăng xuất, đổi mật khẩu
  - `dashboard`: Bảng điều khiển trung tâm, biểu đồ thống kê
  - `giao_nhan`: Giao máy, nhận máy, danh sách chưa nộp, lịch sử
  - `quan_nhan`: Danh sách, hồ sơ, thêm/sửa/xóa quân nhân, gán tủ & ngăn trống
  - `dien_thoai`: Danh sách máy, quản lý tủ/ngăn động, sơ đồ tủ trực quan
  - `ca_truc`: Quản lý ca trực, bàn giao ca trực kèm snapshot
  - `cau_hinh`: Khung giờ sử dụng, tài khoản & vai trò động (`/tai-khoan-phan-quyen`)
  - `bao_cao`: Xuất excel, biểu mẫu in A4
- **UI Architecture & Layout**:
  - Fixed 100vh Sidebar with independent `overflow-y: auto`.
  - Main content scrolls independently (`margin-left: 260px; width: calc(100% - 260px)`).
  - Responsive toggle off-canvas menu for screen widths < 1024px with overlay, close button (✕), and Escape key support.
  - Standard Military Button Design System: `.btn-quan-doi`, `.btn-qd-primary`, `.btn-qd-secondary`, `.btn-qd-success`, `.btn-qd-warning`, `.btn-qd-danger`, `.btn-qd-ghost`, `.btn-qd-sm`, `.btn-qd-md`, `.btn-qd-lg`, 6px border radius, standardized icons and color palette.
- **Dynamic Lockers & History Snapshots**:
  - Dynamic compartments per cabinet (no hardcoded 24-compartment limit).
  - Safe deletion: reject deletion if compartment is assigned to personnel (`ngan.khoa_quan_nhan IS NOT NULL`). Soft delete when vacant.
  - Snapshot fields `ma_tu_snapshot` and `ten_ngan_snapshot` in `lich_su_giao_nhan` and `ban_giao_ca` with automated schema migration and backfill.
- **Multi-Phone per Soldier & Vacant Compartment Allocation**:
  - Modal Create/Edit Personnel: Dynamic dropdowns for Cabinet and vacant compartments (`GET /api/tu/<id>/ngan-trong`).
  - 1 personnel owns 1 locker compartment; multiple phones (2-3 devices) belonging to that personnel are stored together in that compartment.
  - Handover screen: list each phone with individual checkboxes; duty officer can check-in/out individual phones or choose "Giao nhận tất cả máy". Backward compatible fallback.
  - Cabinet diagram: displays total phones stored and individual status (e.g. "2 máy: 1 trong tủ, 1 đã lấy") without duplicating compartment cells.
- **Dynamic Military Roles**:
  - `bac_vai_tro` stored directly in table `vai_tro` with automated migration.
  - Form "+ Thêm vai trò mới" at `/tai-khoan-phan-quyen`: Role Name, Role Code, Role Rank (`bac_vai_tro`), Description, and functional permission checkboxes.
  - Backend validation prevents lower ranks from creating higher roles or creating duplicate `QUAN_TRI`.
  - New roles appear dynamically in role lists and user assignment dropdowns.
- **Clean Code Rule**: 100% Zero comments (`#`, `//`, `/*`, `<!--`, `{# #}`) across all source code and templates.

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| F1 | Salted Password Hashing | Upgrade from unsalted SHA-256 to `werkzeug.security` with lazy migration | M1 | ORIGINAL_REQUEST §R2 |
| F2 | Session Hardening | Secure cookie flags, session regeneration | M1 | ORIGINAL_REQUEST §R2 |
| F3 | RBAC Enforcement Decorator | `@yeu_cau_quyen(*quyen_hop_le)` on controller endpoints | M1 | ORIGINAL_REQUEST §R2 |
| F4 | Super Admin Protection | Prevent editing/deleting `admin` except by `admin`; enforce role hierarchy | M1 | ORIGINAL_REQUEST §R2 |
| F5 | UI Sidebar Menu Scoping | Hide administrative menus in `base.html` for non-admins | M1 | ORIGINAL_REQUEST §R2 |
| F6 | Data Scoping (`pham_vi_loai`) | Filter data according to platoon/unit scope | M2 | ORIGINAL_REQUEST §R2 |
| F7 | Trực ban Quick Search (<5s) | Real-time JS soldier search/filter in `giao_nhan/index.html` | M3 | ORIGINAL_REQUEST §R1 |
| F8 | A4 Report 1-Click Print | Add direct print button & back button with print-hidden CSS | M3 | ORIGINAL_REQUEST §R3 |
| F9 | Shift Handover Warning | Red/amber warning banner, unreturned device list, modal confirmation | M3 | ORIGINAL_REQUEST §R1 |
| F10 | Dashboard & Cabinet Visuals | Overdue list on dashboard; military red highlight on locker cells | M3 | ORIGINAL_REQUEST §R3 |
| F11 | Zero Comments Clean Code | 100% comment elimination across all code and templates | M4 | ORIGINAL_REQUEST §R3 |
| F12 | Military Persona E2E Tests | 4-Tier test suite verifying 4 roles | M5 | ORIGINAL_REQUEST §R1 |
| F13 | Fixed 100vh Sidebar & Independent Scroll | Sidebar fixed 100vh with `overflow-y: auto`; main content scrolls independently | M6 | ORIGINAL_REQUEST 2026-10-30 §R1 |
| F14 | Responsive Toggle Off-Canvas (<1024px) | Responsive toggle button (☰), overlay, close (✕), ESC shortcut, no content obstruction | M6 | ORIGINAL_REQUEST 2026-10-30 §R1 |
| F15 | Standard Military Button Design System | Unified `.btn-quan-doi`, `.btn-qd-*`, 6px border radius, standard sizes, colors, icons | M6 | ORIGINAL_REQUEST 2026-10-30 §R1 |
| F16 | Dynamic Compartments per Cabinet | Add new compartments dynamically per cabinet without hardcoded 24 limit | M7 | ORIGINAL_REQUEST 2026-10-30 §R2 |
| F17 | Safe Compartment Deletion | Strictly reject deletion of assigned compartments; soft-delete vacant ones | M7 | ORIGINAL_REQUEST 2026-10-30 §R2 |
| F18 | Snapshot History Tracking | `ma_tu_snapshot`, `ten_ngan_snapshot` in transaction logs & handover logs with migration | M7 | ORIGINAL_REQUEST 2026-10-30 §R2 |
| F19 | Vacant Compartment Allocation Modal | Dropdowns for Cabinet and vacant compartments in Create/Edit Personnel modal | M8 | ORIGINAL_REQUEST 2026-10-30 §R3 |
| F20 | Multi-Phone per Personnel in 1 Locker | Support 2-3 phones per soldier stored in same compartment without row duplication | M8 | ORIGINAL_REQUEST 2026-10-30 §R3 |
| F21 | Multi-Device Handover & Diagram Details | Checkbox list per device or "Giao nhận tất cả máy"; diagram shows detailed phone counts & status | M8 | ORIGINAL_REQUEST 2026-10-30 §R3 |
| F22 | Dynamic Military Roles Management | "+ Thêm vai trò mới" form, `bac_vai_tro` persistence, role hierarchy, immediate assignment | M9 | ORIGINAL_REQUEST 2026-10-30 §R4 |
| F23 | Comprehensive E2E Verification & Audit | Tiers 1-5 tests, zero comments check, forensic integrity audit | M10 | Acceptance Criteria |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M1 | Security & Access Control | F1, F2, F3, F4, F5 | none | DONE |
| M2 | Data Scoping & Unit Isolation | F6 | M1 | DONE |
| M3 | Military UX Refinements | F7, F8, F9, F10 | none | DONE |
| M4 | Clean Code Verification | F11 | M1, M2, M3 | DONE |
| M5 | Persona Testing & E2E Verification | F12 | M1, M2, M3, M4 | DONE |
| M6 | UI/UX Foundation: Fixed Sidebar 100vh, Responsive Toggle & Military Button System | F13, F14, F15 | none | PLANNED |
| M7 | Dynamic Cabinets/Compartments & Snapshot History Tracking | F16, F17, F18 | none | PLANNED |
| M8 | Vacant Compartment Allocation & Multi-Phone Support per Soldier | F19, F20, F21 | M7 | PLANNED |
| M9 | Dynamic Military Roles Management (`/tai-khoan-phan-quyen`) | F22 | none | PLANNED |
| M10 | Final Milestone: Comprehensive E2E Verification & Integrity Audit | F23 | M6, M7, M8, M9 | PLANNED |

## Interface Contracts

### UI & Layout Contracts (M6)
- Base layout: `templates/base.html`
  - `.app-shell`: root container
  - `.sidebar`: `position: fixed; top: 0; left: 0; bottom: 0; width: 260px; height: 100vh; overflow: hidden;`
  - `.sidebar-nav`: `flex: 1; overflow-y: auto;`
  - `.main-content`: `margin-left: 260px; width: calc(100% - 260px); min-height: 100vh;`
  - Topbar responsive button: `<button type="button" class="btn-sidebar-toggle" id="btnToggleSidebar" aria-label="Menu">☰</button>` (visible only on <= 1024px)
  - Sidebar close button: `<button type="button" class="btn-sidebar-close" id="btnCloseSidebar" aria-label="Đóng">✕</button>` (visible only on <= 1024px)
  - Overlay: `<div class="sidebar-overlay" id="sidebarOverlay"></div>`
- Military Button System: `static/css/style.css`
  - Base: `.btn-quan-doi` (and `.btn` alias for backward compatibility), `border-radius: 6px !important;`
  - Variants: `.btn-qd-primary`, `.btn-qd-secondary`, `.btn-qd-success`, `.btn-qd-warning`, `.btn-qd-danger`, `.btn-qd-ghost`
  - Sizes: `.btn-qd-sm` (5px 10px, 11px), `.btn-qd-md` (9px 16px, 12.5px), `.btn-qd-lg` (12px 20px, 13.5px, bold), `.btn-qd-block`

### Cabinet & Compartment Contracts (M7)
- Endpoints in `controllers/dien_thoai_controller.py`:
  - `POST /ngan/them`: Add new compartment to cabinet (`khoa_tu`, optional `ten_ngan`).
  - `POST /ngan/xoa/<int:id>`: Safe deletion. If `khoa_quan_nhan IS NOT NULL`, reject with flash warning. If vacant, soft delete (`dang_dung = 0`).
- Models in `models/dien_thoai_model.py`:
  - `them_ngan(khoa_tu, ten_ngan=None)` -> creates new compartment record, increments `tu.so_ngan`.
  - `xoa_ngan(khoa_ngan)` -> checks assignment, performs soft delete, updates `tu.so_ngan`.
- Snapshot fields in `models/co_so_du_lieu.py`:
  - `lich_su_giao_nhan`: `ma_tu_snapshot TEXT`, `ten_ngan_snapshot TEXT`
  - `ban_giao_ca`: `ma_tu_snapshot TEXT`, `ten_ngan_snapshot TEXT`
  - Auto-migration and backfill on application startup.
  - Queries in `models/giao_nhan_model.py` and `models/ca_truc_model.py` populate snapshots on INSERT and use `COALESCE(gn.ten_ngan_snapshot, ng.ten_ngan)`.

### Personnel & Multi-Phone Contracts (M8)
- Endpoints:
  - `GET /api/tu/<int:khoa_tu>/ngan-trong`: Query vacant compartments in cabinet (including current soldier's compartment if `khoa_qn` provided).
  - `POST /quan-nhan/them`: Supports selecting `khoa_tu` and `khoa_ngan`.
  - `POST /quan-nhan/sua/<int:id>`: Supports updating `khoa_tu` and `khoa_ngan`.
  - `POST /giao-nhan/lay` and `POST /giao-nhan/nop`: Accepts `danh_sach_dien_thoai` list of device IDs; fallback to all soldier devices if omitted.
- Visual diagram: `models/dien_thoai_model.py:lay_so_do_tu()` returns grouped compartment info with `tong_so_may`, `so_trong_tu`, `so_da_lay`, and device list.

### Dynamic Roles Contracts (M9)
- Table `vai_tro`: Column `bac_vai_tro INTEGER DEFAULT 10`
- Model `models/phan_quyen_model.py`:
  - `them_vai_tro(ten_vai_tro, ma_vai_tro, bac_vai_tro, mo_ta, danh_sach_khoa_quyen)`
  - `lay_bac_vai_tro(ma_vai_tro)` queries DB first, fallback to static map.
- Controller `controllers/cau_hinh_controller.py`:
  - Route `POST /vai-tro/them` with `@yeu_cau_quyen("QUANTRI.TAIKHOAN")`.
  - Form validation: rank checking, prevent `QUAN_TRI` duplication, safe integer parsing.
- Template `templates/cau_hinh/phan_quyen.html`:
  - Button `＋ Thêm vai trò mới` -> modal `modalThemVaiTro`.
  - Checkbox grid of permissions loaded from `quyen_list`.

## Code Layout
- `static/css/style.css`: Fixed sidebar, responsive drawer, military button design system
- `static/js/app.js`: Sidebar toggle handlers (☰, ✕, overlay, Escape key)
- `templates/base.html`: Structure with toggle button, overlay, close button
- `templates/**/*.html`: Standard military button classes across all 17 templates
- `models/co_so_du_lieu.py`: Schema definitions, auto-migrations for `bac_vai_tro`, `ma_tu_snapshot`, `ten_ngan_snapshot`
- `models/dien_thoai_model.py`: Dynamic compartment addition/deletion, diagram grouping
- `models/quan_nhan_model.py`: Compartment allocation on create/edit, multi-phone queries
- `models/giao_nhan_model.py`: Multi-device checkout/in, snapshot population, fallback handling
- `models/ca_truc_model.py`: Snapshot population for handover
- `models/phan_quyen_model.py`: Dynamic roles creation, rank checks
- `controllers/dien_thoai_controller.py`: Endpoints for compartment add/delete and vacant list API
- `controllers/quan_nhan_controller.py`: Handle locker assignment on create/edit
- `controllers/giao_nhan_controller.py`: Multi-device checkout/in handling
- `controllers/cau_hinh_controller.py`: Route `POST /vai-tro/them`
- `tests/`: 4-Tier test suite covering R1-R4, persona verification, and zero comments audit
