"""Generate the Vietnamese VT-024 assignment report and evidence appendices."""

from __future__ import annotations

import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    KeepTogether,
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = ROOT / "backend" / "tests" / "evidence"
OUTPUT = ROOT / "output" / "pdf" / "BT3_23001819_VT-024.pdf"
FONT_DIR = Path("C:/Windows/Fonts")
NAVY = colors.HexColor("#18324B")
TEAL = colors.HexColor("#0B7776")
PALE = colors.HexColor("#EAF2F5")
INK = colors.HexColor("#1E2933")
MUTED = colors.HexColor("#526473")
GRID = colors.HexColor("#C9D5DC")

pdfmetrics.registerFont(TTFont("Segoe", str(FONT_DIR / "segoeui.ttf")))
pdfmetrics.registerFont(TTFont("Segoe-Bold", str(FONT_DIR / "segoeuib.ttf")))
pdfmetrics.registerFont(TTFont("Segoe-Italic", str(FONT_DIR / "segoeuii.ttf")))
pdfmetrics.registerFontFamily(
    "Segoe", normal="Segoe", bold="Segoe-Bold", italic="Segoe-Italic", boldItalic="Segoe-Bold"
)

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="TitleVN", fontName="Segoe-Bold", fontSize=21, leading=25, textColor=NAVY, spaceAfter=5 * mm))
styles.add(ParagraphStyle(name="SubTitleVN", fontName="Segoe", fontSize=10, leading=14, textColor=MUTED, spaceAfter=4 * mm))
styles.add(ParagraphStyle(name="H1VN", fontName="Segoe-Bold", fontSize=15, leading=18, textColor=NAVY, spaceAfter=3 * mm, keepWithNext=True))
styles.add(ParagraphStyle(name="H2VN", fontName="Segoe-Bold", fontSize=9.5, leading=12, textColor=TEAL, spaceBefore=2 * mm, spaceAfter=1.3 * mm, keepWithNext=True))
styles.add(ParagraphStyle(name="BodyVN", fontName="Segoe", fontSize=8.6, leading=11.5, textColor=INK, spaceAfter=2 * mm))
styles.add(ParagraphStyle(name="SmallVN", fontName="Segoe", fontSize=7.5, leading=9.3, textColor=INK, spaceAfter=1 * mm))
styles.add(ParagraphStyle(name="TinyVN", fontName="Segoe", fontSize=6.8, leading=8.1, textColor=INK))
styles.add(ParagraphStyle(name="CellVN", fontName="Segoe", fontSize=7.0, leading=8.3, textColor=INK))
styles.add(ParagraphStyle(name="CaseCellVN", fontName="Segoe", fontSize=6.1, leading=7.3, textColor=INK))
styles.add(ParagraphStyle(name="CellHeadVN", fontName="Segoe-Bold", fontSize=7.0, leading=8.3, textColor=colors.white))
styles.add(ParagraphStyle(name="QuoteVN", fontName="Segoe-Bold", fontSize=10.3, leading=14, textColor=NAVY, alignment=TA_CENTER))
styles.add(ParagraphStyle(name="AppendixVN", fontName="Segoe-Bold", fontSize=12, leading=15, textColor=NAVY, spaceAfter=3 * mm))
styles.add(ParagraphStyle(name="CodeVN", fontName="Courier", fontSize=6.6, leading=8.0, textColor=INK))


def p(text: str, style: str = "BodyVN") -> Paragraph:
    return Paragraph(text, styles[style])


def section(title: str, body: str) -> list:
    return [KeepTogether([p(title, "H2VN"), p(body)])]


def table(rows: list[list[str]], widths: list[float], header: bool = True, font: str = "CellVN") -> KeepTogether:
    converted = []
    for ridx, row in enumerate(rows):
        converted.append([p(cell, "CellHeadVN" if header and ridx == 0 else font) for cell in row])
    t = Table(converted, colWidths=widths, repeatRows=1 if header else 0, hAlign="LEFT")
    cmds = [
        ("GRID", (0, 0), (-1, -1), 0.35, GRID),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]
    if header:
        cmds += [("BACKGROUND", (0, 0), (-1, 0), NAVY), ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PALE])]
    t.setStyle(TableStyle(cmds))
    return KeepTogether([t])


def page_header(canvas, doc) -> None:
    canvas.saveState()
    page = canvas.getPageNumber()
    canvas.setStrokeColor(GRID)
    canvas.setLineWidth(0.5)
    canvas.line(18 * mm, 14 * mm, 192 * mm, 14 * mm)
    canvas.setFont("Segoe", 7)
    canvas.setFillColor(MUTED)
    canvas.drawString(18 * mm, 9 * mm, "AI-03  |  VT-024  |  Hoàng Khánh An")
    canvas.drawRightString(192 * mm, 9 * mm, f"Trang {page}")
    if page > 1:
        canvas.setFont("Segoe-Bold", 7)
        canvas.setFillColor(TEAL)
        canvas.drawString(18 * mm, 286 * mm, "BT CÁ NHÂN 3  /  BÁO CÁO KỸ THUẬT")
    canvas.restoreState()


