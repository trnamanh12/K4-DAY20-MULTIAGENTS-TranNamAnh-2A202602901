# Báo cáo Lab: Self evolving Agentic

> Sao chép tệp này thành `report/REPORT.md` (đã làm ở Phần 0) và điền dần qua các Phần của lab. Xóa các dòng hướng dẫn dạng trích dẫn (bắt đầu bằng `>`). Văn phong kỹ thuật, ngắn gọn, mọi nhận định đi kèm số liệu hoặc bằng chứng. Trong buổi học: điền mục 1 đến 7 (bản nháp). Sau buổi học: hoàn thiện mục 8 đến 10.

## 1. Thông tin nhóm và cấu hình

| Họ tên | Mã sinh viên | Phần đóng góp |
|---|---|---|
| | | |

- Nhà cung cấp và mô hình (`LAB_MODEL`, không ghi khóa API), nhiệt độ (`LAB_TEMPERATURE`), `recursion_limit`: `google_genai:gemini-3.5-flash-lite`, nhiệt độ 0; nhà cung cấp cảnh báo model dùng sampling cố định nên bỏ qua nhiệt độ. `recursion_limit=40` cho logs và một lần thử code; các run còn lại dùng 60.
- Phiên bản Deep Agents (`pip show deepagents`), hệ điều hành, chạy trực tiếp hay trong Docker: `deepagents 0.7.21`, Python 3.14.7, Linux, chạy trực tiếp.
- Số lần chạy tác vụ đã dùng / ngân sách: có 15 bản ghi (baseline 6, subagents 6, skills-auto learning 3), ngoài ra có các lần chạy lại và một lần subagents bị ngắt; có lỗi giới hạn đệ quy và quota; ngân sách tiền/tokens do nhà cung cấp đặt, không đọc được từ kho.
- Commit của tag `freeze`: `2157cc3`.

## 2. Giả thuyết (commit TRƯỚC tag `freeze`, Phần 4.0)

> Dự đoán điều kiện nào đạt điểm cao nhất trên **tác vụ đánh giá** và vì sao. Nêu căn cứ từ phân loại lỗi (mục 4) và từ tài liệu tham khảo. Điền cả ba dòng; `verify_freeze.py` kiểm tra điều này.

