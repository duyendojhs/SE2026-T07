# Task #8 — Khởi tạo và refactor kiến trúc frontend

Tài liệu kiến trúc liên quan: [Kiến trúc frontend](../frontend/architecture.md)

---

## PHẦN I: GIAI ĐOẠN KHỞI TẠO SCAFFOLD (TASK #8 BAN ĐẦU)

### 1. Mục tiêu và phạm vi ban đầu

Khởi tạo Next.js 14 App Router + TypeScript trong `frontend/`, cấu hình Tailwind CSS và Lucide Icons, tạo sidebar responsive với Dashboard, Collaboration Heatmap, Stale Alerts, Audit Logs, cùng header hiển thị GitHub Rate-Limit Quota mẫu.

DoD của task: production build không lỗi; shell dùng được trên desktop và mobile.
Theo phản hồi thiết kế, bổ sung dashboard minh họa, bộ lọc kỳ, chart và trang chi tiết.
Đây là prototype frontend được yêu cầu thêm; không thay thế backend analytics.

### 2. Trạng thái ban đầu và ràng buộc

Repo có tài liệu quản trị, hướng dẫn AI và workflow kiểm tra cấu trúc, chưa có ứng dụng frontend. Stack frontend đã được xác định. Các kiểm thử phải offline và dùng fixture; sản phẩm chỉ xử lý metadata, không chấm điểm hay xếp hạng sinh viên.

### 3. Thay đổi đã thực hiện ban đầu

| Nhóm | Thay đổi | Tác dụng |
| --- | --- | --- |
| Công cụ | Next 14, TS strict, Tailwind 3, Lucide, ESLint, Prettier, Vitest | Nền phát triển thống nhất |
| Route | Cấu trúc phẳng, `/heatmap`, `not-found`, redirect URL cũ | Dễ tìm file và giữ liên kết cũ |
| Layout | AppShell, Sidebar, Header, PageHeader | Tách trách nhiệm, dùng chung chrome |
| Quota | Helper thuần, gauge có nhãn truy cập và trạng thái unavailable | Không giấu lỗi dữ liệu, dễ kiểm thử |
| Dashboard | 4 chỉ số, kỳ 3/7 ngày, chart riêng từng loại, tối đa 3 cảnh báo | Tổng quan có ưu tiên và lối đi sâu |
| Chi tiết | Heatmap, rule/evidence cảnh báo, Audit Logs empty state | Giữ Dashboard gọn |
| Màu | Token ngữ nghĩa, giao diện sáng | Tránh mã màu rải rác |
| Kiểm thử | `src/__tests__`, setup ở root frontend, fixture offline | Dễ tìm và chạy lại |
| CI | Lint, typecheck, format, test, build | Kiểm tra tự động khi push/PR phù hợp trigger |
| Tài liệu | README, kiến trúc và bản ghi task riêng | Phân biệt cách dùng, thiết kế và lý do |

### 4. Các quyết định thiết kế ban đầu và lý do

#### D1. Dùng route phẳng và root layout bọc AppShell
- **Vấn đề:** Phiên bản đầu có `app/(dashboard)/layout.tsx` và `page.tsx`; tên group dễ bị hiểu nhầm là quan hệ cha/con trên giao diện, đồng thời thêm tầng tìm file.
- **Phương án cân nhắc:** Giữ route group; thêm `/dashboard` với các route con; hoặc route phẳng dùng layout gốc. Chọn phương án phẳng vì bốn trang hiện đều có chung sidebar/header, chưa có khu vực đăng nhập hay layout khác. Phân cấp sidebar là quan hệ nghiệp vụ, không phải yêu cầu phân cấp URL.
- **Đánh đổi:** Trang mới cần chrome khác sẽ phải tách route group khi nhu cầu xuất hiện. Không tạo trước các layout chỉ để chuyển hướng hoặc dự phòng.

