# Báo cáo Lab: Self evolving Agentic

> Sao chép tệp này thành `report/REPORT.md` (đã làm ở Phần 0) và điền dần qua các Phần của lab. Xóa các dòng hướng dẫn dạng trích dẫn (bắt đầu bằng `>`). Văn phong kỹ thuật, ngắn gọn, mọi nhận định đi kèm số liệu hoặc bằng chứng. Trong buổi học: điền mục 1 đến 7 (bản nháp). Sau buổi học: hoàn thiện mục 8 đến 10.

## 1. Thông tin nhóm và cấu hình

| Họ tên | Mã sinh viên | Phần đóng góp |
|---|---|---|
| | | |

- Nhà cung cấp và mô hình (`LAB_MODEL`, không ghi khóa API), nhiệt độ (`LAB_TEMPERATURE`), `recursion_limit`: `google_genai:gemini-3.5-flash-lite`, nhiệt độ 0; `recursion_limit=60` cho data/code và 40 cho logs. Lần chạy code đầu tiên bị giới hạn ở 40 và được chạy lại ở 60.
- Phiên bản Deep Agents (`pip show deepagents`), hệ điều hành, chạy trực tiếp hay trong Docker: `deepagents 0.7.21`, Python 3.14.7, Linux, chạy trực tiếp.
- Số lần chạy tác vụ đã dùng / ngân sách: hiện có 9 bản ghi cho ba điều kiện learning, ngoài ra có các lần chạy lại; có lần chạy bị giới hạn đệ quy và một lỗi quota; ngân sách tiền/tokens do nhà cung cấp đặt, không đọc được từ kho.
- Commit của tag `freeze`:

## 2. Giả thuyết (commit TRƯỚC tag `freeze`, Phần 4.0)

> Dự đoán điều kiện nào đạt điểm cao nhất trên **tác vụ đánh giá** và vì sao. Nêu căn cứ từ phân loại lỗi (mục 4) và từ tài liệu tham khảo. Điền cả ba dòng; `verify_freeze.py` kiểm tra điều này.

- H1 (subagents so với baseline):
- H2 (skills-auto so với baseline):
- H3 (tác vụ học so với tác vụ đánh giá):

## 3. Làm quen Deep Agents (Phần 0.3)

1. Công cụ gồm `ls`, `read_file`, `write_file`, `edit_file`, `delete`, `glob`, `grep`, `execute`, và `task`. `execute` chạy lệnh shell.
2. `general-purpose` là subagent đa dụng có thể tìm tệp, nghiên cứu và làm nhiều bước. Mỗi lần gọi mặc định là stateless; nó chỉ nhận prompt được giao, không tự thấy toàn bộ lịch sử/ngữ cảnh của tác tử chính.
3. Mô tả `task`: “Put full detail in the prompt and state exactly what it should return.” Mô tả `execute`: “Use absolute paths and avoid `cd` so the working directory stays stable.” System prompt mặc định in ra là rỗng (`''`).

## 4. Đường cơ sở và phân loại lỗi (Phần 2.2)

> Chỉ dùng tác vụ học. Mỗi dòng là một check thất bại.

| Tác vụ | Check thất bại | Nhóm lỗi (A-G) | Bằng chứng (trích ngắn từ `detail` hoặc vết) |
|---|---|---|---|
| code-learn | rule_type_hints | E | `RULE: every public function ... has type annotations` |
| code-learn | rule_regression_tests | E | `RULE: add tests/test_regressions.py ... (at least 3)` |
| code-learn | rule_changelog | E | `RULE: record each fix in CHANGELOG.md ... (at least 3 bullets)` |
| data-learn | rule_money_in_cents | E | `RULE: money values in answer.json are integer cents` |
| data-learn | rule_meta_block | E | `RULE: answer.json has an object meta` with source, rows_in, rows_used |
| data-learn | rule_clean_csv | E | `RULE: write workspace/clean.csv` with specified columns, UTC timestamps, canonical regions, integer cents |
| logs-learn | rule_service_names | E | `RULE: service names ... lower-case with '-' replaced by '_'` |
| logs-learn | rule_sorted_errors | E | `RULE: errors is sorted by service, then by timestamp_utc` |
| logs-learn | rule_schema_header | E | `RULE: top-level object has schema_version 2 and generated_by log-triage` |

Nhận xét: cả 9 thất bại thuộc nhóm E: tác tử hoàn thành phần việc chính nhưng bỏ sót quy ước chấm điểm bổ sung. Kết quả là bằng chứng cho việc báo cáo chi tiết các đầu ra khi kiểm tra yêu cầu; skill có thể nhắc tác tử đọc toàn bộ định dạng/README và kiểm tra các yêu cầu đầu ra phụ, nhưng không thể tự biết quy ước ẩn nếu chúng không được nêu.

## 5. Điều kiện `subagents` (Phần 2.3)

- Các subagent đã định nghĩa: `explorer` đọc đặc tả và báo cáo, `implementer` thực hiện thay đổi và chạy kiểm tra, `reviewer` kiểm tra độc lập; vai trò tách việc khảo sát, sửa và xác minh.
- `subagent_calls`: `code-learn` 3 (explorer, general-purpose, implementer); `data-learn` 3 (general-purpose); `logs-learn` 0. Logs là trường hợp hợp lệ: trace cho thấy tác tử chính đã trực tiếp đọc log, chuyển đổi và kiểm tra kết quả.
- Lời giao việc cho code nêu đường dẫn, mục tiêu, edge cases và yêu cầu kiểm tra; sau báo cáo implementer, tác tử chính chạy pytest. Lời giao việc cho data truyền quy tắc dedupe, ngày/múi giờ, giá trị thiếu và câu hỏi về convention, nhưng kết quả cuối vẫn 4/8; trace không cho thấy kiểm tra toàn bộ cấu trúc đầu ra trước khi kết thúc. Với logs không có giao việc để đánh giá.
- `subagents` đạt `code-learn` 7/10 (21 tool calls, 256,674 tokens), `data-learn` 4/8 (11 tool calls, 955,735 tokens), `logs-learn` 6/9 (11 tool calls, 93,017 tokens). Trung bình 435,142 tokens so với 159,159 của baseline; chênh lệch chủ yếu do data-learn. Điểm không tăng so với baseline ở code/logs và giảm ở data.

