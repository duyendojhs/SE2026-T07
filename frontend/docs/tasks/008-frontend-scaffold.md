# Task #8 — Khởi tạo frontend và dashboard shell

## 1. Mục tiêu và phạm vi

Khởi tạo Next.js 14 App Router + TypeScript trong frontend, cấu hình Tailwind và
Lucide, tạo sidebar responsive với Dashboard, Collaboration Heatmap, Stale Alerts,
Audit Logs, cùng header hiển thị GitHub Rate-Limit Quota mẫu.

DoD của task: production build không lỗi; shell dùng được trên desktop và mobile.
Theo phản hồi thiết kế, bổ sung dashboard minh họa, bộ lọc kỳ, chart và trang chi tiết.
Đây là prototype frontend được yêu cầu thêm; không thay thế backend analytics.

## 2. Trạng thái ban đầu và ràng buộc

Repo có tài liệu quản trị, hướng dẫn AI và workflow kiểm tra cấu trúc, chưa có ứng
dụng frontend. Stack frontend đã được xác định. Các kiểm thử phải offline và dùng
fixture; sản phẩm chỉ xử lý metadata, không chấm điểm hay xếp hạng sinh viên.

## 3. Thay đổi đã thực hiện

| Nhóm      | Thay đổi                                                         | Tác dụng                                     |
| --------- | ---------------------------------------------------------------- | -------------------------------------------- |
| Công cụ   | Next 14, TS strict, Tailwind 3, Lucide, ESLint, Prettier, Vitest | Nền phát triển thống nhất                    |
| Route     | Cấu trúc phẳng, /heatmap, not-found, redirect URL cũ             | Dễ tìm file và giữ liên kết cũ               |
| Layout    | AppShell, Sidebar, Header, PageHeader                            | Tách trách nhiệm, dùng chung chrome          |
| Quota     | Helper thuần, gauge có nhãn truy cập và trạng thái unavailable   | Không giấu lỗi dữ liệu, dễ kiểm thử          |
| Dashboard | 4 chỉ số, kỳ 3/7 ngày, chart riêng từng loại, tối đa 3 cảnh báo  | Tổng quan có ưu tiên và lối đi sâu           |
| Chi tiết  | Heatmap, rule/evidence cảnh báo, Audit Logs empty state          | Giữ Dashboard gọn                            |
| Màu       | Token ngữ nghĩa, giao diện sáng                                  | Tránh mã màu rải rác                         |
| Kiểm thử  | src/**tests**, setup ở root frontend, fixture offline            | Dễ tìm và chạy lại                           |
| CI        | Lint, typecheck, format, test, build                             | Kiểm tra tự động khi push/PR phù hợp trigger |
| Tài liệu  | README, kiến trúc và bản ghi task riêng                          | Phân biệt cách dùng, thiết kế và lý do       |

## 4. Các quyết định và lý do

### D1. Dùng route phẳng và root layout bọc AppShell

**Vấn đề:** phiên bản đầu có app/(dashboard)/layout.tsx và page.tsx; tên group dễ
bị hiểu nhầm là quan hệ cha/con trên giao diện, đồng thời thêm tầng tìm file.

**Phương án cân nhắc:** giữ route group; thêm /dashboard với các route con; hoặc
route phẳng dùng layout gốc. Chọn phương án phẳng vì bốn trang hiện đều có chung
sidebar/header, chưa có khu vực đăng nhập hay layout khác. Phân cấp sidebar là
quan hệ nghiệp vụ, không phải yêu cầu phân cấp URL.

**Đánh đổi:** trang mới cần chrome khác sẽ phải tách route group khi nhu cầu xuất
hiện. Không tạo trước các layout chỉ để chuyển hướng hoặc dự phòng.

### D2. Component PascalCase; tách AppShell, Header và PageHeader

AppShell quản lý tương tác drawer; Header quản lý breadcrumb và telemetry;
PageHeader trình bày tiêu đề/action trong nội dung. Tách ba vai trò để tránh một
shell chứa cả logic điều hướng, drawer lẫn cách trình bày từng trang.

Client boundary chỉ đặt ở phần cần state/hooks. Không chuyển root layout thành
client component. features/dashboard được giữ để route page không chứa toàn bộ
chart, số liệu và phép tính. Helper cn dùng clsx + tailwind-merge v2 tương thích
Tailwind 3; chỉ sử dụng khi ghép class có thể xung đột như Panel.

### D3. Quản lý menu ở navigation.ts, URL chi tiết là /heatmap

Tên, URL, icon, nhóm menu nằm cùng nguồn để tránh sidebar và breadcrumb lệch nhau.
URL ngắn giúp cấu trúc dễ đọc. Giữ redirect cho /collaboration-heatmap vì phiên bản
trước đã dùng URL đó. Dashboard có tên nhất quán, không đổi qua lại với Overview.

### D4. Giao diện sáng, compact panel và màu có ý nghĩa

Đã tham khảo cách chia panel và drill-down của Grafana, cùng cách tổng hợp
repository của GitHub Pulse. Sau thử nghiệm nền tối, chọn nền sáng theo yêu cầu.
Bỏ tagline, mô tả lặp và thông tin triển khai khỏi dashboard; giữ một nhãn dữ liệu mẫu.

Hàng đầu là ngữ cảnh và chỉ số; phần giữa là xu hướng/cảnh báo; cuối là tóm tắt.
Cảnh báo không chiếm cả chiều ngang thành một khối dài trên desktop. Mobile ưu tiên
cảnh báo trước chart. Màu ở globals.css tránh mỗi component tự chọn sắc độ.

### D5. Tách current snapshot và selected period

Số PR hiện chờ review không phải số phát sinh trong kỳ. Vì vậy hai nhóm chỉ số có
nhãn phạm vi riêng. Không đổi snapshot khi chọn 3/7 ngày; chart, merged count và
review-wait median cập nhật theo kỳ. Không cộng commit, PR và review thành một
chỉ số tổng hợp vì con số đó khó diễn giải và dễ bị dùng làm đánh giá cá nhân.

Median được dùng để minh họa thời gian chờ review với định nghĩa rõ; thiếu quan
sát hiển thị dấu gạch thay vì 0. Tooltip và bảng số liệu giúp diễn giải dữ liệu.

### D6. Fixture dùng chung và adapter có kiểu

Không nối API khi contract backend chưa có. Fixture ở backend/tests/mocks theo
hướng dẫn repo, frontend/src/mocks là adapter. Phép tính nằm trong model/helper
thuần; UI nhận props. Khi có API, thay điểm cấp dữ liệu thay vì viết lại component.

Đánh đổi: cần checkout cả monorepo. Chưa thêm auth, token, HTTP client, cache client
hay global state store khi chưa có nghiệp vụ tích hợp thật.

### D7. Kiểm thử hành vi và commit theo mục đích

Tách kiểm thử theo helper/component: quota bounds, median, bộ lọc, Sidebar active,
drawer, route, missing data và giới hạn preview. Các commit chia thành khởi tạo,
shell + kiểm thử, analytics + kiểm thử, CI và tài liệu. Không tách bằng số lượng
file; mỗi phần phải build được với dependency của chính nó.

Giữ lịch sử cũ trên backup/8-frontend-scaffold-20261018; tạo lại nhánh
chore/8-frontend-scaffold từ 48aee32 theo yêu cầu làm sạch commit. Không push hoặc
force-push. .gitattributes buộc LF cho frontend vì core.autocrlf trên Windows có
thể làm format check của snapshot khác bản đang làm việc.

## 5. Điều chỉnh qua các lần thiết kế

1. Ban đầu dùng các card dẫn đường và empty state.
2. Thêm dashboard theo độ quan trọng, sau đó thử phong cách Grafana tối.
3. Chuyển sang tông sáng, bỏ chữ dư và thống nhất palette theo phản hồi.
4. Tách tổng quan/chi tiết, giữ lại tên Dashboard nhất quán.
5. Bỏ route group, đổi /heatmap và PascalCase component theo sườn được thống nhất.

Các bước trên giải thích thiết kế cuối; không phải tất cả phương án đều còn tồn tại
trong code. Chi tiết trạng thái hiện tại xem [kiến trúc](../architecture.md).

## 6. Kiểm chứng

Lệnh: npm run lint, npm run typecheck, npm run format:check, npm test, npm run build.
Kết quả local của sườn mới: 24 kiểm thử offline qua; lint, typecheck, format và
production build được kiểm tra trước bàn giao. Từng snapshot commit được kiểm tra
trước khi tạo commit để tránh phụ thuộc vào file của commit sau.

Cần phân biệt: workflow CI được cấu hình trong repo; chưa khẳng định CI trên GitHub
đã pass vì nhánh chưa được push. Kiểm tra trình duyệt ghi nhận URL /heatmap,
redirect URL cũ, chọn kỳ và menu mobile ở bản cuối.

## 7. Giới hạn và công việc tiếp theo

- Mọi dữ liệu analytics/quota là mẫu, chưa có rule evaluation thực tế.
- Audit Logs chưa nối backend; summary là template xác định, chưa có LLM.
- Chưa có auth, token hoặc API contract.
- npm audit còn advisory ở Next.js 14/tooling; cần đánh giá nâng version trước deploy.
- Khi có nhiều repository mới thêm bộ chọn repo; hiện chỉ hiển thị repo mẫu, tránh
  tạo dropdown chỉ có một lựa chọn và không làm gì.
- Khi tích hợp backend cần thống nhất định nghĩa chỉ số, phân trang, lỗi và refresh.

## 8. Tham chiếu

- Task #8: Initialize Next.js 14 App Router, Tailwind CSS, and Dashboard Layout.
- .ai/AGENTS.md và PRIVACY.md của repository.
- [Grafana GitHub](https://grafana.com/docs/plugins/grafana-github-datasource/latest/).
- [Grafana dashboard guidance](https://grafana.com/docs/grafana/latest/visualizations/dashboards/build-dashboards/best-practices/).
- [GitHub Pulse](https://docs.github.com/en/repositories/viewing-activity-and-data-for-your-repository/using-pulse-to-view-a-summary-of-repository-activity).

## 9. Các commit để review

| Commit                                                     | Nội dung review                                                      |
| ---------------------------------------------------------- | -------------------------------------------------------------------- |
| `39a3c17`                                                  | Khởi tạo Next.js 14, cấu hình và công cụ phát triển                  |
| `0d39219`                                                  | Route phẳng, AppShell/Header/PageHeader, quota/helper và 13 kiểm thử |
| `1f57df3`                                                  | Dashboard analytics, bộ lọc, trang chi tiết; tổng 24 kiểm thử        |
| `38f6c4b`                                                  | Job CI riêng cho frontend                                            |
| `docs(frontend): record architecture and task 8 decisions` | Tài liệu hiện tại và lý do thay đổi                                  |

Snapshot khởi tạo qua format/build; snapshot shell qua format/13 tests/build;
snapshot analytics qua format/24 tests/build. Các commit CI/tài liệu không thay đổi
runtime. Lịch sử trước khi làm sạch được giữ trên nhánh backup đã nêu ở D7.