#### D2. Component PascalCase; tách AppShell, Header và PageHeader
- AppShell quản lý tương tác drawer; Header quản lý breadcrumb và telemetry; PageHeader trình bày tiêu đề/action trong nội dung. Tách ba vai trò để tránh một shell chứa cả logic điều hướng, drawer lẫn cách trình bày từng trang.
- Client boundary chỉ đặt ở phần cần state/hooks. Không chuyển root layout thành client component. Helper `cn` dùng `clsx` + `tailwind-merge` v2 tương thích Tailwind 3; chỉ sử dụng khi ghép class có thể xung đột như Panel.

#### D3. Quản lý menu ở navigation.ts, URL chi tiết là /heatmap
- Tên, URL, icon, nhóm menu nằm cùng nguồn để tránh sidebar và breadcrumb lệch nhau. URL ngắn giúp cấu trúc dễ đọc. Giữ redirect cho `/collaboration-heatmap` vì phiên bản trước đã dùng URL đó. Dashboard có tên nhất quán, không đổi qua lại với Overview.

#### D4. Giao diện sáng, compact panel và màu có ý nghĩa
- Đã tham khảo cách chia panel và drill-down của Grafana, cùng cách tổng hợp repository của GitHub Pulse. Sau thử nghiệm nền tối, chọn nền sáng theo yêu cầu. Bỏ tagline, mô tả lặp và thông tin triển khai khỏi dashboard; giữ một nhãn dữ liệu mẫu.
- Hàng đầu là ngữ cảnh và chỉ số; phần giữa là xu hướng/cảnh báo; cuối là tóm tắt. Cảnh báo không chiếm cả chiều ngang thành một khối dài trên desktop. Mobile ưu tiên cảnh báo trước chart. Màu ở `globals.css` tránh mỗi component tự chọn sắc độ.

#### D5. Tách current snapshot và selected period
- Số PR hiện chờ review không phải số phát sinh trong kỳ. Vì vậy hai nhóm chỉ số có nhãn phạm vi riêng. Không đổi snapshot khi chọn 3/7 ngày; chart, merged count và review-wait median cập nhật theo kỳ. Không cộng commit, PR và review thành một chỉ số tổng hợp vì con số đó khó diễn giải và dễ bị dùng làm đánh giá cá nhân.
- Median được dùng để minh họa thời gian chờ review với định nghĩa rõ; thiếu quan sát hiển thị dấu gạch thay vì 0. Tooltip và bảng số liệu giúp diễn giải dữ liệu.

#### D6. Fixture dùng chung và adapter có kiểu
- Không nối API khi contract backend chưa có. Fixture ở `backend/tests/mocks/` theo hướng dẫn repo, frontend tạo adapter có kiểu. Phép tính nằm trong model/helper thuần; UI nhận props. Khi có API, thay điểm cấp dữ liệu thay vì viết lại component.
- Đánh đổi: Cần checkout cả monorepo. Chưa thêm auth, token, HTTP client, cache client hay global state store khi chưa có nghiệp vụ tích hợp thật.

#### D7. Kiểm thử hành vi và commit theo mục đích
- Tách kiểm thử theo helper/component: quota bounds, median, bộ lọc, Sidebar active, drawer, route, missing data và giới hạn preview. Các commit chia thành khởi tạo, shell + kiểm thử, analytics + kiểm thử, CI và tài liệu. Không tách bằng số lượng file; mỗi phần phải build được với dependency của chính nó.
- Giữ lịch sử cũ trên `backup/8-frontend-scaffold-20261018`; tạo lại nhánh `chore/8-frontend-scaffold` từ `48aee32` theo yêu cầu làm sạch commit. Không push hoặc force-push. `.gitattributes` buộc LF cho frontend vì `core.autocrlf` trên Windows có thể làm format check của snapshot khác bản đang làm việc.

