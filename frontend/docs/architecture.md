# Kiến trúc frontend

## 1. Mục đích và phạm vi

GitHub Project Coach hỗ trợ theo dõi tiến độ và điểm nghẽn cộng tác bằng metadata
GitHub. Bản hiện tại là frontend scaffold kèm các màn hình minh họa bằng fixture.
Chưa có backend integration, xác thực, truy cập GitHub hoặc thực thi rule engine.

## 2. Cấu trúc hiện tại

```text
frontend/
├── docs/
│   ├── architecture.md
│   └── tasks/008-frontend-scaffold.md
├── vitest.config.ts
├── vitest.setup.ts
└── src/
    ├── app/
    │   ├── layout.tsx
    │   ├── globals.css
    │   ├── page.tsx
    │   ├── heatmap/page.tsx
    │   ├── stale-alerts/page.tsx
    │   ├── audit-logs/page.tsx
    │   └── not-found.tsx
    ├── components/
    │   ├── layout/{AppShell,Sidebar,Header,PageHeader}.tsx
    │   ├── telemetry/RateLimitGauge.tsx
    │   └── ui/{Panel,EmptyState}.tsx
    ├── config/navigation.ts
    ├── features/dashboard/
    │   ├── model.ts
    │   └── components/{DashboardView,ActivityChart}.tsx
    ├── lib/{cn,rate-limit}.ts
    ├── types/{telemetry,dashboard}.ts
    ├── mocks/{rate-limit,dashboard}.ts
    └── __tests__/
```

Các file cấu hình Next.js, Tailwind, PostCSS, TypeScript, ESLint và Prettier nằm
ở thư mục frontend. Tên component dùng PascalCase; helper, model và adapter dùng
kebab-case. Không có route group hoặc layout trung gian.

## 3. Trách nhiệm và ranh giới

| Thành phần        | Trách nhiệm                                                  |
| ----------------- | ------------------------------------------------------------ |
| Root layout       | Khai báo HTML, metadata, CSS; cấp quota mẫu và bọc AppShell  |
| AppShell          | State drawer, khóa cuộn, modal focus, bố trí trang           |
| Sidebar           | Đọc route hiện tại và cấu hình menu                          |
| Header            | Breadcrumb, nút menu mobile và quota                         |
| PageHeader        | Tiêu đề, metadata ngắn và action của trang                   |
| Route page        | Metadata, đọc query và ghép nội dung                         |
| DashboardView     | Bộ lọc và bố cục dashboard                                   |
| ActivityChart     | Các chuỗi hoạt động riêng và bảng số liệu thay thế           |
| model.ts          | Chọn kỳ, tổng hợp và tính median; không phụ thuộc React      |
| lib/rate-limit.ts | Kiểm tra quota, tỷ lệ còn lại, mức cảnh báo, thời điểm reset |
| lib/cn.ts         | Ghép class có điều kiện và xử lý xung đột Tailwind           |
| mocks             | Biên cấp dữ liệu mẫu có kiểu; nơi biết vị trí fixture        |

Root layout và route page là Server Components. AppShell, Sidebar, Header và
DashboardView là Client Components vì cần state hoặc route hooks. Server content
được truyền qua children của AppShell, không biến toàn bộ route thành client code.
Header được ghép trong AppShell; PageHeader không cần client boundary riêng.

## 4. Điều hướng và URL

| URL             | Vai trò                                                   |
| --------------- | --------------------------------------------------------- |
| `/`             | Dashboard: chỉ số, xu hướng, cảnh báo rút gọn, tóm tắt kỳ |
| `/heatmap`      | Chi tiết hoạt động theo ngày và loại sự kiện              |
| `/stale-alerts` | Cảnh báo hiện tại, rule và bằng chứng                     |
| `/audit-logs`   | Empty state cho nhật ký, chờ tích hợp backend             |

