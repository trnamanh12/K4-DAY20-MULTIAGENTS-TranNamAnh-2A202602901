# Báo cáo Lab: Self evolving Agentic

## 1. Thông tin và cấu hình

| Họ tên | Mã sinh viên | Phần đóng góp |
|---|---|---|
| Trần Nam Anh | 2A202602901 | Triển khai harness, chạy thí nghiệm và tổng hợp báo cáo với hỗ trợ của Codex |

Tên và mã sinh viên lấy từ tên kho mã nguồn.

- Mô hình: `google_genai:gemini-3.5-flash-lite`; `LAB_TEMPERATURE=0`. SDK cảnh báo mô hình dùng sampling cố định, bỏ qua tham số nhiệt độ.
- Môi trường: Python 3.14.7, Linux, Deep Agents 0.7.21, chạy trực tiếp trong `.venv`.
- Giới hạn: baseline data/code learning 60; baseline logs learning 40; subagents 60; skills-auto phát triển 40 rồi chạy lại code/data ở 60; sáu run skills-auto chính thức 100 để tránh cắt sớm sau khi code đã chạm 60.
- Ngày 07/10/2026, thay API key và giữ nguyên tên mô hình. Các run tiếp tục được giới hạn 0.2 yêu cầu mô hình/giây, bucket 1, để tránh lỗi quota theo phút. Vì thay đổi pacing, không dùng thời gian chạy để khẳng định điều kiện nào nhanh hơn.
- Có 18 bản ghi chính thức (6 tác vụ × 3 điều kiện), 3 bản ghi phát triển skills-auto và các lần thử lỗi/chạy lại. Tổng token của 18 run chính thức: 4,029,629; không đặt ngân sách tiền cố định và không quy đổi token thành giá API.
- Commit giả thuyết: `3fd4309`; tag `freeze`: `2157cc3874549053cd9f067ae548e00a8d093457`. Skill không thay đổi sau tag.

## 2. Giả thuyết đã commit trước freeze

Ba giả thuyết dưới đây giữ nguyên nội dung đã commit trước khi xem điểm eval.

