# GitHub Project Coach Frontend

Frontend dashboard xây dựng trên nền tảng Next.js 14 App Router, TypeScript, Tailwind CSS 3 và Lucide Icons.

## Yêu cầu môi trường

- **Node.js**: Phiên bản 20 hoặc 22 LTS
- **Package Manager**: `npm` (dùng lockfile `package-lock.json` đi kèm)

## Cài đặt và cấu hình

1. Cài đặt dependencies:

   ```sh
   npm ci
   ```

2. Cấu hình biến môi trường (tùy chọn trong môi trường phát triển):
   - Mặc định ứng dụng kết nối tới backend tại `http://localhost:8000` thông qua cấu hình tập trung tại `src/shared/config/env.ts`.
   - Có thể chỉ định backend URL qua biến môi trường:
     ```sh
     NEXT_PUBLIC_API_URL=http://localhost:8000
     ```

## Khởi chạy ứng dụng

- Chạy chế độ phát triển (development):

  ```sh
  npm run dev
  ```

  Truy cập giao diện tại: [http://localhost:3000](http://localhost:3000).

- Build và chạy production:
  ```sh
  npm run build
  npm start
  ```

## Kiểm tra chất lượng mã nguồn (Checks)

Tất cả các kiểm tra đều chạy ngoại tuyến (offline) và sử dụng fixtures từ `../backend/tests/mocks/`:

```sh
npm run lint          # Next.js ESLint
npm run typecheck     # TypeScript strict type checking
npm run format:check  # Prettier code formatting check
npm test              # Vitest test suite (offline unit & integration tests)
npm run build         # Next.js production build verification
```

Để tự động sửa định dạng code theo chuẩn Prettier:

```sh
npm run format
```

## Các Routes hỗ trợ

- `/`: Dashboard tổng quan, các chỉ số cộng tác, xu hướng hoạt động và cảnh báo ngắn.
- `/heatmap`: Ma trận hoạt động chi tiết theo ngày và loại sự kiện.
- `/stale-alerts`: Danh sách pull requests tồn đọng kèm rule và bằng chứng cụ thể.
- `/audit-logs`: Màn hình nhật ký truy cập và xử lý metadata.
- `/collaboration-heatmap`: Tự động chuyển hướng vĩnh viễn (308 permanent redirect) sang `/heatmap`.

## Tài liệu liên quan

Tài liệu chi tiết được lưu trữ tập trung tại thư mục `/docs` ở root monorepo:

- [Kiến trúc Frontend](../docs/frontend/architecture.md): Cấu trúc thư mục Feature-based, ranh giới Server/Client Components, luồng dữ liệu và quy ước phát triển.
- [Bản ghi Task #8 Refactor](../docs/tasks/08-frontend-refactor.md): Bối cảnh, các quyết định kiến trúc, kết quả kiểm chứng và giới hạn kỹ thuật.
- [Mục lục tài liệu dự án](../docs/README.md): Toàn bộ tài liệu kiến trúc, ADR và hợp đồng kỹ thuật monorepo.