`navigation.ts` là nguồn duy nhất cho URL, nhãn, icon và nhóm menu. Dashboard là
điểm bắt đầu; hai trang phân tích được thụt lề trong sidebar; Audit Logs thuộc System.
Phân cấp nghiệp vụ của menu không bắt buộc tạo thêm tầng thư mục hay URL.

`/collaboration-heatmap` chuyển hướng vĩnh viễn sang `/heatmap` để các liên kết cũ
vẫn dùng được. Route không hợp lệ hiển thị not-found với lối về Dashboard.

## 5. Luồng và ngữ nghĩa dữ liệu

```text
backend/tests/mocks/*.json → src/mocks → Server route/root layout
                                       → props → component → pure model → UI
```

Chỉ adapter import fixture. UI nhận dữ liệu qua props hoặc route composition.
Sườn này cần checkout monorepo đầy đủ để đọc fixture dùng chung. Đây là đánh đổi
có chủ ý cho kiểm thử offline, chưa phải frontend package chạy độc lập.

Bộ lọc `range=7d|3d` được chuẩn hóa trước khi dùng. Dashboard cập nhật state và URL;
liên kết trang chi tiết và liên kết quay lại mang theo range. Kỳ mẫu neo vào ngày
trong fixture, không phải ngày thực tế của máy.

- Awaiting review và Stale PRs là current snapshot, không đổi theo kỳ lịch sử.
- Merged PRs và median review wait áp dụng cho kỳ được chọn.
- Review wait là số giờ từ mở PR đến review đầu tiên, tính trên các lần review
  đầu tiên được ghi nhận trong kỳ. Không có quan sát hợp lệ thì hiển thị `—`.
- Số 0 khác với thiếu dữ liệu; thời lượng âm hoặc không hữu hạn bị loại khi tính median.
- PR mở, PR merge và review là ba chuỗi riêng, không cộng thành điểm đánh giá.
- Tóm tắt là văn bản xác định từ fixture, chưa phải báo cáo do LLM tạo.
- Quota không hợp lệ hiển thị unavailable; còn từ 20% trở xuống dùng warning.
  Reset nếu có hiển thị UTC để tránh phụ thuộc timezone của máy.

Chỉ xử lý metadata; không thu thập source code, xếp hạng hay tự động chấm điểm cá nhân.

## 6. Giao diện và khả năng truy cập

Màu được khai báo tập trung trong globals.css và ánh xạ qua Tailwind: surface,
foreground, secondary, muted, line, primary, success, warning. Màu tím của chuỗi
review là màu phân loại dữ liệu, không mang ý nghĩa cảnh báo. Tailwind quét toàn src.

Từ 1024px sidebar cố định; dưới ngưỡng này dùng native modal dialog. Menu hỗ trợ
Escape, backdrop, đóng khi chọn trang, focus containment và trả focus về nút mở.
Có skip link, aria-current và breadcrumb được đặt tên riêng.

Thẻ số liệu dùng 2 cột, mở thành 4 cột từ 1280px. Biểu đồ và cảnh báo dùng tỷ lệ
2:1 ở màn hình rộng; trên mobile cảnh báo nằm trước biểu đồ. Chart có chú giải,
nhãn truy cập và bảng số liệu mở rộng; heatmap dùng bảng có row/column headers.

## 7. Kiểm tra và hướng tích hợp

Chạy lint, typecheck, format:check, test và build theo README. Kiểm thử không gọi
mạng; fixture nằm tại backend/tests/mocks. CI cài dependency trước khi chạy kiểm tra.

Khi tích hợp API: thống nhất contract, thay mock adapter, thêm loading/error/empty
states theo nguồn dữ liệu thật. Token và truy cập GitHub ở server. Chưa cần global
state store hay HTTP abstraction khi chưa có nhiều nơi dùng chung.

Next.js 14.2.35 được giữ theo task. npm audit còn advisory của framework/tooling;
việc nâng major version cần task riêng. Không khẳng định audit bảo mật đã sạch.