### 5. Điều chỉnh qua các lần thiết kế ban đầu
1. Ban đầu dùng các card dẫn đường và empty state.
2. Thêm dashboard theo độ quan trọng, sau đó thử phong cách Grafana tối.
3. Chuyển sang tông sáng, bỏ chữ dư và thống nhất palette theo phản hồi.
4. Tách tổng quan/chi tiết, giữ lại tên Dashboard nhất quán.
5. Bỏ route group, đổi `/heatmap` và PascalCase component theo sườn được thống nhất.

### 6. Các commit review giai đoạn ban đầu

| Commit | Nội dung review |
| --- | --- |
| `39a3c17` | Khởi tạo Next.js 14, cấu hình và công cụ phát triển |
| `0d39219` | Route phẳng, AppShell/Header/PageHeader, quota/helper và 13 kiểm thử |
| `1f57df3` | Dashboard analytics, bộ lọc, trang chi tiết; tổng 24 kiểm thử |
| `38f6c4b` | Job CI riêng cho frontend |
| `6cc63d7` | Ghi nhận tài liệu kiến trúc và quyết định task 8 ban đầu |

---

## PHẦN II: GIAI ĐOẠN REFACTOR KIẾN TRÚC & ĐỒNG BỘ TÀI LIỆU

### 1. Bối cảnh và mục tiêu refactor
- Nhánh `main` cập nhật backend S1 (FastAPI, Alembic migrations, GitHub OAuth/App auth, audit hash chain) và bổ sung các checks governance trong CI.
- Nhánh `chore/8-frontend-scaffold` cần được cập nhật qua việc merge `origin/main` (giữ lịch sử shared branch, không rebase).
- Mã nguồn frontend trước refactor có cấu trúc thư mục phẳng (`components/`, `types/`, `mocks/`, `lib/`), mã JSX của heatmap và stale-alerts bị viết inline trong route page, và tài liệu nằm cục bộ tại `frontend/docs/`.
- Mục tiêu: Tái cấu trúc source code thành Feature-based & Shared modules, tối ưu hóa ranh giới Server Component/Client Component, tập trung hóa cấu hình môi trường và API contract, và đồng bộ toàn bộ tài liệu về `/docs` ở root monorepo.

### 2. Các quyết định kiến trúc đợt refactor (D08 – D12)

#### D08. Tái cấu trúc theo Feature-based và Shared Cross-cutting Modules
- **Vấn đề:** Các thư mục dùng chung dạng phẳng (`components/`, `types/`, `mocks/`, `lib/`) khiến việc mở rộng tính năng mới khó quản lý ranh giới, khó tìm kiếm mã nguồn liên quan.
- **Giải pháp:** Tách rõ ràng thành:
  - `src/features/<feature>/`: Mỗi feature (`dashboard`, `heatmap`, `stale-alerts`, `audit-logs`, `telemetry`) tự đóng gói `components/`, `model.ts`, `types.ts`, `data.ts` (adapter), và public API qua `index.ts`.
  - `src/shared/`: Đóng gói các thành phần dùng chung xuyên suốt: `components/layout/` (AppShell, Header, Sidebar, PageHeader), `components/ui/` (Panel, EmptyState), `config/` (env, api, navigation), `lib/` (cn).

#### D09. Chuẩn hóa ranh giới Server Component và Client Component
- **Giải pháp:**
  - Toàn bộ file route trong `src/app/` (`page.tsx`, `heatmap/page.tsx`, `stale-alerts/page.tsx`, `audit-logs/page.tsx`, `not-found.tsx`) là Server Components 100%. Route page chỉ đọc URL query params, nạp dữ liệu và truyền props vào view component.
  - Tách nhỏ các component con chuyên biệt (`MetricsGrid.tsx`, `HeatmapTable.tsx`, `HeatmapLegend.tsx`, `AlertCard.tsx`, `AuditLogsView.tsx`) để mã nguồn mạch lạc, dễ kiểm thử và không bị phình to.
  - Chỉ giữ `"use client"` ở 4 vị trí thực sự cần state hoặc browser hooks: `AppShell` (quản lý modal dialog, phím tắt Escape, body overflow lock), `Header` (active route qua `usePathname`), `Sidebar` (menu link active), và `DashboardView` (quản lý state bộ lọc `3d`/`7d` và cập nhật searchParams qua `window.history.replaceState`).

#### D10. Đóng gói Offline Fixture Adapter ở cấp độ Feature
- **Giải pháp:** Di chuyển logic nạp fixture từ `src/mocks/*.ts` vào `src/features/*/data.ts`. UI components không bao giờ trực tiếp import file `.json` ngoài thư mục src hay monorepo backend tests, mà chỉ tiếp nhận domain model đã được định kiểu (`DashboardData`, `RateLimitQuota`). Điều này giúp việc chuyển đổi sang API service ở Sprint 3 diễn ra minh bạch và an toàn.

#### D11. Tập trung hóa cấu hình môi trường và API Endpoints
- **Giải pháp:** Bổ sung `src/shared/config/env.ts` và `src/shared/config/api.ts` quản lý URL backend (`NEXT_PUBLIC_API_URL` với fallback `http://localhost:8000`) và bản đồ các endpoint backend S1 (Auth, Tenant, Repos, Backfill Sync, Audit Hash Chain, Health/Ready), sẵn sàng cho việc tích hợp mà không hard-code URL rải rác.

#### D12. Đồng bộ hóa tài liệu về `/docs` ở root monorepo
- **Giải pháp:**
  - Chuyển `frontend/docs/architecture.md` thành `docs/frontend/architecture.md`.
  - Chuyển và hợp nhất toàn bộ `frontend/docs/tasks/008-frontend-scaffold.md` thành `docs/tasks/08-frontend-refactor.md`.
  - Hợp nhất mục lục `frontend/docs/README.md` vào `docs/README.md` ở root.
  - Xóa bỏ hoàn toàn thư mục `frontend/docs/` để tránh phân mảnh tài liệu.

### 3. Kết quả kiểm chứng sau refactor

Toàn bộ các lệnh kiểm tra của dự án được thực thi và xác nhận đạt yêu cầu 100%:

```sh
npm run lint          # Next.js ESLint: 0 errors, 0 warnings
npm run typecheck     # TypeScript strict check (tsc --noEmit): PASS
npm run format:check  # Prettier style check: PASS
npm test              # Vitest offline suite: 9 test files, 24/24 tests PASS
npm run build         # Next.js 14 production build: PASS (tất cả 7 static/dynamic pages)
```

Kiểm tra governance audit assets theo CI: PASS (13/13 governance files và test directories tồn tại đầy đủ).

### 4. Giới hạn hiện tại và công việc tiếp theo

- Dữ liệu frontend vẫn tiêu thụ qua offline fixture adapter (`features/*/data.ts`), chưa gọi HTTP trực tiếp đến backend FastAPI (chờ tích hợp ở Sprint 3).
- Dịch vụ Audit Logs và tóm tắt tiến độ tuần (Weekly summary) hiện tại dùng template xác định mẫu, chưa kết nối LLM pipeline.
- Upstream Tooling Advisories: `npm audit` ghi nhận một số advisory bảo mật từ Next.js 14/dependencies upstream; việc nâng version framework sẽ được đánh giá qua task riêng.

### 5. Tham chiếu tài liệu

- [Kiến trúc frontend](../frontend/architecture.md)
- [Mục lục tài liệu dự án](../README.md)
- [BUILD CONTRACT](../BUILD-CONTRACT.md)
- [.ai/AGENTS.md](../../.ai/AGENTS.md) và [PRIVACY.md](../../PRIVACY.md)
- [Grafana GitHub](https://grafana.com/docs/plugins/grafana-github-datasource/latest/) & [GitHub Pulse](https://docs.github.com/en/repositories/viewing-activity-and-data-for-your-repository/using-pulse-to-view-a-summary-of-repository-activity)