def main_pages() -> list:
    story = []

    # Page 1
    story += [p("BT CÁ NHÂN 3 · AI-03", "SubTitleVN"), p("VT-024 | Bounded retry cho GitHub API", "TitleVN")]
    story += [p("GitHub Project Coach · Báo cáo kiểm thử và đánh giá kỹ thuật", "SubTitleVN")]
    identity = [
        ["Thông tin", "Giá trị"],
        ["Họ tên / MSSV", "Hoàng Khánh An / 23001819"],
        ["Team / mã đề tài", "SE2026-T07 / AI-03"],
        ["Repository", "<link href='https://github.com/duyendojhs/SE2026-15-1' color='#0B7776'>duyendojhs/SE2026-15-1</link> (đề bài); repo dự án: <link href='https://github.com/duyendojhs/SE2026-T07' color='#0B7776'>SE2026-T07</link>"],
        ["Nhánh / PR", "bt3-23001819-vt024-retry · PR #15 (draft)"],
        ["Baseline", "90f831c8c8afc84dd4f0268b7ed5704e41f32cbf"],
    ]
    story += [table(identity, [34 * mm, 140 * mm]), Spacer(1, 3 * mm)]
    declaration = Table([[p("“Tôi chịu trách nhiệm về toàn bộ code, test và nội dung bài làm; tôi đã khai báo việc sử dụng AI.”", "QuoteVN")]], colWidths=[174 * mm])
    declaration.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), PALE), ("BOX", (0, 0), (-1, -1), 0.8, TEAL), ("LEFTPADDING", (0, 0), (-1, -1), 9), ("RIGHTPADDING", (0, 0), (-1, -1), 9), ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 8)]))
    story += [declaration]
    story += section("Bối cảnh và yêu cầu cá nhân hóa", "GitHub Project Coach đồng bộ issue, pull request, review và metadata vào backend. VT-024 yêu cầu GitHubClient chịu được lỗi tạm thời trong các lần đọc an toàn, trong khi giới hạn số lần thử và giữ nguyên lỗi khi cạn lượt. Điểm thay đổi được chọn là tầng HTTP client; yêu cầu không bao gồm retry toàn bộ backfill.")
    story += section("Vấn đề và rủi ro chính", "Nếu GET bị timeout hoặc mất kết nối nhất thời, yêu cầu đọc có thể thất bại dù lần gọi tiếp theo thành công. Ngược lại, retry POST/PUT/PATCH/DELETE có thể lặp side effect. Backfill còn ghi RawEvent và AuditLog theo kiểu append; uniqueness của business rows không chứng minh các bản ghi phụ có exactly-once semantics. Vì vậy phạm vi retry phải hẹp, có giới hạn và không biến lỗi persistence thành kết quả thành công.")
    story += [p("Kết quả cuối: thay đổi production giới hạn ở GitHubClient; kiểm thử cuối 49 passed; branch đã được đẩy lên remote.", "SmallVN")]

    # Page 2
    story += [p("02  /  ĐẶC TẢ VÀ BẤT BIẾN", "H1VN")]
    ac_rows = [
        ["Tiêu chí", "Hành vi được xác nhận"],
        ["AC-01 · retry tạm thời", "GET retry khi gặp 5xx, timeout hoặc ConnectError; dùng giới hạn và backoff hiện có."],
        ["AC-02 · không retry sai", "401/404 không retry; request không an toàn không retry sau status/transport failure; hết lượt phải báo lỗi."],
        ["AC-03 · ingest ổn định", "Re-ingestion giữ duy nhất business rows theo các khóa/upsert hiện có; không khẳng định exactly-once cho raw/audit append."],
        ["AC-04 · persistence", "Lỗi commit không được trả về BackfillResult thành công; API cũng không được trả success giả."],
        ["AC-05 · partial failure", "Khi một nguồn lỗi nhưng nguồn khác thành công, trạng thái partial và dữ liệu hợp lệ được giữ."],
    ]
    story += [table(ac_rows, [34 * mm, 140 * mm])]
    story += section("Bất biến kỹ thuật", "Số lần gọi ≤ max_retries + 1; max_retries=0 nghĩa là đúng một lần thử. Kết quả thành công chỉ trả sau phản hồi thành công. Khi cạn lượt, transport exception hoặc GitHubAPIError phù hợp được truyền ra. Endpoint allowlist và auth header tiếp tục được áp dụng.")
    story += section("Yêu cầu phi chức năng và ràng buộc", "Mục tiêu kiểm thử hiệu năng: 100 concurrent users/tasks và p95 latency ≤ 3.0 giây. Kiểm thử tự động phải offline và deterministic. Privacy policy chỉ lưu metadata, không lưu nội dung issue/comment nhạy cảm. Retry phải bounded và không tạo side effects trùng ngoài ý muốn. Bản vá retry GET cho ConnectError/TimeoutException, không thêm dependency runtime, giữ backoff hiện hữu, không retry unsafe methods và không mở rộng sang BackfillService. Benchmark mock ở trang 7 không chứng minh production đạt p95 ≤ 3.0 giây.")
    story += section("Định nghĩa failure rõ ràng", "Lỗi kết nối/timeout sau lượt cuối không bị đổi thành success hoặc che giấu. HTTP 401/404 giữ nguyên xử lý không retry. 403/429/5xx cho GET giữ xử lý hiện hành; với non-GET, giới hạn retry không được làm thay đổi kiểu exception hiện hữu.")

    # Page 3
    story += [KeepTogether([p("03  /  KẾ HOẠCH AI VÀ REVIEW CỦA CON NGƯỜI", "H1VN"), *section("Kế hoạch triển khai ban đầu", "1) Kiểm tra hợp đồng GitHubClient, allowlist, backoff và trạng thái backfill. 2) Viết test trước cho timeout, ConnectError, retry bound, unsafe POST và persistence failure. 3) Quan sát RED và giữ log nguyên gốc. 4) Chỉ sửa request loop trong backend/app/github/client.py. 5) Chạy GREEN, hồi quy, lint rồi đánh giá mutation, coverage và harness mock. 6) Ghi AI Usage Log và traceability trước khi đóng gói báo cáo.")])]
    story += section("Quyết định review 1 — không retry toàn workflow", "Không bọc BackfillService.run() bằng retry. Kiểm tra models.py xác nhận uniqueness/upsert cho business rows, nhưng RawEvent và AuditLog được append trong cùng unit of work và không có khóa idempotency tương ứng. Chạy lại workflow có thể nhân bản log phụ. Tầng GET là nơi an toàn hơn cho retry trong vertical slice.")
    story += section("Quyết định review 2 — Hypothesis là phần bắt buộc", "Property test không bị bỏ qua sau khi example-based test pass. Oracle ban đầu đòi GitHubAPIError sau transport exhaustion; kiểm tra client hiện hữu cho thấy httpx transport exception được truyền nguyên trạng và không có contract yêu cầu chuyển kiểu. Oracle được sửa sang httpx.TransportError, nhưng vẫn giữ bounded attempts và yêu cầu không trả success khi cạn lượt.")
    story += section("Quyết định review 3 — giữ bằng chứng RED", "Log RED gốc và test-only commit được giữ nguyên. Bốn test thất bại chính xác: test_read_timeout_is_retried_then_succeeds, test_connection_error_is_retried_then_succeeds, test_transient_http_error_on_post_is_not_retried, test_timeout_retry_is_bounded_and_returns_only_after_success. Persistence characterization test_commit_failure_never_returns_success_and_recovery_is_consistent đã PASS trên baseline. API regression ban đầu kỳ vọng JSON 500; phản hồi thực tế của Starlette là plain text nên chỉ assertion được chỉnh theo response quan sát được.")
    story += section("Rủi ro thiếu ngữ cảnh đã điều tra", "Sau khi được phép kiểm tra model/audit code, xác nhận business rows có uniqueness nhưng raw events/audit records không có cùng bảo đảm. Rủi ro còn lại: manual full backfill có thể append thêm log; chưa có test count cho side effect này. Nhật ký AI ghi lại giả định, quyết định review, và giới hạn.")

    # Page 4
    tests = [
        ["ID", "Requirement / Risk", "Test Level", "Precondition / Input", "Expected Result", "Priority"],
        ["T01<br/><font size='5.4'>test_rate_limit_retry_after_is_respected</font>", "AC-01<br/>Retry-After", "Unit", "GET 403 + Retry-After", "Sleep delay follows header", "P2"],
        ["T02<br/><font size='5.4'>test_rate_limit_exhaustion_raises</font>", "AC-02<br/>Bound/exhaustion", "Unit", "GET receives repeated 403", "Raise GitHubAPIError at bound", "P1"],
        ["T03<br/><font size='5.4'>test_bad_token_is_not_retried</font>", "AC-02<br/>Auth", "Unit", "GET returns 401", "One attempt; propagate error", "P1"],
        ["T04<br/><font size='5.4'>test_content_endpoint_is_blocked_before_network</font>", "Allowlist", "Unit", "Endpoint outside allowlist", "Reject before network", "P1"],
        ["T05<br/><font size='5.4'>test_pagination_follows_link_header</font>", "Pagination", "Unit", "Response includes Link header", "Follow next page", "P2"],
        ["T06<br/><font size='5.4'>test_http_500_is_retried_then_succeeds</font>", "AC-01<br/>Server error", "Unit", "GET 500 then 200", "Retry and return success", "P1"],
        ["T07<br/><font size='5.4'>test_read_timeout_is_retried_then_succeeds</font>", "AC-01<br/>Timeout", "Unit", "GET ReadTimeout then 200", "Retry and return success", "P1"],
        ["T08<br/><font size='5.4'>test_connection_error_is_retried_then_succeeds</font>", "AC-01<br/>ConnectError", "Unit", "GET ConnectError then 200", "Retry and return success", "P1"],
        ["T09<br/><font size='5.4'>test_transient_http_error_on_post_is_not_retried</font>", "AC-02<br/>Unsafe method", "Unit", "POST receives 500", "One request; propagate error", "P1"],
        ["T10<br/><font size='5.4'>test_timeout_retry_is_bounded_and_returns_only_after_success</font>", "AC-02<br/>Retry bound", "Property", "max_retries 0–5; transient sequence", "≤ retries+1; exhaustion raises", "P1"],
        ["T11<br/><font size='5.4'>test_backfill_is_idempotent_and_metadata_only</font>", "AC-03<br/>Re-ingestion", "Integration", "Repeat same backfill", "Business-row counts stable", "P1"],
        ["T12<br/><font size='5.4'>test_backfill_marks_partial_when_one_resource_fails</font>", "AC-05<br/>Partial failure", "Integration", "One resource fails; others succeed", "Partial status; keep successful data", "P1"],
        ["T13<br/><font size='5.4'>test_generated_duplicate_issue_ids_remain_unique_after_reordered_reingestion</font>", "AC-03<br/>Duplicate IDs", "Property", "Duplicate IDs in changed order", "Issue rows remain unique", "P1"],
        ["T14<br/><font size='5.4'>test_commit_failure_never_returns_success_and_recovery_is_consistent</font>", "AC-04<br/>Persistence", "Integration", "Inject commit failure; then recover", "No false success; rollback/recovery", "P1"],
    ]
    story += [KeepTogether([p("04  /  CHIẾN LƯỢC KIỂM THỬ THEO RỦI RO", "H1VN"), p("T01–T14 là documentation IDs của báo cáo, không đổi tên Python test function hiện có.", "SmallVN"), table(tests, [36 * mm, 26 * mm, 15 * mm, 42 * mm, 42 * mm, 13 * mm], font="CaseCellVN")])]
    story += section("Mức kiểm thử và oracle", "MockTransport cho HTTP/unit; SQLite in-memory cho backfill/integration; TestClient cho API persistence regression sau đó; không chạy E2E với GitHub thật. Retry property sinh max_retries 0–5 và chuỗi timeout/connection. Oracle đếm lần gọi, xác nhận ≤ max_retries+1 và yêu cầu exception khi không còn lượt. Invariant idempotency kiểm tra business rows sau ID trùng và reordering.")
    story += [p("Hypothesis thực thi: retry 40 pass, 2 invalid, 0 fail; idempotency 30 pass, 4 invalid, 0 fail. Không có minimized failing counterexample. Nguyên nhân chi tiết của invalid examples không được log.", "SmallVN")]

    # Page 5
    story += [p("05  /  TEST-FIRST: RED → PATCH → GREEN", "H1VN")]
    phases = [
        ["Mốc", "Commit", "Bằng chứng"],
        ["Baseline", "90f831c8c8afc84dd4f0268b7ed5704e41f32cbf", "Điểm bắt đầu; client chưa retry timeout/connection."],
        ["RED · test-only", "11055810f10729963a8706b22fec2fcf5d9b0647", "4 test fail: ReadTimeout, ConnectError, POST 500 retry, bounded retry. Persistence characterization đã pass baseline."],
        ["PATCH · GREEN", "ecd22676f6a1ce43bcfa0d21852f717d475c130d", "Production chỉ backend/app/github/client.py; oracle dùng TransportError."],
        ["Quality evidence", "e4e56c86b9dab3e3c2fbaf36b751f29e4b135a", "Mutation, coverage, API regression, lint/perf evidence."],
        ["Perf refinement", "5f1fcbb719a8efad847e58bca03dce406566bfae", "Barrier 100 workers; latency tính cả outcome lỗi."],
        ["Traceability", "4982995c17d42999908780b3aec1af6aa4c7cd05", "Ma trận test/AC, tên test thật và SHA."],
        ["Final verification", "99ca2d46841be8a164224c9ac7597961fa61b58f", "49 passed; Ruff pass; clean branch trước hồ sơ."],
    ]
    story += [table(phases, [29 * mm, 70 * mm, 75 * mm])]
    story += section("Bản vá tối thiểu", "Request loop retry ConnectError và TimeoutException cho GET nếu còn lượt; chờ theo exponential backoff hiện hữu. Hết lượt thì raise exception gốc. Các response 403/429/5xx tiếp tục theo logic cũ; non-GET không nhận retry status/transport. Không thay đổi BackfillService, allowlist, token provider hay dependency production.")
    story += section("GREEN và hồi quy", "Checkpoint 3: 14/14 test retry/backfill. Checkpoint 4: 48/48 toàn backend. Sau API persistence regression: 49/49 cuối cùng (một warning deprecation). Ruff: All checks passed. Thứ tự ba file test được đảo hai lần, mỗi lần 15/15 pass. Mypy không chạy được vì module không tồn tại trong .venv.")
    story += section("Vì sao GitHubClient đủ cho lát cắt", "Lỗi phát sinh trước khi có dữ liệu trả về từ GitHub; retry đúng một GET trong client giữ nguyên ranh giới và phép đo số lần gọi. Backfill không cần biết transport retry, và lỗi commit vẫn được kiểm tra riêng ở service/API. Phạm vi hẹp tránh nhân đôi side effects của workflow.")

    # Page 6
    story += [p("06  /  MUTATION VÀ COVERAGE", "H1VN")]
    story += section("Mutation thử nghiệm", "Tạo mutant tạm thời bắt lỗi session.commit() trong BackfillService.run() rồi trả BackfillResult giả ở trạng thái ready. Chạy test_commit_failure_never_returns_success_and_recovery_is_consistent cho kết quả DID NOT RAISE SQLAlchemyError: test thất bại đúng kỳ vọng và mutant bị giết. Diff mutant và output được giữ trong evidence. Kiểm tra sau đó: backfill.py không có diff so với baseline; không có mutation trong source branch.")
    cov = [
        ["Module / phạm vi", "Statement", "Branch", "Combined Cover"],
        ["app/github/client.py", "95/121 · 78.51%", "31/50 · 62.00%", "73.68% (74%)"],
        ["app/ingestion/backfill.py", "151/163 · 92.64%", "35/40 · 87.50%", "91.63% (92%)"],
        ["Tổng hai module", "246/284 · 86.62%", "66/90 · 73.33%", "83.42% (83%)"],
    ]
    story += [table(cov, [52 * mm, 40 * mm, 40 * mm, 42 * mm])]
    story += [p("Coverage command giới hạn source ở hai module production và chạy 15 test retry/backfill/API. Cột Combined là số coverage.py gộp statement và branch; không được gọi là line coverage. Đây không phải coverage toàn repository.", "SmallVN")]
    story += section("Rủi ro được bao phủ", "AC-01: 5xx, timeout, ConnectError và bound có test trực tiếp. AC-02: 401, POST/500, 403 exhaustion và transport exhaustion; chưa có test riêng 404, generic 4xx hay POST transport. AC-03: business rows được kiểm tra; raw/audit count không được assert. AC-04: service, API và mutant đều kiểm tra false success. AC-05: partial một nguồn lỗi được kiểm tra; all-fail path chưa có test riêng.")
    story += section("Branch còn thiếu có giá trị rủi ro", "Client: rate-reset wait, Retry-After thiếu/sai, generic 4xx, 304, pagination malformed. Backfill: all-resources-failed, issue cũng là PR, cutoff PR cũ, review thiếu PR. Coverage mô tả phần chưa chạy; tỷ lệ cao không thay thế assertion theo rủi ro.")

    # Page 7
    story += [p("07  /  ĐỘ ỔN ĐỊNH VÀ HIỆU NĂNG", "H1VN")]
    story += section("Điều tra rủi ro flaky đã thực thi", "Time/backoff: test dùng sleep callback giả ghi nhận delay, không đợi thật; jitter fallback không bị assert. Hypothesis: bật deterministic seed behavior (derandomize=True), không dùng example database; retry 40 pass/2 invalid, ingest 30 pass/4 invalid. Test order: hai thứ tự file khác nhau đều 15 pass; SQLite in-memory theo fixture và API listener/override được dọn trong finally. Concurrency: harness có 100 worker, mỗi task sở hữu client/transport/counter riêng; không gọi GitHub thật.")
    perf = [
        ["Thước đo mock", "Kết quả"],
        ["Task / worker", "100 / 100; barrier chặn trước khi đo tới khi đủ worker"],
        ["Scenario", "90 success ngay; 5 transient rồi success; 5 exhausted có chủ ý"],
        ["Request / outcome", "115 request = 90×1 + 5×2 + 5×3; 95 success, 5 fail dự kiến"],
        ["Latency trên 100 task", "p50 0.376 ms · p95 0.701 ms · max 1.131 ms"],
        ["Đo lường", "perf_counter mỗi task; p95 nearest-rank trên cả 100 outcome, kể cả lỗi"],
    ]
    story += [table(perf, [43 * mm, 131 * mm])]
    story += section("Diễn giải đúng phạm vi", "100 worker rendezvous tại Barrier trước timed interval, nên tác vụ được thả đồng thời; thời gian barrier không tính latency. Handler MockTransport không blocking. Sleep/backoff là no-op: latency đo request/retry logic và callback, nhưng loại trừ thời gian chờ backoff thật. Năm lỗi exhausted được tiêm có chủ ý; 115 request khớp với cấu hình max_retries=2.")
    story += section("Giới hạn", "Đây là benchmark trong process với mock. Nó không đánh giá p95 production, độ trễ GitHub thật, database throughput, API concurrency end-to-end hay chứng minh ngưỡng production p95 ≤ 3 giây. Không có timing assertion trong pytest. Đây chỉ là bằng chứng rằng harness hoạt động theo các chuỗi retry đã định.")

    # Page 8
    trace = [
        ["AC / rủi ro · case IDs", "Test function(s)", "File · commit", "Kết quả"],
        ["AC-01/02 · T01, T02, T06", "test_rate_limit_retry_after_is_respected; test_rate_limit_exhaustion_raises; test_http_500_is_retried_then_succeeds", "test_rate_limit.py · 1105581", "Pass; GET retry/exhaustion"],
        ["AC-02 · T03, T04, T05", "test_bad_token_is_not_retried; test_content_endpoint_is_blocked_before_network; test_pagination_follows_link_header", "test_rate_limit.py · 1105581", "Pass; 401, allowlist, pagination"],
        ["AC-01/02 · T07–T10", "test_read_timeout_is_retried_then_succeeds; test_connection_error_is_retried_then_succeeds; test_transient_http_error_on_post_is_not_retried; test_timeout_retry_is_bounded_and_returns_only_after_success", "test_rate_limit.py · 1105581 / ecd2267", "Pass; property 40 pass, 2 invalid"],
        ["AC-03/05 · T11–T13", "test_backfill_is_idempotent_and_metadata_only; test_backfill_marks_partial_when_one_resource_fails; test_generated_duplicate_issue_ids_remain_unique_after_reordered_reingestion", "test_backfill.py · 7c13113 / 1105581", "Pass; property 30 pass, 4 invalid"],
        ["AC-04 · T14", "test_commit_failure_never_returns_success_and_recovery_is_consistent", "test_backfill.py · 1105581", "Pass; mutant killed"],
        ["API regression · ngoài T01–T14", "test_sync_api_does_not_return_success_when_persistence_fails", "test_tenants_sync_api.py · e4e56c8", "Pass; API 500"],
        ["Performance experiment", "main / _run_task", "perf_retry_harness.py · e4e56c8 / 5f1fcbb", "100 task mock; p95 0.701 ms"],
    ]
    story += [KeepTogether([p("08  /  TRACEABILITY, BẰNG CHỨNG VÀ PHẢN TƯ", "H1VN"), table(trace, [34 * mm, 79 * mm, 36 * mm, 25 * mm])])]
    story += [p("T01–T14 là documentation IDs, ánh xạ từng test function tại trang 4; tên Python test không đổi. API persistence regression được thêm sau đó và nằm ngoài bộ 14 case. Commit đầy đủ, commands, mutation experiment và kết quả nằm trong evidence appendix. Hai giả định AI đã sửa: ép transport exhaustion thành GitHubAPIError (oracle sửa về httpx.TransportError); kỳ vọng response 500 JSON (assert plain text thực tế). Tóm tắt perf sai 85/10/5 được sửa thành 90/5/5 theo phép đếm request.", "SmallVN")]
    reflection = (
        "Độ tin cậy tăng lên nhờ ba loại bằng chứng bổ sung nhau: test-first làm lộ lỗi trước khi vá, kiểm tra bounded retry xác nhận giới hạn lời gọi, còn mutation thử xem test có thật sự phát hiện false success khi commit thất bại hay không. Mutant bị test persistence giết bằng lỗi DID NOT RAISE SQLAlchemyError; đây là bằng chứng mạnh hơn việc chỉ thấy test pass trên implementation đúng. Chạy lại toàn backend được 49 pass và Ruff pass, đồng thời đổi thứ tự các file test hai lần vẫn 15/15, giúp giảm lo ngại về state dùng chung.\n\n"
        "Một số điều vẫn chưa được chứng minh: nhánh 404/generic 4xx và vài nhánh pagination chưa có test trực tiếp; raw event và audit append có thể tăng khi chạy lại workflow; Hypothesis ghi nhận invalid examples nhưng không ghi rõ dữ liệu gây ra; coverage giới hạn ở hai module; benchmark dùng mock và bỏ thời gian backoff thật. Vì vậy p95 0.701 ms không đại diện cho production.\n\n"
        "Mutation testing đánh giá sức mạnh assertion bằng cách đưa một lỗi có chủ đích vào đường commit rồi xác nhận test bắt được kết quả thành công giả. Bước kế tiếp có giá trị nhất là kiểm thử integration với database cho raw-event/audit semantics khi re-run, rồi bổ sung test cho 404 và POST transport failure. Nếu có môi trường staging, đo network/API latency riêng sẽ trả lời câu hỏi hiệu năng thực tế tốt hơn harness hiện tại.\n\n"
        "AI giúp tạo khung test và tổng hợp dữ liệu nhanh, nhưng các giả định phải được đối chiếu với code và output thật. Tôi chịu trách nhiệm chọn phạm vi, sửa oracle, giữ nguyên RED evidence, kiểm tra mutation đã gỡ, và công bố những điều chưa biết. AI hỗ trợ thao tác; kết luận kỹ thuật và nội dung nộp bài vẫn cần con người xác nhận."
    )
    reflection_words = len(re.findall(r"\S+", reflection))
    if not 250 <= reflection_words <= 350:
        raise ValueError(f"Reflection has {reflection_words} whitespace-delimited words; expected 250-350")
    story += [KeepTogether([p("PHẢN TƯ", "H2VN"), p(reflection.replace("\n\n", "<br/><br/>"), "SmallVN"), Spacer(1, 1 * mm), p(f"Số từ phản tư (tách theo khoảng trắng): {reflection_words}.", "TinyVN")]), PageBreak()]
    return story, reflection_words