## 6. Self-evolving: skill do curator sinh (Phần 3)

- Số lần chạy curator, số skill bị xóa và lý do: chạy một lần; sinh 3 skill hợp lệ; không xóa skill và không chạy lại.

| Skill | Tổng quát hay riêng cho tác vụ học? | Đúng hay sai (nêu chỗ sai nếu có) | Độ dài, `description` và `skills_read` ở Phần 3.4 |
|---|---|---|---|
| `enforce-type-hints-and-tests` | Khá riêng cho sửa mã Python; còn lặp lại quy ước CHANGELOG và regression test của tác vụ học | Đúng nhưng chưa nêu số lượng tối thiểu hay cấu trúc tiêu đề chính xác; không thấy hướng dẫn gây hại | 7 dòng; description kích hoạt khi viết/sửa Python; `skills_read=0` trong bản ghi vì GraphRecursionError ở giới hạn 60 làm mất luồng message |
| `format-financial-data-in-cents` | Tổng quát cho dữ liệu tiền tệ, kèm nhắc metadata và dữ liệu sạch | Chuyển tiền sang integer cents là đúng; nhắc định dạng metadata còn chung, chưa nêu kiểm tra múi giờ/trùng lặp | 6 dòng; description kích hoạt khi xử lý tài chính hoặc ghi tiền ra JSON/CSV; `skills_read=3` (đọc cả ba skill) |
| `normalize-identifiers-and-sort-logs` | Tổng quát cho log/sự kiện có tên dịch vụ và timestamp | Quy tắc chuẩn hóa và sắp xếp đúng; thiếu chi tiết định dạng timestamp và các trường đầu ra | 6 dòng; description nêu rõ log/sự kiện; `skills_read=1` |

Ở lần chạy skills-auto trên `data-learn`, agent đọc cả ba skill nhưng vẫn đạt 5/8 như baseline; trace cho thấy nó chỉ ghi `answer.json`, không tạo `clean.csv` hoặc metadata. Trên `logs-learn`, agent đọc skill log và đạt 8/9 so với baseline 6/9; check còn thiếu là `rule_schema_header`, điều mà skill không đề cập. Lần `code-learn` cuối cùng hit GraphRecursionError ở giới hạn 60 nên không có vết luồng chính để đo tác dụng skill.

## 7. Kết quả so sánh (Phần 4.3, 4.4)

> Dán nội dung `report/table.md` và kết quả `python scripts/check_breakdown.py`. Nêu các lần chạy có `error` hoặc `skills_modified = true` (nếu có) và cách xử lý.

```text
(dán bảng ở đây)
```

## 8. Phân tích

> Trả lời từng câu bằng số liệu từ mục 7 và bằng chứng từ vết. Kết quả âm hoặc không có khác biệt vẫn hợp lệ nếu được phân tích tốt.

1. So với `baseline`, điều kiện nào cải thiện điểm tác vụ **học**? Điều kiện nào cải thiện điểm tác vụ **đánh giá**? Có điều kiện nào cải thiện tác vụ học nhưng không cải thiện tác vụ đánh giá? Nếu có, đó là dấu hiệu gì?
2. Tách điểm thành check kỹ thuật và check quy ước (`rule_`). Skill do curator sinh giúp nhóm check nào? Check quy ước **mới** của tác vụ đánh giá có được skill giúp không, và vì sao?
3. Dựa vào vết và `skills_read`, giải thích một check mà skill giúp đạt và một check mà skill không giúp (skill chưa được đọc, đọc nhưng không làm theo, skill thiếu hoặc sai).
4. Chi phí: so sánh số token trung bình giữa các điều kiện. Điều kiện nào có hiệu quả tốt nhất theo điểm trên mỗi token? Đa tác tử có đáng chi phí trong thí nghiệm này không?
5. Có dấu hiệu rò rỉ dữ liệu hoặc quá khớp nào trong skill sinh ra không? Nhóm đã phòng tránh như thế nào?
6. Nhiễu: so sánh điểm tác vụ học của cùng bộ skill ở Phần 3.4 (đã sao lưu) và sau đóng băng. Chênh lệch bao nhiêu? Nó cho biết điều gì về độ tin cậy của các chênh lệch trong bảng ở mục 7?

## 9. Hạn chế và tính hợp lệ

> Nêu ít nhất 3 hạn chế và ảnh hưởng của từng hạn chế đến kết luận (ví dụ: chỉ 3 tác vụ mỗi vai trò, mỗi cấu hình chạy một lần, nhiễu của mô hình, tác vụ do giảng viên thiết kế sẵn quy ước, chỉ một mô hình).

1.
2.
3.

## 10. Kết luận

> Tối đa 5 câu. Chỉ khẳng định điều số liệu hỗ trợ. Nêu một đề xuất cải tiến tiếp theo.

## Phụ lục

- Lệnh đã chạy (theo thứ tự):
- Thử thách mở rộng (nếu có): hướng chọn, kết quả, nhận xét.
- Ghi chú khác:
