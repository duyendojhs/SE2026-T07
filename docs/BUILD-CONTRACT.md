# SE2026-T07 — BUILD CONTRACT

**Đề tài:** AI-03 — GitHub Project Coach cho nhóm sinh viên  
**Nhóm:** SE2026-T07 — Entropy  
**Phiên bản:** 1.2 — 2026-10-25  
**Trạng thái:** Frozen cùng guide v2.0 sau Batch 6.1; là contract ngắn cho Build, không thay thế guide chi tiết.

---

## 0. Cách dùng

Build phải đọc theo thứ tự:

1. `D:\SE\docs\04-implementation\SE2026_T07-Implementation-Guide.md` — thiết kế chi tiết.
2. File này — invariants, quyết định đã chốt, gate và acceptance checks.

Quy tắc:

- Làm **một sprint mỗi lần**.
- Không sửa guide, `PRIVACY.md`, `.ai/AGENTS.md` nếu task không ghi rõ.
- Trước khi code: in checklist việc sẽ làm.
- Sau khi code: chạy acceptance checks liên quan.
- Nếu guide và contract mâu thuẫn: **dừng, báo, không tự chọn**.

---

## 1. Biên sản phẩm

- Một workspace cho **một nhóm**; schema multi-tenant theo `tenant_id`.
- Không dashboard cho giảng viên/cả lớp.
- Không so sánh chéo nhóm.
- Không chấm điểm, xếp hạng, hoặc tạo finding cấp cá nhân.
- Chỉ đọc metadata GitHub; **không đọc source code**.
- Không Kanban/task management, không mobile/CLI, không tự động ghi vào repo.
- Sản phẩm hướng mức 4–5:
  - rule engine explainable,
  - graph cộng tác,
  - closed-loop,
  - simulator,
  - field study,
  - benchmark,
  - privacy/audit.

---

## 2. Invariants — không được vi phạm

| ID | Invariant |
|---|---|
| **I-01** | Metadata-only: không đọc/lưu `patch`, `diff`, `blob`, file content, source code. |
| **I-02** | Không lưu comment body; chỉ `body_length`, `has_code_block`, và link GitHub nếu cần. |
| **I-03** | Không lưu commit body/footer. `commit.message` chỉ đọc transient; chỉ lưu dòng đầu thành `message_subject` (tối đa 200 ký tự). |
| **I-04** | Không finding/score/ranking cấp cá nhân. Finding chỉ cấp team hoặc module. Không có `silent_member`. |
| **I-05** | Multi-tenant: mọi bảng nghiệp vụ có `tenant_id`; mọi query lọc theo tenant. |
| **I-06** | Pulse: **pseudonymous với server, anonymous với team**; chỉ lưu `respondent_key = HMAC(member_id + week_start + salt)`; API không bao giờ trả `respondent_key`. |
| **I-07** | Pulse chỉ aggregate khi `n ≥ 3`; không ghép pulse với dữ liệu từng người. |
| **I-08** | AI chỉ narrates từ facts; không tự tính số; có citation, validator, refusal khi thiếu dữ liệu. |
| **I-09** | Không dùng PAT fallback. Chỉ GitHub App; permission tối thiểu. |
| **I-10** | Audit là append-only hash chain; không xoá entry giữa chuỗi; retention dùng checkpoint + archive. |
| **I-11** | Không log payload, token, `Authorization`, comment body, `patch`, hoặc response body lỗi. |
| **I-12** | Không hard-code tenant; không dùng `updated_at` làm stale signal. |
| **I-13** | Không đếm bot account là member. |
| **I-14** | PR chưa merge không có cycle time 0; phải censored. |

---

## 3. Decision register

| ID | Quyết định | Acceptance tối thiểu |
|---|---|---|
| **D-01** | Modular monolith: FastAPI + PostgreSQL 16 + Redis/ARQ + Next.js 14. Không microservices. | `docker compose up` chạy; CI xanh. |
| **D-02** | Một workspace = một team; mọi bảng có `tenant_id`. | Không query nào thiếu tenant filter. |
| **D-03** | Field allowlist; `strip_payload()` trước DB/log. | Payload có `patch`/`diff`/`body` không vào DB. |
| **D-04** | `EXTRACT_ONLY_FIELDS = {"commit.message"}`; chỉ lưu `message_subject`. | Test commit body không vào DB. |
| **D-05** | Comment endpoint chỉ lấy metadata; không lấy `body`. | DB không có cột `comment_body`/`body`. |
| **D-06** | Rule DSL YAML; rule phải có `id`, `version`, `severity`, `scope`, `when`, `evidence`, `action`, `confidence`. | Rule test offline; finding có evidence. |
| **D-07** | `priority_score` deterministic; AI không xếp hạng finding. | Cùng facts → cùng score. |
| **D-08** | AI chỉ narrates; prompt có allowlist facts; output có citation; validator từ chối số không có nguồn. | LLM eval 20 case; refusal case pass. |
| **D-09** | Q&A trên facts là **Stretch S5**, không tính MVP; endpoint/tool allowlist riêng. | Nếu làm: prompt-injection test + eval riêng. |
| **D-10** | Repo Replay là **Could S5**; không đọc code; timeline metadata. | Nếu làm: không có diff/patch. |
| **D-11** | Pulse 3 câu/tuần; pseudonymous với server, anonymous với team; `n ≥ 3`. | API không trả `respondent_key`; UI không hiện danh tính. |
| **D-12** | Perception Gap: `flow_score = 1 - min(cycle_time_p50 / target_cycle, 1)`; `collab_score = 1 - review_load_hhi`; `composite = 0.5*flow + 0.5*collab`. | `target_cycle` lấy từ agreement; nếu chưa có, median baseline 6 tuần; ghi rõ. |
| **D-13** | Closed-loop: baseline 6 tuần + 3 tuần tiền cứu; can thiệp bắt đầu S3. Pre/post 3 tuần nếu đủ dữ liệu. | Báo cáo median + bootstrap CI; n < 5 không báo %. |
| **D-14** | Field study fallback: nếu T07 `< 4 tuần dữ liệu` hoặc `< 3 PR đã merge` → bỏ pre/post định lượng; chỉ phỏng vấn + pulse + benchmark. | Báo cáo ghi rõ "không đủ dữ liệu để đánh giá hiệu quả". |
| **D-15** | Nếu đủ dữ liệu, chỉ gọi ITS khi có `≥ 8 điểm tuần` và `≥ 3 điểm sau can thiệp`; nếu không, chỉ pre/post + qualitative. | Không gọi ITS khi thiếu điểm. |
| **D-16** | Simulator là DES rời rạc, không ML prediction; backtest 7–9 chỉ khi chưa can thiệp. Nếu can thiệp từ S3: holdout fit 1–4, dự đoán 5–6, hoặc synthetic. | Báo MAPE + CI + caveat. |
| **D-17** | Benchmark 60 synthetic team = 7 archetype × 8 + 4 mixed edge (1 noisy, 1 missing-data, 1 bot-heavy, 1 revert-heavy). | Seed cố định; manifest; ground truth; chạy offline. |
| **D-18** | Audit hash chain per tenant + checkpoint + archive; `actor_hash`, không lưu login/email. | Verify chain; test audit không chứa login/email. |
| **D-19** | Retention: audit không có `deleted_at`; chỉ archive + checkpoint. Finding dùng `status`/`deleted_at`. | Không xoá entry giữa chuỗi. |
| **D-20** | GitHub App; permission tối thiểu; rate-limit handling; ETag/cursor; không PAT fallback. | Rate-limit test; backfill idempotent. |
| **D-21** | ADR sequencing: S0 cần 001–005; 006/008 trước S1; 009 trước S2; 007/011 trước S4; 010/012 trước S5. | Checklist ADR khớp sprint. |
| **D-22** | T07 repo hiện chỉ là scaffolding; field study phải chấp nhận N nhỏ và fallback. | Không overclaim kết quả. |

---

## 4. Data model guardrails

### Bảng bắt buộc

- `tenants`
- `members` (không lưu login trong finding/audit)
- `repos`
- `pull_requests`
- `issues`
- `reviews`
- `comments` (`body_length`, `has_code_block`)
- `commits` (`message_subject`)
- `metrics_daily`
- `findings`
- `agreements`
- `interventions`
- `pulse_responses`
- `audit_logs`
- `audit_checkpoints`

### Cấm

- `patch`, `diff`, `blob`, `file_content`, `raw_content`
- `comment_body`
- `commit_body`
- `commit.message` trong cột lưu trữ
- `respondent_key` trong API response
- Bảng finding/score cấp cá nhân
- Query không có `tenant_id`