- H1 (subagents so với baseline): Trên eval, subagents sẽ không cải thiện ổn định điểm tổng so với baseline và sẽ dùng nhiều token hơn. Learning cho thấy điểm không tăng ở code/logs, giảm ở data, trong khi token trung bình tăng từ 159,159 lên 435,142.
- H2 (skills-auto so với baseline): Skills-auto có thể giữ hoặc cải thiện một số check kỹ thuật có quy trình tương tự, nhưng không dự đoán sẽ giải quyết quy ước mới của eval vì skill được rút từ feedback learning. SkillsBench ghi nhận skill có thể giúp khi được biên soạn/chọn lọc, nhưng SkillEvolBench cho thấy skill tự sinh thường không chuyển bền vững sang deployment đã đóng băng; vì vậy dự đoán không có cải thiện tổng điểm nhất quán ([SkillsBench](https://arxiv.org/abs/2602.12670); [SkillEvolBench](https://arxiv.org/abs/2605.24117)).
- H3 (tác vụ học so với tác vụ đánh giá): Điểm eval sẽ bằng hoặc thấp hơn learning, vì eval đổi dữ liệu và bổ sung một quy ước; quy trình kỹ thuật có thể chuyển giao nhưng quy ước không xuất hiện trong feedback learning thì không thể học trực tiếp. SkillEvolBench nêu rủi ro suy giảm khi đóng băng skill dưới chuyển dịch ngữ cảnh.

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

`report/table.md` hiện chỉ có `baseline` và `subagents`; `skills-auto` chưa có kết quả eval do quota API. Các ô 0/9 và 0/10 của `subagents` là lỗi quota ghi vào `error`, không phải điểm tác tử.

```text
| Task | baseline | subagents |
|---|---|---|
| code-learn | 7/10 | 7/10 |
| data-learn | 5/8 | 4/8 |
| logs-learn | 6/9 | 6/9 |
| code-eval | 7/11 | 7/11 |
| data-eval | 5/9 | 0/9 |
| logs-eval | 6/10 | 0/10 |
| **Mean score - learning tasks** | 0.66 | 0.62 |
| **Mean score - evaluation tasks** | 0.60 | 0.21 |
| **Mean tokens per run** | 132,402 | 269,644 |
| **Runs that read a skill** | 0/6 | 0/6 |
```

```text
condition     role    technical  house rules  mean tokens  read a skill
baseline      eval     18/18         0/12         105,646      0/3
baseline      learn    18/18         0/9          159,159      0/3
subagents     eval      7/18         0/12         104,147      0/3
subagents     learn    17/18         0/9          435,142      0/3
```

Không có kết quả `skills-auto` chính thức sau freeze; các lần chạy phát triển được lưu ở `results/skills-auto-dev/`. Hai run eval của `subagents` (`data-eval`, `logs-eval`) có `GoogleRateLimitError` 429 và điểm 0 do lỗi hạ tầng. Không run nào ghi `skills_modified=true`.

`verify_freeze.py` hiện in `checked 0 runs of skill conditions: OK`: nó xác nhận tag, commit giả thuyết và thư mục skill không đổi, nhưng chưa thể xác nhận bất kỳ lần chạy skills-auto chính thức nào.

## 8. Phân tích

> Trả lời từng câu bằng số liệu từ mục 7 và bằng chứng từ vết. Kết quả âm hoặc không có khác biệt vẫn hợp lệ nếu được phân tích tốt.

1. Trên learning, baseline đạt 0.66 trung bình còn subagents đạt 0.62. Trên eval, baseline đạt 0.60; subagents chỉ có một run hợp lệ (`code-eval` 7/11, bằng baseline), hai run còn lại lỗi quota. Chưa đủ dữ liệu để so sánh eval đầy đủ hoặc kết luận điều kiện tốt nhất.
2. Baseline learning đạt 18/18 check kỹ thuật nhưng 0/9 check quy ước. Skills-auto learning đạt 18/18 kỹ thuật và 2/9 quy ước; mức tăng quy ước nằm ở `logs-learn`, nơi điểm tăng từ 6/9 lên 8/9. Chưa có eval skills-auto nên chưa xác định được tác dụng trên quy ước mới.
3. Trace `logs-learn` cho thấy skill log được đọc (`skills_read=1`); lỗi giảm từ ba quy ước baseline xuống còn `rule_schema_header`, điều mà skill không hướng dẫn. Ở `data-learn`, cả ba skill được đọc nhưng điểm vẫn 5/8 và agent không tạo `clean.csv` hoặc metadata; đọc skill không đảm bảo làm theo đầy đủ.
4. Learning-only mean tokens: baseline 159,159; subagents 435,142; skills-auto 210,531. Subagents dùng khoảng 2.7 lần baseline nhưng điểm trung bình thấp hơn; skills-auto tốn hơn baseline nhưng cải thiện một phần check quy ước trong logs. Điểm trên mỗi token chưa thể so sánh đầy đủ vì một run skills-auto lỗi và thiếu eval skills-auto; bằng chứng hiện có không ủng hộ chi phí subagents.
5. Ba skill không chứa marker hoặc tên tệp riêng của tác vụ eval; curator chỉ nạp run có `role=learn`, validator từ chối marker eval, và skills đã đóng băng trước khi eval. Skill code vẫn gần với quy ước của tác vụ học nên nguy cơ quá khớp còn tồn tại.
6. Learning results của skills-auto được sao lưu ở `results/skills-auto-dev/`, nhưng chưa chạy lại sau freeze vì quota cạn. Chưa tính được chênh lệch nhiễu của cùng bộ skill.

## 9. Hạn chế và tính hợp lệ

> Nêu ít nhất 3 hạn chế và ảnh hưởng của từng hạn chế đến kết luận (ví dụ: chỉ 3 tác vụ mỗi vai trò, mỗi cấu hình chạy một lần, nhiễu của mô hình, tác vụ do giảng viên thiết kế sẵn quy ước, chỉ một mô hình).

1. Mỗi vai trò chỉ có ba tác vụ và mỗi cấu hình chạy một lần; kết quả nhạy với dữ liệu cụ thể và không cho phép ước lượng ổn định biến thiên.
2. Chỉ dùng một mô hình Gemini; tool use, tốc độ và quota nhà cung cấp giới hạn khả năng khái quát. Hai eval subagents thất bại do quota, không phải năng lực tác tử.
3. `recursion_limit` không đồng nhất giữa mọi lần chạy (40 hoặc 60); một số run chạm GraphRecursionError, nên so sánh điểm/token bị ảnh hưởng bởi giới hạn chạy.
4. Chưa có eval skills-auto chính thức và chỉ một trong ba eval subagents hợp lệ; giả thuyết chính về chuyển giao skill chưa được kiểm định.

## 10. Kết luận

Các lần chạy learning cho thấy baseline làm tốt check kỹ thuật nhưng bỏ sót nhiều quy ước đầu ra. Skill log được đọc và đi kèm mức tăng 2 check ở `logs-learn`, nhưng chưa đủ để khẳng định hiệu quả tổng quát. Subagents tăng mạnh chi phí token mà điểm learning không tăng. Chưa thể kết luận về eval skills-auto vì quota miễn phí 500 request/ngày đã hết; bước tiếp theo là chạy đủ eval bằng provider có quota rồi cập nhật bảng và phân tích.

## Phụ lục

- Lệnh đã chạy (theo thứ tự): `.venv/bin/pytest tests/test_01_provided.py`; `.venv/bin/pytest tests/test_02_agent.py -k subagents`; `.venv/bin/pytest tests/test_02_agent.py`; `.venv/bin/pytest tests/test_03_runner.py`; `.venv/bin/pytest tests/test_04_curator.py`; `.venv/bin/pytest`; `.venv/bin/python scripts/tour.py`; baseline learning (`data-learn`, sau đó `code-learn logs-learn`, code chạy lại); subagents learning (`--tasks learn --recursion-limit 60`); `.venv/bin/python -m lab.curator`; skills-auto learning (limit 40, sau đó code/data chạy lại ở 60); `git commit -m hypotheses`; `git commit --allow-empty -m 'freeze skills' && git tag freeze`; baseline eval (`--tasks eval --recursion-limit 60`); subagents eval (`--tasks eval --recursion-limit 60`); `.venv/bin/python scripts/verify_freeze.py`; `.venv/bin/python -m lab.compare > report/table.md`; `.venv/bin/python scripts/check_breakdown.py`.
- Thử thách mở rộng (nếu có): hướng chọn, kết quả, nhận xét.
- Ghi chú khác: Gemini API trả `429 RESOURCE_EXHAUSTED`, giới hạn miễn phí 500 requests/ngày, retry estimate hơn 13 giờ. Do đó `results/skills-auto/` chưa có run chính thức; hai run subagents eval ghi lỗi hạ tầng. Các run skills-auto/code bị recursion/quota ghi trong JSON và không được diễn giải như kết quả model hợp lệ. Để tiếp tục sau khi đổi sang provider có quota hoặc quota reset: chạy `.venv/bin/python -m lab.runner --condition subagents --tasks data-eval logs-eval --recursion-limit 60`, rồi `.venv/bin/python -m lab.runner --condition skills-auto --tasks all --recursion-limit 60`; sau đó tạo lại bảng, chạy `verify_freeze.py` và `check_breakdown.py`, cập nhật phân tích, rồi commit.
