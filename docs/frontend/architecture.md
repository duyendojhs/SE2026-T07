# Kiến trúc frontend

## 1. Mục đích và phạm vi

Frontend của GitHub Project Coach cung cấp giao diện trực quan hóa dữ liệu cộng tác của các nhóm sinh viên bằng cách khai thác metadata từ GitHub (commit, pull request, review, rate limit telemetry). Ứng dụng tập trung vào tính giải thích được (explainability), hỗ trợ phát hiện sớm nút thắt cổ chai mà không xâm phạm quyền riêng tư (không đọc source code, không xếp hạng hay chấm điểm cá nhân).

Ở giai đoạn hiện tại (S1/S2 chuẩn bị cho S3), frontend sử dụng Next.js 14 App Router, TypeScript, Tailwind CSS, Lucide Icons, kết nối qua adapter dữ liệu mẫu (offline fixture adapter) và đã sẵn sàng cấu hình để tích hợp API backend FastAPI.

## 2. Cấu trúc thư mục ứng dụng

Ứng dụng được tổ chức theo kiến trúc phân tách rõ ràng giữa Next.js App Router, các Module nghiệp vụ (Feature-based) và Thư viện dùng chung (Shared):

```text
frontend/
├── package.json
├── tsconfig.json
├── next.config.mjs
├── tailwind.config.ts
├── postcss.config.mjs
├── vitest.config.ts
├── vitest.setup.ts
└── src/
    ├── app/                               # Next.js 14 App Router (Routes & Layouts)
    │   ├── layout.tsx                     # Root Layout: HTML wrap, CSS, telemetry quota
    │   ├── globals.css                    # Semantic color tokens & base Tailwind layers
    │   ├── page.tsx                       # Route / (Dashboard)
    │   ├── heatmap/page.tsx               # Route /heatmap (Collaboration Heatmap)
    │   ├── stale-alerts/page.tsx          # Route /stale-alerts (Stale Pull Request Alerts)
    │   ├── audit-logs/page.tsx            # Route /audit-logs (Audit Logs)
    │   └── not-found.tsx                  # 404 handler
    ├── features/                          # Feature-driven business modules
    │   ├── dashboard/                     # Feature: Tổng quan dự án & metrics
    │   │   ├── components/
    │   │   │   ├── DashboardView.tsx      # Client Component: bộ lọc kỳ, bố cục dashboard
    │   │   │   ├── ActivityChart.tsx      # Chart CSS hiển thị PRs/reviews & bảng chi tiết
    │   │   │   └── MetricsGrid.tsx        # Grid thẻ 4 chỉ số chính với accessibility
    │   │   ├── model.ts                   # Pure domain logic: parse range, median, selectDashboard
    │   │   ├── types.ts                   # Types của dashboard & metrics
    │   │   ├── data.ts                    # Adapter đọc fixture dữ liệu mẫu
    │   │   └── index.ts                   # Public API của feature dashboard
    │   ├── heatmap/                       # Feature: Ma trận hoạt động cộng tác
    │   │   ├── components/
    │   │   │   ├── HeatmapView.tsx        # Bố cục màn hình heatmap
    │   │   │   ├── HeatmapTable.tsx       # Bảng ma trận sự kiện theo ngày & vai trò
    │   │   │   └── HeatmapLegend.tsx      # Chú thích mức độ hoạt động (heat scale)
    │   │   ├── model.ts                   # Logic bảng màu activityColor và danh sách hàng
    │   │   └── index.ts
    │   ├── stale-alerts/                  # Feature: Cảnh báo PR tồn đọng
    │   │   ├── components/
    │   │   │   ├── StaleAlertsView.tsx    # Bố cục danh sách cảnh báo
    │   │   │   └── AlertCard.tsx          # Thẻ chi tiết từng alert kèm rule & evidence
    │   │   └── index.ts
    │   ├── audit-logs/                    # Feature: Nhật ký truy cập metadata
    │   │   ├── components/
    │   │   │   └── AuditLogsView.tsx      # Trạng thái empty state & chuẩn bị kết nối backend
    │   │   └── index.ts
    │   └── telemetry/                     # Feature: Rate limit & quota GitHub
    │       ├── components/
    │       │   └── RateLimitGauge.tsx     # Thanh tiến độ và nhãn truy cập cho quota
    │       ├── model.ts                   # Tính ratio, quota level (warning/healthy), format reset UTC
    │       ├── types.ts                   # RateLimitQuota type
    │       ├── data.ts                    # Adapter quota fixture
    │       └── index.ts
    ├── shared/                            # Dùng chung giữa các feature
    │   ├── components/
    │   │   ├── layout/
    │   │   │   ├── AppShell.tsx           # Client Component: drawer state, scroll lock, responsive shell
    │   │   │   ├── Header.tsx             # Client Component: breadcrumb, mobile menu button, quota
    │   │   │   ├── Sidebar.tsx            # Client Component: danh mục điều hướng, active state
    │   │   │   ├── PageHeader.tsx         # Server Component: tiêu đề, mô tả và action trang
    │   │   │   └── index.ts
    │   │   └── ui/
    │   │       ├── Panel.tsx              # Khung card chuẩn với header & action
    │   │       ├── EmptyState.tsx         # Giao diện hiển thị khi chưa có dữ liệu
    │   │       └── index.ts
    │   ├── config/
    │   │   ├── env.ts                     # Tập trung biến môi trường và fallback an toàn
    │   │   ├── api.ts                     # URL map các endpoints backend (auth, audit, sync, health)
    │   │   └── navigation.ts              # Định nghĩa các route, nhãn, icon và nhóm menu
    │   └── lib/
    │       └── cn.ts                      # Utility hợp nhất classnames (clsx + tailwind-merge)
    └── __tests__/                         # Automated test suite (Vitest + Testing Library)
```