### Audit

- `audit_logs` có `prev_hash`, `entry_hash`, `actor_hash`, `timestamp`, `tenant_id`.
- Không có `deleted_at`.
- Retention job chỉ archive + ghi checkpoint; không xoá entry giữa chuỗi.
- Verify từ checkpoint gần nhất; nếu checkpoint mất → `valid=unknown`, không báo `valid=true`.

---

## 5. Rule engine + AI guardrails

### Rule engine

- DSL YAML versioned.
- Facts là deterministic; rule không truy cập DB trực tiếp.
- Finding có:
  - `rule_id`, `version`
  - `severity`
  - `scope`: `team` hoặc `module`
  - `evidence`: field path + giá trị
  - `action`
  - `confidence`
  - `priority_score` deterministic
- Không rule nào tạo finding gắn tên cá nhân.
- `module_coverage_risk` chỉ chạy nếu repo trả file path; nếu không, skip.
- `deadline_crunch` chỉ chạy nếu có milestone; nếu không, skip.

### AI

- LLM chỉ viết narrative từ facts đã cho.
- Không để LLM tính metric, priority, hoặc chọn finding.
- Prompt injection guard:
  - facts là JSON có schema;
  - không đưa raw comment/commit body;
  - output phải cite field.
- Validator:
  - số trong output phải khớp facts;
  - nếu thiếu dữ liệu → refusal template;
  - nếu vi phạm → fallback template không dùng LLM.
- LLM eval tối thiểu 20 case, gồm:
  - grounded summary,
  - refusal,
  - prompt injection,
  - số bịa.

---

## 6. Sprint gates

| Sprint | Tuần | Mục tiêu | Gate bắt buộc | Fallback hợp lệ |
|---|---|---|---|---|
| **S0** | 1 | Docs, ADR, skeleton, compose, CI, fixtures | `docker compose up`; CI xanh; ADR-001..005 | Không |
| **S1** | 2–3 | Auth + GitHub App + backfill + DB + audit | App cài lên T07; ingest 90 ngày; `/health`; rate-limit test; ADR-006/008 xong | Nếu GitHub App bị chặn: mock data + video backup; **không PAT** |
| **S2** | 4–5 | Metrics + 5 rule + findings API + tests | Rule tests offline; dashboard đọc findings; ADR-009 xong | Ít rule hơn 5 nếu data thiếu; ghi rõ |
| **S3** | 6–7 | Dashboard + graph + weekly summary grounded + deploy T07 | 3 màn demo; LLM eval 20 case; bắt đầu dùng thật tuần 7 | Nếu graph thiếu file path: chỉ graph review/co-change |
| **S4** | 8 | Agreements + intervention + pulse + simulator | Before/after **sơ bộ** (2 tuần post) **hoặc fallback §18.5**; backtest (hoặc synthetic); pulse tuần 7–9; ADR-007/011 xong | Nếu `< 4 tuần` hoặc `< 3 PR`: bỏ pre/post định lượng |
| **S5** | 9–10 | Benchmark + field study + Replay/Q&A nếu kịp + polish | 60 synthetic team; phỏng vấn; **đủ 3 tuần post hoặc fallback §18.5**; báo cáo; ADR-010/012 xong | Replay/Q&A cắt nếu S3–S4 chưa xanh |

### Definition of Done chung

- CI xanh.
- Không có P0/P1 mở.
- Test privacy/tenant/audit pass.
- Không thêm dependency lớn nếu chưa có ADR.
- Không sửa guide/PRIVACY/AGENTS ngoài task.
- README/docs cập nhật cho sprint.

---

## 7. Field study fallback — chi tiết

### Khi nào fallback

Kích hoạt nếu **một trong hai**:

- T07 có `< 4 tuần dữ liệu`, hoặc
- T07 có `< 3 PR đã merge`.

### Khi fallback

- Bỏ pre/post định lượng.
- Không báo % hiệu quả.
- Chỉ dùng:
  - phỏng vấn bán cấu trúc,
  - pulse aggregate,
  - benchmark synthetic,
  - quan sát qualitative.
- Báo cáo ghi rõ:

> "Không đủ dữ liệu để đánh giá hiệu quả; kết quả chỉ mang tính mô tả."

### Khi đủ dữ liệu