def repo_link(path: str, label: str | None = None) -> str:
    href = f"https://github.com/duyendojhs/SE2026-T07/blob/bt3-23001819-vt024-retry/{path}"
    return f"<link href='{href}' color='#0B7776'>{label or path}</link>"


def appendix_pages() -> list:
    story = [
        p("PHỤ LỤC A · NHẬT KÝ AI TÓM TẮT", "H1VN"),
        p("Bản tóm tắt ghi lại yêu cầu, đóng góp AI, quyết định của người review và vị trí bằng chứng. Nhật ký gốc không bị sửa.", "SmallVN"),
    ]
    usage_rows = [
        ["Giai đoạn / prompt chính", "Đầu ra AI và quyết định review của con người", "Bằng chứng gốc"],
        ["Kế hoạch và RED", "Yêu cầu: kiểm tra hợp đồng client, viết test trước, giới hạn retry ở GET an toàn. AI đề xuất lát cắt nhỏ; reviewer yêu cầu giữ RED nguyên. Bốn test retry thất bại; characterization persistence đã pass baseline.", repo_link("backend/tests/evidence/vt024-red.txt")],
        ["Oracle Hypothesis", "Đề xuất ban đầu đòi GitHubAPIError sau exhaustion. Reviewer đối chiếu public behavior: httpx transport exception được truyền nguyên. Oracle sửa sang TransportError, vẫn giữ giới hạn số lần thử và yêu cầu không trả success.", repo_link("backend/tests/evidence/vt024-ai-usage-log.md", "AI Usage Log đầy đủ")],
        ["Bản vá và GREEN", "Human approval: chỉ sửa GitHubClient, retry ConnectError/TimeoutException cho GET và giữ backoff hiện hữu; không retry workflow hay unsafe methods. Targeted suite 14 pass; full suite cuối 49 pass; Ruff pass.", repo_link("backend/tests/evidence/vt024-green.txt")],
        ["Mutation, coverage, perf", "Reviewer duyệt coverage.py như dev dependency và yêu cầu tách statement/branch. Test persistence giết mutant false-success. AI tóm tắt perf sai 85/10/5; phép tính nguồn được sửa thành 90/5/5.", repo_link("backend/tests/evidence/vt024-phase4-context.txt")],
        ["Giả định AI bị sửa", "Hai ví dụ: (1) đòi exception type GitHubAPIError không đúng contract; (2) kỳ vọng body lỗi API là JSON nhưng Starlette trả plain text. Cả hai được kiểm tra với code/output thật. Không tuyên bố mypy pass vì thiếu package.", repo_link("backend/tests/evidence/vt024-traceability.md", "Traceability và commit")],
    ]
    story += [table(usage_rows, [36 * mm, 99 * mm, 39 * mm], font="CaseCellVN"), Spacer(1, 2 * mm)]
    story += [p("Human checkpoints: duyệt patch tối thiểu (3A/3B), GREEN (4), mutation/coverage/performance (5), source-integrity review (6), hiệu chỉnh báo cáo (7B), và gửi Draft PR #15. Không có thay đổi log gốc trong lần rút gọn này.", "SmallVN")]
    story += [
        p("PHỤ LỤC B · RED, GREEN VÀ MUTATION", "H1VN"),
        p("Chỉ trích kết quả và thông báo lỗi liên quan; toàn bộ terminal logs cùng traceback vẫn được giữ trong repository.", "SmallVN"),
    ]
    red_rows = [
        ["RED test thất bại", "Thông báo / kết quả quan sát"],
        ["test_read_timeout_is_retried_then_succeeds", "httpx.ReadTimeout: temporary timeout"],
        ["test_connection_error_is_retried_then_succeeds", "httpx.ConnectError: temporary connection error"],
        ["test_transient_http_error_on_post_is_not_retried", "AssertionError: POST bị gửi quá một lần"],
        ["test_timeout_retry_is_bounded_and_returns_only_after_success", "Property fail khi exhaustion truyền httpx transport exception; oracle sau đó được sửa đúng contract."],
    ]
    story += [table(red_rows, [80 * mm, 94 * mm], font="CaseCellVN")]
    story += [p("Phân biệt baseline: test_commit_failure_never_returns_success_and_recovery_is_consistent đã PASS trước patch. Trong mutation experiment, chính test này giết mutant: <font name='Segoe-Bold'>Failed: DID NOT RAISE SQLAlchemyError</font>. Đây không phải một trong bốn RED failure.", "SmallVN")]
    story += [p(f"RED source: {repo_link('backend/tests/evidence/vt024-red.txt')} · GREEN source: {repo_link('backend/tests/evidence/vt024-green.txt')} · mutation source: {repo_link('backend/tests/evidence/vt024-mutation.txt')} · mutant diff: {repo_link('backend/tests/evidence/vt024-mutation-diff.patch')}", "SmallVN")]
    story += [p("Lệnh tái hiện RED và targeted GREEN (chạy từ backend):", "H2VN")]
    story += [Preformatted(r".\.venv\Scripts\python.exe -m pytest -q --hypothesis-show-statistics tests/test_rate_limit.py tests/test_backfill.py", styles["CodeVN"])]
    story += [p(r"Kết quả: RED có đúng 4 failure trên; persistence characterization pass baseline. Sau patch: targeted 14 passed; Hypothesis retry 40 pass/2 invalid, idempotency 30 pass/4 invalid, 0 failing examples. Lệnh regression cuối: <font name='Courier'>.\.venv\Scripts\python.exe -m pytest -q</font> → 49 passed, 1 deprecation warning. Ruff → All checks passed; mypy unavailable.", "SmallVN")]
    story += [p("Lệnh mutation (PowerShell, chạy từ backend):", "H2VN"), Preformatted(".\\.venv\\Scripts\\python.exe -m pytest -q `\n  tests/test_backfill.py::test_commit_failure_never_returns_success_and_recovery_is_consistent", styles["CodeVN"])]
    story += [PageBreak()]

    story += [
        p("PHỤ LỤC C · COVERAGE VÀ PERFORMANCE", "H1VN"),
        p("Coverage chỉ bao gồm hai module của vertical slice; performance là thử nghiệm mock trong process.", "SmallVN"),
    ]
    coverage_rows = [
        ["Module", "Statements", "Branches", "Combined"],
        ["GitHubClient", "95/121 · 78.51%", "31/50 · 62.00%", "73.68%"],
        ["BackfillService", "151/163 · 92.64%", "35/40 · 87.50%", "91.63%"],
        ["Tổng đã chọn", "246/284 · 86.62%", "66/90 · 73.33%", "83.42%"],
    ]
    story += [table(coverage_rows, [43 * mm, 43 * mm, 43 * mm, 45 * mm], font="CaseCellVN")]
    story += [p("Risk mapping: AC-01 có test 5xx/timeout/ConnectError/bound; AC-02 có 401, unsafe POST/500, 403 exhaustion; AC-03 bảo vệ uniqueness business rows nhưng chưa assert số RawEvent/AuditLog; AC-04 service/API regression và mutant; AC-05 một nguồn lỗi, nguồn khác thành công. Thiếu trực tiếp: một số 404/generic 4xx, POST transport, all-resources-fail. Tỷ lệ không phải coverage toàn repo.", "SmallVN")]
    perf_rows = [
        ["Mock harness", "Kết quả"],
        ["Tải và scenario", "100 worker đồng bộ bằng Barrier; 90 success ngay, 5 transient→success, 5 exhaustion cố ý."],
        ["Requests/outcomes", "115 requests; 95 success, 5 exhaustion; max_retries=2."],
        ["Latency", "p50 0.376 ms · p95 0.701 ms · max 1.131 ms; nearest-rank trên cả 100 task, gồm lỗi."],
    ]
    story += [table(perf_rows, [43 * mm, 131 * mm], font="CaseCellVN")]
    story += [p("Giới hạn: MockTransport không blocking; backoff là no-op nên latency loại trừ thời gian chờ thật. Kết quả không chứng minh p95 production ≤ 3.0 giây, GitHub latency, database throughput hay end-to-end API concurrency. Không gọi GitHub thật.", "SmallVN")]
    story += [p("Lệnh harness (chạy từ backend):", "H2VN"), Preformatted(r".\.venv\Scripts\python.exe tests\perf_retry_harness.py", styles["CodeVN"])]
    story += [p(f"Nguồn: {repo_link('backend/tests/evidence/vt024-coverage-review.md')} · {repo_link('backend/tests/evidence/vt024-coverage-run.txt')} · {repo_link('backend/tests/evidence/vt024-coverage.json')} · {repo_link('backend/tests/evidence/vt024-performance.txt')} · {repo_link('backend/tests/perf_retry_harness.py')} · {repo_link('backend/tests/evidence/vt024-ai-usage-log.md')}", "SmallVN")]
    return story


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    main_story, reflection_words = main_pages()
    story = main_story + appendix_pages()
    doc = SimpleDocTemplate(
        str(OUTPUT), pagesize=A4,
        rightMargin=18 * mm, leftMargin=18 * mm,
        topMargin=21 * mm, bottomMargin=19 * mm,
        title="BT cá nhân 3 · AI-03 · VT-024",
        author="Hoàng Khánh An",
        subject="Bounded retry cho GitHub API: kiểm thử, mutation, coverage và hiệu năng",
    )
    doc.build(story, onFirstPage=page_header, onLaterPages=page_header)
    print(f"PDF={OUTPUT}")
    print(f"REFLECTION_WORDS={reflection_words}")


if __name__ == "__main__":
    main()