## 3. Trách nhiệm các module và ranh giới Server/Client

| Thành phần | Loại Component | Trách nhiệm chính |
| --- | --- | --- |
| `src/app/layout.tsx` | Server Component | Khai báo thẻ HTML gốc, load metadata, nạp CSS, truyền quota và bọc toàn bộ ứng dụng bằng `AppShell`. |
| `src/app/*` (Route pages) | Server Component | Đọc URL query searchParams (ví dụ `range`), gọi adapter/model để chuẩn bị dữ liệu, truyền props xuống các view component. Không nhúng state hoặc hooks client vào route. |
| `shared/components/layout/AppShell` | Client Component | Quản lý state mở/đóng mobile drawer, khóa cuộn trang (`body.style.overflow`), hỗ trợ phím Escape, backdrop click, focus trap và chứa `Sidebar`, `Header`. |
| `shared/components/layout/Header` | Client Component | Hiển thị breadcrumb tự động theo route hiện tại, nút mở drawer trên mobile và đồng hồ `RateLimitGauge`. |
| `shared/components/layout/Sidebar` | Client Component | Đọc route đang truy cập qua `usePathname` và render danh sách navigation theo nhóm. |
| `shared/components/layout/PageHeader` | Server Component | Trình bày tiêu đề trang, subtitle/meta và button action. |
| `features/dashboard/DashboardView` | Client Component | Quản lý tương tác chọn kỳ (`3d` / `7d`), đồng bộ query param qua `window.history.replaceState`, bố cục metrics grid, activity chart và preview cảnh báo. |
| `features/dashboard/model` | Pure TypeScript | Hàm thuần túy: parse URL range, tính median (bỏ qua số âm, NaN, infinite), tính aggregate kỳ. Hoàn toàn không phụ thuộc React/DOM. |
| `features/telemetry` | Feature Module | Quản lý kiểu, tính toán tỷ lệ còn lại của GitHub API quota, hiển thị `RateLimitGauge` với nhãn hỗ trợ accessibility (aria-valuenow, aria-valuetext). |
| `features/heatmap` | Feature Module | Hiển thị ma trận hoạt động theo từng loại sự kiện và ngày; legend biểu thị mức độ hoạt động. |
| `features/stale-alerts` | Feature Module | Hiển thị danh sách các pull request cần chú ý kèm rule và evidence cụ thể. |
| `features/audit-logs` | Feature Module | Hiển thị empty state giải thích mục đích nhật ký truy cập metadata; sẵn sàng nối API audit backend. |