- Pre/post 3 tuần; median + bootstrap CI.
- `n < 5` → không báo %.
- ITS chỉ khi `≥ 8 điểm tuần` và `≥ 3 điểm sau can thiệp`.
- Không kết luận nhân quả.
- Ghi rõ N=1, reflexivity, Hawthorne, deadline/exam confounders.

---

## 8. Benchmark

- 60 team:
  - 7 archetype × 8 = 56,
  - 4 mixed edge: 1 noisy, 1 missing-data, 1 bot-heavy, 1 revert-heavy.
- Seed cố định; ghi `benchmark/manifest.json`.
- Ground truth từ generator, không từ LLM.
- Chạy offline; không gọi GitHub.
- Metrics:
  - precision/recall/F1 theo rule,
  - false positive rate,
  - calibration nếu có confidence.
- Không dùng benchmark để chấm điểm sinh viên.

---

## 9. Acceptance checks

### Trước khi merge

```text
[ ] Không có silent_member / individual_score / leaderboard trong code.
[ ] Không có cột patch, diff, blob, comment_body, commit_body.
[ ] Mọi bảng nghiệp vụ có tenant_id.
[ ] API không trả respondent_key.
[ ] Audit chain verify được; test không chứa login/email.
[ ] Log redaction test: patch, token, Authorization, comment body.
[ ] Rate-limit test: 403/429 có backoff, không loop.
[ ] Rule test offline: facts → finding + evidence.
[ ] LLM eval 20 case: grounded/refusal/injection.
[ ] Benchmark chạy offline; manifest + seed.
```

### Trước khi demo

```text
[ ] 3 màn hình: overview, finding/evidence, graph hoặc weekly summary.
[ ] Mỗi finding có evidence + action + citation.
[ ] Không có số liệu cá nhân trên dashboard.
[ ] Pulse chỉ aggregate khi n ≥ 3.
[ ] Audit verify hiển thị đúng.
```

---

## 10. Build protocol

### Trước khi code

1. Đọc guide + contract.
2. Xác định sprint.
3. In checklist:
   - file sẽ tạo/sửa,
   - test sẽ viết,
   - acceptance sẽ chạy.
4. Nếu thiếu quyết định: dừng, hỏi.

### Trong khi code

- Không sửa file ngoài phạm vi sprint.
- Không đổi schema ngoài migration.
- Không thêm package nếu chưa có lý do.
- Commit nhỏ; message rõ.

### Sau khi code

1. Chạy test.
2. Chạy acceptance checks.
3. In diff tóm tắt.
4. Ghi rõ:
   - đã xong gì,
   - chưa xong gì,
   - rủi ro,
   - bước tiếp theo.

---

## 11. Prompt mẫu cho Build

```text
Bạn là Build. Trước khi làm:

1. Đọc:
   - D:\SE\docs\04-implementation\SE2026_T07-Implementation-Guide.md (v2.0)
   - BUILD-CONTRACT.md

2. Chỉ làm đúng sprint được giao.

3. Không sửa guide/PRIVACY/AGENTS nếu task không ghi rõ.

4. Trước khi code:
   - in checklist file sẽ sửa/tạo,
   - in test sẽ viết,
   - in acceptance sẽ chạy.

5. Sau khi code:
   - chạy test,
   - chạy acceptance checks,
   - in diff tóm tắt.

6. Nếu guide và contract mâu thuẫn:
   - dừng,
   - báo rõ mâu thuẫn,
   - không tự diễn giải.
```

---

## 12. Freeze status — đã đóng

Guide v2.0 (2026-10-25) và `PRIVACY.md` đã đồng bộ với contract:

- S4/S5 gate đã có fallback §18.5.
- §18.5 analysis đã có fallback.
- §13.2 backtest đã có điều kiện holdout/synthetic.
- §1.7 mức 4, §12.3 ITS/pre-post và §18.5 ngưỡng dữ liệu đã được làm rõ.
- `PRIVACY.md` dùng `items` thay vì `answers`.

Guide v2.0 là bản freeze. Mọi thay đổi sau freeze phải có ADR mới và cập nhật contract.

---

## 13. Nguyên tắc cuối

- Không thêm tính năng ngoài plan.
- Không biến dashboard thành công cụ giám sát cá nhân.
- Không overclaim từ dữ liệu N nhỏ.
- Không giấu lỗi mô hình.
- Không dùng "AI" nếu không có eval.
- Không sửa guide để hợp thức hoá code; nếu code sai, sửa code.