- H1 (subagents so với baseline): Trên eval, subagents sẽ không cải thiện ổn định điểm tổng so với baseline và sẽ dùng nhiều token hơn. Learning cho thấy điểm không tăng ở code/logs, giảm ở data, trong khi token trung bình tăng từ 159,159 lên 435,142.
- H2 (skills-auto so với baseline): Skills-auto có thể giữ hoặc cải thiện một số check kỹ thuật có quy trình tương tự, nhưng không dự đoán sẽ giải quyết quy ước mới của eval vì skill được rút từ feedback learning. SkillsBench ghi nhận skill có thể giúp khi được biên soạn/chọn lọc, nhưng SkillEvolBench cho thấy skill tự sinh thường không chuyển bền vững sang deployment đã đóng băng; vì vậy dự đoán không có cải thiện tổng điểm nhất quán ([SkillsBench](https://arxiv.org/abs/2602.12670); [SkillEvolBench](https://arxiv.org/abs/2605.24117)).
- H3 (tác vụ học so với tác vụ đánh giá): Điểm eval sẽ bằng hoặc thấp hơn learning, vì eval đổi dữ liệu và bổ sung một quy ước; quy trình kỹ thuật có thể chuyển giao nhưng quy ước không xuất hiện trong feedback learning thì không thể học trực tiếp. SkillEvolBench nêu rủi ro suy giảm khi đóng băng skill dưới chuyển dịch ngữ cảnh.

## 3. Làm quen Deep Agents

1. Tour in các công cụ `ls`, `read_file`, `write_file`, `edit_file`, `delete`, `glob`, `grep`, `execute`, `task`; `execute` chạy shell.
2. `general-purpose` có thể khảo sát tệp và làm nhiệm vụ nhiều bước, nhận prompt được giao và trả một báo cáo cuối. Phiên gọi mặc định stateless, không tự nhận toàn bộ lịch sử tác tử chính. Baseline vẫn có subagent mặc định, nhưng các baseline run ở đây ghi `subagent_calls=0`.
3. Mô tả `task`: “Put full detail in the prompt and state exactly what it should return.” Mô tả `execute`: “Use absolute paths and avoid `cd` so the working directory stays stable.” System prompt mặc định của tour là rỗng (`''`); harness của lab dùng `BASE_PROMPT` có quy ước đường dẫn tương đối `workspace/...` cho file tools và shell.

Backend chỉ truyền PATH, HOME của sandbox và PYTHONDONTWRITEBYTECODE; không kế thừa môi trường chứa API key. Workspace được sao chép sang thư mục tạm và chấm trước khi xóa. Token cộng ở mọi lần gọi mô hình, gồm subagent; số tool call, delegation và skill read chỉ đo luồng chính.

## 4. Baseline và phân loại lỗi

| Tác vụ học | Check thất bại | Nhóm A–G | Bằng chứng từ feedback |
|---|---|---|---|
| code-learn | `rule_type_hints` | E | `RULE: every public function (name not starting with '_') in the package has type annotations on all parameters and on the return value.` |
| code-learn | `rule_regression_tests` | E | `RULE: add tests/test_regressions.py with one test function per bug you fixed (at least 3); the file must pass.` |
| code-learn | `rule_changelog` | E | `RULE: record each fix in CHANGELOG.md under the heading '## Unreleased' as a bullet '- fix(<function name>): <short description>' (at least 3 bullets).` |
| data-learn | `rule_money_in_cents` | E | `RULE: money values in answer.json are integer cents (1606.67 USD is written 160667).` |
| data-learn | `rule_meta_block` | E | `RULE: answer.json has an object 'meta' = {"source": <input file name>, "rows_in": <number of data rows in the input file, duplicates included>, "rows_used": <numb...` |
| data-learn | `rule_clean_csv` | E | `RULE: write workspace/clean.csv with the header order_id,timestamp_utc,region,amount_cents; one row per distinct order with a known amount; timestamp_utc as YYYY-...` |
| logs-learn | `rule_service_names` | E | `RULE: service names in the output are lower-case with '-' replaced by '_' (payment-service -> payment_service).` |
| logs-learn | `rule_sorted_errors` | E | `RULE: 'errors' is sorted by service, then by timestamp_utc, ascending.` |
| logs-learn | `rule_schema_header` | E | `RULE: the top-level object has "schema_version": 2 and "generated_by": "log-triage".` |

Cả 9 check thất bại đều thuộc nhóm E: quy ước tổ chức có tiền tố `rule_` và feedback `RULE:`. Baseline learning đạt 18/18 check kỹ thuật, là bằng chứng phủ định đối với việc các nhóm A–D chiếm đa số trong bộ dữ liệu này; không khẳng định mọi hành vi trung gian đều hoàn hảo. Không dùng lỗi API hoặc recursion để phân loại năng lực tác tử. Quy ước ẩn không được nêu đủ trong đề nên đọc lại đề chưa đủ; curator nhận feedback mới có cơ hội đưa chúng vào context.

## 5. Điều kiện subagents

Ba vai trò tự định nghĩa: explorer đọc đặc tả và báo cáo; implementer sửa và kiểm tra; reviewer kiểm tra độc lập. Description nói khi nào gọi, system prompt giới hạn phạm vi; builder nối PATHS_NOTE vào từng subagent.

| Tác vụ | subagent_calls | Tên thấy trong trace | Token subagents | Token baseline |
|---|---|---|---|---|
| code-learn | 3 | explorer × 1, general-purpose × 1, implementer × 1 | 256,674 | 159,122 |
| data-learn | 3 | general-purpose × 3 | 955,735 | 210,111 |
| logs-learn | 0 | Không gọi | 93,017 | 108,246 |
| code-eval | 1 | reviewer × 1 | 175,666 | 145,244 |
| data-eval | 1 | general-purpose × 1 | 263,896 | 93,362 |
| logs-eval | 2 | implementer × 1; 1 lượt không còn tên trong đoạn trace bị cắt | 401,053 | 78,332 |

- Code learning giao khảo sát cho explorer rồi general-purpose, sau đó nhờ implementer thêm kiểm tra; tác tử chính chạy lại pytest. Code eval giao reviewer kiểm tra docstring/edge cases và chạy lại pytest sau báo cáo.
- Data learning giao general-purpose phân tích lại cùng tệp ba lần; check kỹ thuật `north_q1_orders` vẫn sai (feedback: got 13). Lời giao việc nêu loại giá trị thiếu ra revenue nhưng chưa ràng buộc rõ số lượng chỉ gồm order được tính vào revenue; lượt giao việc sau lại khá chung. Đây là dấu hiệu có thể mất một ràng buộc khi chuyển ngữ cảnh. Data eval giao một lần, nêu dedupe, UTC, giá trị thiếu và các khóa kết quả. Đây là bằng chứng về công việc lặp lại có thể làm tăng token; không thấy các bước bên trong worker để quy toàn bộ chi phí cho một nguyên nhân.
- Logs learning không giao việc: tác tử chính tự phân tích bằng shell. Logs eval có hai lượt, trong đó implementer được yêu cầu tạo parser và lượt sau sửa cấu trúc sau khi tác tử chính đối chiếu báo cáo. Trace cắt mỗi đoạn ở 1,500 ký tự nên tên lượt thứ hai không được giữ lại.
- Learning mean tokens: baseline 159,159, subagents 435,142 (2.73 lần). Eval mean tokens: baseline 105,646, subagents 280,205 (2.65 lần). Điểm subagents learning thấp hơn baseline ở data; cả ba điểm eval bằng baseline.

Data dùng general-purpose mặc định thay vì ba vai trò mới; điều kiện subagents còn thêm SUBAGENTS_NOTE khuyến khích giao việc. Vì vậy số đo phản ánh cả prompt và hành vi chọn worker, chưa tách được tác dụng của riêng các vai trò tự định nghĩa.

## 6. Self-evolving và chất lượng skill

Curator chạy một lần từ baseline learning, tạo ba skill hợp lệ; không xóa, không sửa tay, không chạy lại sau khi biết eval. Mô hình và trọng số không được huấn luyện lại; tiến hóa ở lớp context qua SKILL.md. Curator loại run có role khác learn, đưa tên check/detail và đoạn cuối trace vào prompt; validator chặn tên đường dẫn không an toàn và marker eval.

| Skill | Tính tổng quát | Đúng và còn thiếu gì | Độ dài và description |
|---|---|---|---|
| enforce-type-hints-and-tests | Dùng cho sửa Python, giữ được quy trình annotate/test/changelog | Hướng dẫn type hints rõ; test/changelog thiếu tên tệp và định dạng bullet chính xác của quy ước | 7 dòng; kích hoạt khi viết/sửa Python |
| format-financial-data-in-cents | Dùng cho phân tích và xuất tiền tệ | Chuyển sang cents phù hợp dữ liệu USD; metadata/clean dataset chỉ được nhắc chung, thiếu schema và cách làm tròn | 6 dòng; kích hoạt khi xử lý hoặc xuất giá trị tiền |
| normalize-identifiers-and-sort-logs | Dùng cho log có tên dịch vụ và UTC timestamp | Có chuẩn hóa tên và sắp xếp; thiếu schema header và thông tin dòng nguồn | 6 dòng; kích hoạt khi xử lý log/sự kiện |

Phát triển: data-learn đọc 3 skill và đạt 5/8; logs-learn đọc 1 skill và đạt 8/9. Code-learn chạm GraphRecursionError ở 60: record ghi skills_read=0 và trace rỗng do harness không giữ messages khi invoke lỗi; không suy ra agent thực sự không đọc skill.

| Run chính thức | skills_read (skill khác nhau) | subagent_calls | Điểm |
|---|---|---|---|
| code-learn | 3 | 0 | 8/10 |
| data-learn | 3 | 0 | 6/8 |
| logs-learn | 3 | 0 | 6/9 |
| code-eval | 1 | 0 | 8/11 |
| data-eval | 3 | 0 | 6/9 |
| logs-eval | 1 | 0 | 8/10 |

Đọc skill không đảm bảo thực hiện hết. Code learning chính thức đạt type hints nhưng ghi `tests/test_regression.py` thay vì `tests/test_regressions.py`, và bullet changelog bắt đầu `- Fixed` thay vì cấu trúc `- fix(<function>):`; hai check vẫn thất bại dù agent có tạo test/changelog. Data learning chính thức chuyển tiền sang cents nhưng thiếu metadata/clean.csv. Logs learning chính thức đọc ba skill nhưng vẫn trượt chuẩn hóa tên và sắp xếp; kết quả khác lần phát triển dù skill không đổi.

## 7. Kết quả chính thức

Bảng dưới đây là nội dung `report/table.md`, sinh bằng `python -m lab.compare`. Mọi run trong ba thư mục điều kiện chính có error=null và skills_modified=false; lỗi quota cũ nằm riêng trong `results/failed-attempts-20261007/`, development nằm ở `results/skills-auto-dev/` và không được lab.compare đưa vào bảng.

| Task | baseline | subagents | skills-auto |
|---|---|---|---|
| code-learn | 7/10 | 7/10 | 8/10 |
| data-learn | 5/8 | 4/8 | 6/8 |
| logs-learn | 6/9 | 6/9 | 6/9 |
| code-eval | 7/11 | 7/11 | 8/11 |
| data-eval | 5/9 | 5/9 | 6/9 |
| logs-eval | 6/10 | 6/10 | 8/10 |
| **Mean score - learning tasks** | 0.66 | 0.62 | 0.74 |
| **Mean score - evaluation tasks** | 0.60 | 0.60 | 0.73 |
| **Mean tokens per run** | 132,402 | 357,673 | 181,528 |
| **Runs that read a skill** | 0/6 | 0/6 | 6/6 |

Thống kê từ `scripts/check_breakdown.py`:

```text
condition     role    technical  house rules  mean tokens  read a skill
baseline      eval     18/18         0/12         105,646      0/3
baseline      learn    18/18         0/9          159,159      0/3
subagents     eval     18/18         0/12         280,205      0/3
subagents     learn    17/18         0/9          435,142      0/3
skills-auto   eval     18/18         4/12         165,165      3/3
skills-auto   learn    18/18         2/9          197,891      3/3
```

`verify_freeze.py`: `checked 6 runs of skill conditions: OK`. Mỗi run skills-auto chính thức bắt đầu sau freeze, ghi hash đúng skill đã đóng băng và không sửa skill. Tệp starter, tests, tasks và scripts không bị sửa; 32 offline tests đạt.

## 8. Phân tích

1. **Điểm theo vai trò.** Learning: baseline 0.664; subagents 0.622; skills-auto 0.739. Eval: baseline 0.597; subagents 0.597; skills-auto 0.731. Skills-auto so với baseline thay đổi trung bình learning +0.075, eval +0.134. H1 phù hợp số liệu eval: subagents bằng baseline và tốn nhiều token hơn. Mức trung bình eval cao hơn baseline, nên phần dự đoán không tăng điểm tổng trong H2 không khớp số đo; một lần chạy mỗi tác vụ chưa đủ chứng minh cải thiện ổn định. H3 phù hợp với mean score ở ba điều kiện, nhưng skills-auto chỉ chênh learning/eval khoảng 0.008; riêng logs có eval 8/10 cao hơn learning 6/9. Khoảng chênh nhỏ hơn dao động ở các repeat, và mỗi eval thêm một quy ước, nên không suy ra quá khớp chỉ từ điểm tổng.
2. **Kỹ thuật và quy ước.** Dùng breakdown trên để tách hai nhóm. Baseline learning đạt toàn bộ 18 check kỹ thuật và không đạt 9 convention checks; eval đạt 18 kỹ thuật và không đạt 12 convention checks. Skill đem lại lợi ích quan sát được ở một số convention cũ, như type hints và integer cents, trong khi các quy ước mới có kết quả sau:

| Eval | Quy ước mới so với learning cùng họ | Kết quả skills-auto | Nội dung skill |
|---|---|---|---|
| code-eval | `rule_version_bump` | Không đạt | Không được nêu trong ba skill đã đóng băng |
| data-eval | `rule_sorted_keys_format` | Không đạt | Không được nêu trong ba skill đã đóng băng |
| logs-eval | `rule_source_line` | Không đạt | Không được nêu trong ba skill đã đóng băng |

Cả ba quy ước mới đều không đạt và không được mô tả trong skill. Những cải thiện quan sát được chuyển giao các quy ước đã có ở learning, chưa cho thấy khả năng suy ra một quy ước tổ chức mới.

3. **Cơ chế từ trace.** Code-learn đọc skill trước khi sửa, viết type annotations và đạt rule_type_hints (baseline không đạt); hành vi phù hợp hướng dẫn skill. Cùng trace cho thấy tên regression file và bullet changelog không đúng chuẩn: skill thiếu chi tiết, không phải hoàn toàn không viết test/changelog. Logs-learn trượt rule_service_names và rule_sorted_errors dù đọc skill có hai hướng dẫn đó, cho thấy có cả trường hợp đọc nhưng không áp dụng. Những liên hệ này không chứng minh nhân quả với chỉ một lần chạy.
4. **Chi phí.** Token là tổng cộng dồn qua các call, gồm worker, không phải độ dài một prompt. Thước đo thô dưới đây chia mean normalized task score cho mean tokens và nhân 100,000; không phải tỷ lệ tác vụ đạt toàn bộ.

| Điều kiện | Mean score (6 tác vụ) | Mean tokens | Mean score / 100,000 tokens |
|---|---|---|---|
| baseline | 0.631 | 132,402 | 0.476 |
| subagents | 0.610 | 357,673 | 0.170 |
| skills-auto | 0.735 | 181,528 | 0.405 |

`baseline` có điểm/token cao nhất theo thước đo này. Subagents không tăng điểm eval, giảm mean learning và tăng token, nên chi phí chưa được bù bằng chất lượng trong thí nghiệm này. Pacing làm thay đổi seconds; không dùng thời gian giữa ngày/điều kiện để suy ra tăng tốc.

5. **Overfitting và leakage.** Skill chỉ dùng feedback learning, không chứa marker eval và không thay đổi sau freeze. Nội dung còn gần quy ước của tác vụ học và bỏ các chi tiết cần cho quy ước mới. Điểm trung bình tăng cả ở learning (+0.075) và eval (+0.134), nên không quan sát mẫu chỉ cải thiện learning. Việc thất bại cả ba quy ước mới cho thấy độ phủ hạn chế; số mẫu và các repeat chưa đủ để kết luận mức quá khớp. Không có bằng chứng trong skill cho việc chép đáp án eval.
6. **Nhiễu khi skill giữ nguyên.** So sánh các bản ghi phát triển đã sao lưu với các run chính thức:

| Tác vụ học | Development | Sau freeze | Thay đổi normalized score |
|---|---|---|---|
| code-learn | 7/10 (GraphRecursionError) | 8/10 | Không ước lượng: run phát triển bị lỗi |
| data-learn | 5/8 | 6/8 | +0.125 (+12.5 điểm phần trăm) |
| logs-learn | 8/9 | 6/9 | -0.222 (-22.2 điểm phần trăm) |

Data/logs dao động ở mức một đến hai check, tương đương hoặc lớn hơn một số chênh lệch giữa điều kiện. Do đó không diễn giải mọi mức tăng như hiệu quả học. Đây là ước lượng độ biến thiên hạn chế: model/skill giữ nguyên nhưng key/ngày, pacing và recursion cap khác; code development lỗi nên không là cặp đo nhiễu hợp lệ.

## 9. Hạn chế và tính hợp lệ

1. Chỉ ba họ tác vụ, mỗi vai trò ba task và một official run mỗi cấu hình: không ước lượng được khoảng tin cậy hoặc khái quát rộng.
2. Một mô hình Gemini với sampling cố định; kết luận gắn với mô hình và harness này, cần lặp hoặc đổi mô hình để kiểm tra độ bền.
3. Recursion cap 40/60/100 và pacing khác giữa các giai đoạn; ngân sách chạy là yếu tố gây nhiễu, thời gian không so sánh trực tiếp được.
4. Checker và quy ước ẩn do giảng viên thiết kế; phần tăng điểm có thể là học convention hơn là cải thiện năng lực lập trình/phân tích nói chung.
5. Trace chỉ có luồng chính và bị cắt mỗi đoạn; run lỗi invoke không có trace/skill-read đáng tin. Không thấy đầy đủ chi phí và hành vi bên trong subagent.
6. Hai cặp repeat data/logs đã dao động, code development lỗi; chưa đủ để tách nhiễu, tác động skill và khác biệt yêu cầu eval.

## 10. Kết luận

Baseline đã giải quyết các check kỹ thuật nhưng bỏ sót quy ước ẩn. Skills-auto có thay đổi điểm trung bình learning +0.075 và eval +0.134 so với baseline, nhưng các repeat cho thấy biến thiên đáng kể. Subagents không tăng điểm eval và tăng chi phí token. Bước tiếp theo là lặp các điều kiện với cùng cap/pacing để đo khoảng dao động và kiểm tra khả năng chuyển giao của skill.

## Phụ lục: tái lập và lịch sử

- Đã hoàn thành phần bắt buộc 0–5; không thực hiện phần thưởng 6.
- Hypotheses commit trước freeze; curator không được chạy lại sau eval. Skill library giữ nguyên từ tag.
- Lỗi trước đây: code learning phát triển chạm cap 40/60; Google trả quota theo phút/ngày. Hai quota eval records được sao lưu trước khi chạy lại với key mới, không trộn vào so sánh chính.
- Các lần baseline/subagents ban đầu dùng CLI; skills-auto development được sao lưu bằng `mv results/skills-auto results/skills-auto-dev` trước official run.

Lệnh offline và tạo bảng/kiểm tra:

```bash
python3 -m venv .venv
.venv/bin/pip install -e .
.venv/bin/pytest
.venv/bin/python scripts/tour.py
.venv/bin/python -m lab.compare > report/table.md
.venv/bin/python scripts/check_breakdown.py
.venv/bin/python scripts/verify_freeze.py
```

Thứ tự run trước freeze: baseline data-learn (60), code-learn/logs-learn (40), code-learn retry (60); subagents learn (60); curator; skills-auto learn (40), code/data retry (60), code retry (60). Commit hypotheses rồi commit/tag freeze. Sau freeze: baseline eval (60), subagents eval (60), rồi tiếp tục ngày 07/10/2026 bằng lời gọi dưới đây. Các run dưới đây được gọi tuần tự, không đổi prompt hoặc skill:

```python
from langchain_core.rate_limiters import InMemoryRateLimiter
from lab.model import make_model
from lab.runner import run_task

model = make_model()
model.rate_limiter = InMemoryRateLimiter(
    requests_per_second=0.2, max_bucket_size=1
)
for task in ("data-eval", "logs-eval"):
    run_task(task, "subagents", model=model, recursion_limit=60)
for task in (
    "code-learn", "data-learn", "logs-learn",
    "code-eval", "data-eval", "logs-eval",
):
    run_task(task, "skills-auto", model=model, recursion_limit=100)
```

Đặt cấu hình/key trong `.env` đã được Git ignore. Có thể truyền results_dir khác khi lặp để giữ lại run cũ. Mã curator được chỉnh expression dựng prompt để tương thích cú pháp Python 3.11; không tạo lại skill từ sửa đổi đó. Xem `git log --oneline` để đối chiếu các commit ở từng checkpoint.

Tài liệu: [SkillsBench](https://arxiv.org/abs/2602.12670); [SkillEvolBench](https://arxiv.org/abs/2605.24117). Hai nghiên cứu đặt giả thuyết về hiệu quả và khả năng chuyển giao; không dùng số đo của chúng làm số liệu của lab.