## 4. Điều hướng và URL

Các route chính của hệ thống:
- `/`: Dashboard tổng quan, các chỉ số chính, biểu đồ xu hướng và danh sách cảnh báo ngắn gọn.
- `/heatmap`: Chi tiết ma trận hoạt động theo ngày và loại sự kiện (Commits, PRs opened, PRs merged, Reviews).
- `/stale-alerts`: Danh sách chi tiết các cảnh báo PR tồn đọng kèm theo quy tắc (rule) và bằng chứng (evidence).
- `/audit-logs`: Nhật ký truy cập và xử lý metadata.

**Quy ước chuyển hướng:**
- Route cũ `/collaboration-heatmap` được cấu hình permanent redirect sang `/heatmap` trong `next.config.mjs` để bảo đảm tính tương thích ngược cho liên kết cũ.
- Khi truy cập route không tồn tại, Next.js kích hoạt `not-found.tsx` hiển thị thông báo thân thiện và nút quay lại Dashboard.

## 5. Luồng dữ liệu và tích hợp API

```text
backend/tests/mocks/*.json → features/*/data.ts (Adapter)
                                       ↓
                               Route Pages (Server)
                                       ↓ (props)
                   Feature Views / Layout Shell (Client/Server)
                                       ↓
                                Pure Domain Models
                                       ↓
                                UI Presentation
```

- **Môi trường & API contracts:** File `src/shared/config/env.ts` và `src/shared/config/api.ts` tập trung hóa URL của backend (`NEXT_PUBLIC_API_URL` với fallback `http://localhost:8000`) cùng danh mục các endpoints backend (Auth, Tenant, Repository Sync, Audit Log, Health/Ready).
- **Nguyên tắc cô lập dữ liệu mẫu:** Chỉ các file `data.ts` trong từng feature module được phép import fixture từ `backend/tests/mocks/`. Toàn bộ UI components và route pages chỉ tiếp nhận dữ liệu đã được định kiểu chặt chẽ thông qua domain types.
- **Tính toán thuần túy:** Toàn bộ công thức tính toán (ví dụ median thời gian chờ review, tổng hợp kỳ, phân loại quota) được giữ trong các module `model.ts` độc lập để dễ dàng unit test ngoại tuyến mà không cần mount React.

## 6. Giao diện, Màu sắc và Accessibility

- **Bảng màu ngữ nghĩa:** Định nghĩa tập trung trong `src/app/globals.css` dưới dạng CSS variables (`--background`, `--surface`, `--primary`, `--success`, `--warning`, `--line`, v.v.) và được ánh xạ vào `tailwind.config.ts`.
- **Khả năng truy cập (a11y):**
  - Cung cấp skip link `#main-content` cho người dùng bàn phím.
  - Dialog drawer trên thiết bị di động tuân thủ chuẩn modal: native `<dialog>`, `aria-label`, quản lý focus khi đóng mở, đóng bằng phím Escape hoặc click backdrop.
  - Các phần tử số liệu và tiến độ quota đều có đầy đủ thuộc tính `role="progressbar"`, `aria-valuenow`, `aria-valuetext`.
  - Bảng biểu có thẻ `<caption className="sr-only">`, `scope="col"` và `scope="row"`.

## 7. Quy ước phát triển tiếp theo

- **Tên file & Component:** Component sử dụng PascalCase (`DashboardView.tsx`, `PageHeader.tsx`). Helper, model, types, config sử dụng camelCase hoặc kebab-case (`model.ts`, `types.ts`, `navigation.ts`).
- **Thêm tính năng mới:** Khi phát triển tính năng mới, tạo thư mục tương ứng trong `src/features/<feature-name>/` gồm các thành phần: `components/`, `model.ts`, `types.ts`, `data.ts` (hoặc `service.ts` khi gọi API) và export qua `index.ts`.
- **Không vi phạm biên sản phẩm:** Tuyệt đối không thu thập, lưu trữ hoặc hiển thị mã nguồn (source code, diffs, patches, blobs, comment bodies). Mọi chỉ số chỉ dừng ở cấp độ nhóm hoặc module, không tạo bảng xếp hạng cá nhân hay chỉ số silent member.
