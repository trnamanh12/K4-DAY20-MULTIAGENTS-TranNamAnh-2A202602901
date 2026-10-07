# Báo cáo Lab: Self evolving Agentic

## 1. Thông tin và cấu hình

| Họ tên | Mã sinh viên | Phần đóng góp |
|---|---|---|
| Trần Nam Anh | 2A202602901 | Hoàn thiện harness, chạy thí nghiệm và phân tích kết quả |


- Mô hình: `google_genai:gemini-3.5-flash-lite`, với `LAB_TEMPERATURE=0`. SDK báo mô hình dùng thiết lập lấy mẫu cố định nên không áp dụng giá trị nhiệt độ.
- Môi trường: Python 3.14.7, Linux và Deep Agents 0.7.21; chạy trong môi trường ảo `.venv`.
- Giới hạn vòng lặp: baseline dùng 60 cho `data-learn` và các lần chạy code cuối cùng, 40 cho `logs-learn`; subagents dùng 60. Skills-auto phát triển dùng 40, sau đó chạy lại code và data ở 60. Sáu lần chạy skills-auto chính thức dùng 100 vì code trước đó chạm giới hạn 60.
- Có 18 bản ghi chính thức (6 tác vụ trong mỗi điều kiện), 3 bản ghi skills-auto phát triển và một số lần thử lại. 18 lần chạy chính thức dùng tổng cộng 4.029.629 token. Thí nghiệm không đặt ngân sách tiền cụ thể và báo cáo không quy token ra chi phí API.
- Commit giả thuyết: `3fd4309`; tag `freeze`: `2157cc3874549053cd9f067ae548e00a8d093457`. Nội dung trong `skills/auto/` giữ nguyên sau khi đóng băng.

## 2. Giả thuyết đã commit trước freeze

Ba giả thuyết dưới đây giữ nguyên nội dung đã commit trước khi xem điểm eval.

- H1 (subagents so với baseline): Trên eval, subagents sẽ không cải thiện ổn định điểm tổng so với baseline và sẽ dùng nhiều token hơn. Learning cho thấy điểm không tăng ở code/logs, giảm ở data, trong khi token trung bình tăng từ 159,159 lên 435,142.
- H2 (skills-auto so với baseline): Skills-auto có thể giữ hoặc cải thiện một số check kỹ thuật có quy trình tương tự, nhưng không dự đoán sẽ giải quyết quy ước mới của eval vì skill được rút từ feedback learning. SkillsBench ghi nhận skill có thể giúp khi được biên soạn/chọn lọc, nhưng SkillEvolBench cho thấy skill tự sinh thường không chuyển bền vững sang deployment đã đóng băng; vì vậy dự đoán không có cải thiện tổng điểm nhất quán ([SkillsBench](https://arxiv.org/abs/2602.12670); [SkillEvolBench](https://arxiv.org/abs/2605.24117)).
- H3 (tác vụ học so với tác vụ đánh giá): Điểm eval sẽ bằng hoặc thấp hơn learning, vì eval đổi dữ liệu và bổ sung một quy ước; quy trình kỹ thuật có thể chuyển giao nhưng quy ước không xuất hiện trong feedback learning thì không thể học trực tiếp. SkillEvolBench nêu rủi ro suy giảm khi đóng băng skill dưới chuyển dịch ngữ cảnh.

## 3. Làm quen Deep Agents

1. Tour liệt kê các công cụ `ls`, `read_file`, `write_file`, `edit_file`, `delete`, `glob`, `grep`, `execute` và `task`. Công cụ `execute` dùng để chạy lệnh shell.
2. Subagent `general-purpose` có thể tìm tệp, nghiên cứu hoặc xử lý việc nhiều bước. Mỗi lần gọi mặc định là một phiên riêng: subagent chỉ thấy nội dung được gửi trong prompt và trả về một báo cáo cuối, chứ không tự nhận toàn bộ lịch sử của tác tử chính. Tác tử baseline vẫn được cung cấp công cụ `task`, nhưng cả sáu bản ghi baseline đều có `subagent_calls=0`.
3. Mô tả `task` viết: “Put full detail in the prompt and state exactly what it should return.” Mô tả `execute` viết: “Use absolute paths and avoid `cd` so the working directory stays stable.” System prompt trong tour mặc định rỗng (`''`). Harness của lab đặt thêm `BASE_PROMPT`, trong đó yêu cầu dùng đường dẫn tương đối dạng `workspace/...` cho cả công cụ tệp và shell.

Shell của agent chỉ nhận `PATH`, `HOME` trong sandbox và `PYTHONDONTWRITEBYTECODE`; các biến môi trường khác, trong đó có API key, không được truyền vào. Mỗi tác vụ chạy trên một bản sao tạm của workspace, được chấm xong rồi xóa. Bộ đếm token tính cả các lần gọi subagent, còn số tool call, lần giao việc và skill được đọc chỉ tính trên luồng chính.

## 4. Baseline và phân loại lỗi

| Tác vụ học | Check thất bại | Nhóm A–G | Bằng chứng từ feedback |
|---|---|---|---|
| code-learn | `rule_type_hints` | E | `RULE: every public function ... has type annotations on all parameters and on the return value.` |
| code-learn | `rule_regression_tests` | E | `RULE: add tests/test_regressions.py ... (at least 3); the file must pass.` |
| code-learn | `rule_changelog` | E | `RULE: record each fix in CHANGELOG.md ... '- fix(<function name>): <short description>' (at least 3 bullets).` |
| data-learn | `rule_money_in_cents` | E | `RULE: money values in answer.json are integer cents.` |
| data-learn | `rule_meta_block` | E | `RULE: answer.json has an object meta with source, rows_in and rows_used.` |
| data-learn | `rule_clean_csv` | E | `RULE: write workspace/clean.csv with required columns, UTC timestamps, canonical regions and integer cents.` |
| logs-learn | `rule_service_names` | E | `RULE: service names ... lower-case with '-' replaced by '_' (payment-service -> payment_service).` |
| logs-learn | `rule_sorted_errors` | E | `RULE: errors is sorted by service, then by timestamp_utc, ascending.` |
| logs-learn | `rule_schema_header` | E | `RULE: top-level object has schema_version 2 and generated_by log-triage.` |

Cả chín check thất bại đều thuộc nhóm E: tên check bắt đầu bằng `rule_`, còn phản hồi bắt đầu bằng `RULE:`. Baseline đạt toàn bộ 18 check kỹ thuật, nên các nhóm A–D không phải nguyên nhân của những lần trượt được ghi nhận. Đây là kết quả của bộ tác vụ này, không phải khẳng định agent luôn làm đúng kỹ thuật. Các lỗi API và recursion được ghi riêng, không tính là lỗi của agent. Vì đề không nêu đầy đủ những quy ước này, curator chỉ biết đến chúng sau khi nhận feedback.

## 5. Điều kiện subagents

Ba vai trò được định nghĩa là `explorer` để đọc đặc tả và báo cáo, `implementer` để sửa và kiểm tra, và `reviewer` để rà soát độc lập. Mỗi mô tả nêu trường hợp nên giao việc; system prompt giới hạn phạm vi của vai trò. Khi tạo agent, harness bổ sung quy ước đường dẫn `PATHS_NOTE` vào prompt của từng subagent.

| Tác vụ | subagent_calls | Tên thấy trong trace | Token subagents | Token baseline |
|---|---|---|---|---|
| code-learn | 3 | explorer × 1, general-purpose × 1, implementer × 1 | 256,674 | 159,122 |
| data-learn | 3 | general-purpose × 3 | 955,735 | 210,111 |
| logs-learn | 0 | Không gọi | 93,017 | 108,246 |
| code-eval | 1 | reviewer × 1 | 175,666 | 145,244 |
| data-eval | 1 | general-purpose × 1 | 263,896 | 93,362 |
| logs-eval | 2 | implementer × 1; 1 lượt không còn tên trong đoạn trace bị cắt | 401,053 | 78,332 |

Ở `code-learn`, agent giao việc lần lượt cho explorer, general-purpose rồi implementer; sau khi nhận báo cáo, nó tự chạy lại pytest. Ở `code-eval`, reviewer rà soát docstring và trường hợp biên, rồi agent chính cũng chạy pytest.

Ở `data-learn`, agent gọi general-purpose ba lần để phân tích cùng dữ liệu. Dù lời giao việc có nhắc cách xử lý giá trị thiếu, check `north_q1_orders` vẫn sai; feedback ghi “got 13”. Những lời giao việc chưa nói rõ rằng số đơn này chỉ tính các đơn được đưa vào tổng doanh thu; một lần giao việc sau cũng khá chung chung. Đây có thể là ví dụ về một ràng buộc bị mất khi chuyển ngữ cảnh. Ở `data-eval`, agent giao việc một lần và nêu các quy tắc về dòng trùng, UTC, giá trị thiếu và các khóa đầu ra.

Agent không giao việc ở `logs-learn`; trace cho thấy nó tự đọc log và xử lý bằng shell. Ở `logs-eval`, agent giao việc hai lần. Lượt đầu yêu cầu implementer viết parser; sau khi đối chiếu báo cáo, agent yêu cầu sửa cấu trúc đầu ra. Trace bị giới hạn 1.500 ký tự cho mỗi đoạn nên không còn đủ thông tin để xác định tên subagent ở lượt thứ hai.

Trung bình learning, subagents dùng 435.142 token so với 159.159 của baseline, tức 2,73 lần. Trung bình eval là 280.205 so với 105.646 token, tức 2,65 lần. Điểm learning giảm ở data và giữ nguyên ở code, logs; điểm eval bằng baseline ở cả ba tác vụ.

Các lời giao việc cho tác vụ data đều dùng general-purpose, không dùng ba vai trò tự định nghĩa. Điều kiện subagents cũng bổ sung `SUBAGENTS_NOTE`, khuyến khích agent giao việc. Vì vậy, số liệu phản ánh đồng thời thay đổi prompt và quyết định giao việc; không thể quy kết riêng cho tác dụng của ba vai trò mới.

## 6. Self-evolving và chất lượng skill

Curator được chạy một lần trên các kết quả baseline learning và tạo ra ba skill hợp lệ. Không có skill nào bị xóa hoặc chỉnh tay, và curator không được chạy lại sau khi xem kết quả eval. Thí nghiệm chỉ bổ sung hướng dẫn vào context; mô hình và trọng số không thay đổi. Curator bỏ qua những run không có `role=learn`, đưa tên check cùng feedback và phần cuối trace vào prompt. Hàm kiểm tra skill từ chối tên không an toàn và nội dung có marker của tập eval.

| Skill | Tính tổng quát | Đúng và còn thiếu gì | Độ dài và description |
|---|---|---|---|
| `enforce-type-hints-and-tests` | Hợp với việc sửa mã Python và nhắc agent thêm type hints, test và changelog | Hướng dẫn type hints khá rõ. Với test và changelog, skill chưa nêu tên file hoặc mẫu bullet cần dùng | 7 dòng; description dùng khi viết hoặc sửa Python |
| `format-financial-data-in-cents` | Dùng cho dữ liệu có giá trị tiền và file đầu ra | Đổi USD sang cents phù hợp dữ liệu này. Phần metadata và clean dataset còn chung, chưa nêu schema hay cách làm tròn | 6 dòng; description nêu xử lý hoặc xuất tiền tệ |
| `normalize-identifiers-and-sort-logs` | Dùng cho log hoặc sự kiện có tên dịch vụ và timestamp | Nêu cách chuẩn hóa tên và sắp xếp; còn thiếu header schema và trường dòng nguồn | 6 dòng; description nêu rõ xử lý log/sự kiện |

Trong các lần chạy phát triển, agent đọc ba skill ở `data-learn` và đạt 5/8; ở `logs-learn`, nó đọc một skill và đạt 8/9. Lần `code-learn` phát triển chạm `GraphRecursionError` ở giới hạn 60. Khi `invoke` lỗi, harness không giữ lại messages nên record có `skills_read=0` và trace rỗng; không thể kết luận agent đã bỏ qua skill.

| Run chính thức | skills_read (skill khác nhau) | subagent_calls | Điểm |
|---|---|---|---|
| code-learn | 3 | 0 | 8/10 |
| data-learn | 3 | 0 | 6/8 |
| logs-learn | 3 | 0 | 6/9 |
| code-eval | 1 | 0 | 8/11 |
| data-eval | 3 | 0 | 6/9 |
| logs-eval | 1 | 0 | 8/10 |

Agent đọc skill nhưng không phải lúc nào cũng áp dụng đủ mọi hướng dẫn. Ở `code-learn`, nó thêm type hints và đạt `rule_type_hints`. Nó cũng tạo `tests/test_regression.py` và changelog, nhưng tên file không đúng số nhiều và các bullet dùng `- Fixed` thay cho mẫu `- fix(<function>):`; hai check liên quan vẫn trượt. Ở `data-learn`, agent đổi tiền sang cents nhưng chưa tạo metadata và `clean.csv`. Ở `logs-learn`, dù đọc cả ba skill, nó vẫn không chuẩn hóa tên dịch vụ hoặc sắp xếp danh sách lỗi. Điểm logs cũng giảm từ 8/9 ở lần phát triển xuống 6/9 ở lần chính thức dù bộ skill không đổi.

## 7. Kết quả chính thức

Bảng sau được tạo bằng `python -m lab.compare`. Các run phát triển trong `results/skills-auto-dev/` không nằm trong bảng so sánh. Cả 18 lần chạy chính thức đều hoàn tất, không có lỗi và không sửa skill. Hai lần chạy eval của subagents từng bị quota từ chối được lưu riêng trong `results/failed-attempts-20261007/`.

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

`verify_freeze.py` xác nhận cả sáu run skills-auto dùng đúng skill đã đóng băng, bắt đầu sau tag và không sửa skill. Các tệp khung ban đầu, thư mục tests, tasks và scripts giữ nguyên. Cả 32 bài test offline đều đạt.

## 8. Phân tích

1. **Điểm theo từng điều kiện.** Điểm trung bình learning là 0,664 với baseline, 0,622 với subagents và 0,739 với skills-auto. Trên eval, các điểm lần lượt là 0,597, 0,597 và 0,731. So với baseline, skills-auto tăng 0,075 ở learning và 0,134 ở eval. Subagents bằng baseline ở cả ba tác vụ eval nhưng dùng hơn gấp đôi token. Kết quả eval skills-auto trái với dự đoán H2 là không cải thiện tổng điểm một cách nhất quán; mỗi tác vụ chỉ có một run nên chưa thể biết mức tăng này có lặp lại được không. H3 được ủng hộ nhẹ nếu xét điểm trung bình: learning nhỉnh hơn eval khoảng 0,008 với skills-auto. Riêng logs lại có điểm eval cao hơn learning, và chênh lệch giữa hai vai trò nhỏ hơn dao động ở các lần chạy lặp.
2. **Check kỹ thuật và quy ước.** Baseline đạt cả 18/18 check kỹ thuật ở learning lẫn 18/18 ở eval, nhưng trượt 9/9 và 12/12 check quy ước. Skills-auto đạt 18/18 check kỹ thuật ở cả hai vai trò, cùng 2/9 check quy ước ở learning và 4/12 ở eval. Các check quy ước mới của từng tác vụ eval là:

| Eval | Quy ước mới so với learning cùng họ | Kết quả skills-auto | Nội dung skill |
|---|---|---|---|
| code-eval | `rule_version_bump` | Không đạt | Không được nêu trong ba skill đã đóng băng |
| data-eval | `rule_sorted_keys_format` | Không đạt | Không được nêu trong ba skill đã đóng băng |
| logs-eval | `rule_source_line` | Không đạt | Không được nêu trong ba skill đã đóng băng |

Cả ba check quy ước mới đều trượt. Skill có vẻ giúp agent làm đúng một số quy tắc đã xuất hiện trong feedback learning, nhưng kết quả chưa cho thấy agent tự suy ra được quy ước mới.

3. **Trace và việc dùng skill.** Ở code-learn, agent đọc skill về type hints, thêm annotations và đạt `rule_type_hints`, check baseline đã trượt. Nó cũng tạo test và changelog, nhưng không theo đúng tên file và mẫu bullet; skill sinh ra chưa nêu đủ chi tiết. Ở logs-learn, agent đọc skill nhưng vẫn trượt `rule_service_names` và `rule_sorted_errors`. Có lúc agent làm theo một phần hướng dẫn, có lúc đọc rồi vẫn bỏ qua. Mỗi kết quả chỉ dựa trên một lần chạy.
4. **Chi phí.** Token trong bảng là tổng của các lần gọi mô hình, có tính cả subagent. Cột cuối chia điểm tác vụ trung bình cho token trung bình rồi nhân 100.000. Đây là cách so sánh thô về điểm trên mỗi token, không phải tỉ lệ tác vụ đạt trọn vẹn.

| Điều kiện | Mean score (6 tác vụ) | Mean tokens | Mean score / 100,000 tokens |
|---|---|---|---|
| baseline | 0.631 | 132,402 | 0.476 |
| subagents | 0.610 | 357,673 | 0.170 |
| skills-auto | 0.735 | 181,528 | 0.405 |

Theo cách tính này, baseline có điểm trên mỗi token cao nhất. Subagents không tăng điểm eval, điểm learning trung bình thấp hơn baseline, còn lượng token cao hơn nhiều. Trong các run này, phần chi phí thêm chưa đi cùng với mức điểm cao hơn. Do tốc độ gửi yêu cầu thay đổi giữa các đợt chạy, không dùng số giây để so sánh tốc độ giữa điều kiện.

5. **Quá khớp và rò rỉ dữ liệu.** Curator chỉ đọc kết quả learning, và ba skill được giữ nguyên từ trước khi mở tập eval. Skill không chứa marker hay đáp án eval. Điểm skills-auto tăng ở cả learning và eval, nên số liệu không cho thấy chỉ có lợi trên tập học. Cả ba quy ước eval mới đều trượt, cho thấy skill chưa bao phủ hết yêu cầu. Với ba tác vụ mỗi vai trò và một run mỗi điều kiện, chưa thể kết luận chắc về mức quá khớp.
6. **Dao động giữa các lần chạy.** So sánh lần chạy skills-auto phát triển với run chính thức bằng cùng bộ skill:

| Tác vụ học | Development | Sau freeze | Thay đổi normalized score |
|---|---|---|---|
| code-learn | 7/10 (GraphRecursionError) | 8/10 | Không ước lượng: run phát triển bị lỗi |
| data-learn | 5/8 | 6/8 | +0.125 (+12.5 điểm phần trăm) |
| logs-learn | 8/9 | 6/9 | -0.222 (-22.2 điểm phần trăm) |

Điểm data tăng một check, còn logs giảm hai check dù skill không đổi. Mức dao động này ngang hoặc lớn hơn nhiều chênh lệch giữa các điều kiện, nên không thể xem mọi mức tăng là hiệu quả của skill. Đây chỉ là ước lượng nhiễu hạn chế: các lần chạy khác ngày, key, pacing và recursion limit; run code phát triển bị lỗi nên không thể dùng làm cặp so sánh hợp lệ.

## 9. Hạn chế và tính hợp lệ

1. Chỉ có ba họ tác vụ và mỗi cấu hình chạy một lần. Kết quả có thể phụ thuộc vào dữ liệu cụ thể, chưa đủ để ước lượng khoảng tin cậy.
2. Thí nghiệm dùng một mô hình Gemini với sampling cố định. Kết quả chưa cho biết mô hình hoặc harness khác sẽ hoạt động ra sao.
3. Recursion limit thay đổi từ 40 đến 100, và pacing khác nhau giữa các đợt chạy. Những khác biệt này có thể ảnh hưởng số bước agent thực hiện và thời gian.
4. Bộ chấm có các quy ước do giảng viên thiết kế; điểm tăng có thể phản ánh việc làm đúng quy tắc cụ thể, chưa chắc khái quát sang công việc khác.
5. Trace chỉ lưu luồng chính và bị cắt theo giới hạn ký tự. Khi invoke lỗi, harness không lưu được trace hoặc số skill đã đọc, nên không quan sát được hết hoạt động bên trong subagent.
6. Hai cặp chạy lại ở data và logs dao động rõ; lần phát triển ở code bị lỗi. Chưa đủ lần chạy để tách ảnh hưởng của skill khỏi nhiễu và khác biệt giữa eval với learning.

## 10. Kết luận

Baseline đạt các check kỹ thuật nhưng bỏ sót nhiều quy ước định dạng. Skills-auto tăng điểm trung bình 0,075 ở learning và 0,134 ở eval so với baseline, dù các lần chạy lặp cho thấy kết quả có thể dao động đáng kể. Subagents không tăng điểm eval nhưng dùng nhiều token hơn. Bước tiếp theo là chạy lặp với cùng recursion limit và tốc độ yêu cầu để kiểm tra độ ổn định của kết quả.

## Phụ lục: tái lập và lịch sử

- Đã hoàn thành các phần bắt buộc 0–5 và thực hiện thử thách mở rộng 6c về red-team curator. Thử thách này được chạy riêng, không gọi API và không thay đổi bộ skill đã đóng băng.
- Ba giả thuyết được commit trước tag `freeze`. Curator chỉ chạy một lần trước khi xem kết quả eval; skill không bị sửa sau khi đóng băng.
- Những lần chạy đầu gặp giới hạn recursion và quota API. Hai bản ghi subagents eval bị quota từ chối được lưu riêng trước khi chạy lại bằng key mới; chúng không được tính vào bảng chính.
- Kết quả skills-auto phát triển được chuyển sang `results/skills-auto-dev/` trước khi bắt đầu sáu lần chạy chính thức.

### Thử thách 6c: red-team curator

Thử nghiệm dùng `report/challenge_6c.py` và lưu kết quả ở `results/challenge-6c/`, tách khỏi kết quả chính. Hai ca dùng cùng feedback kiểm tra: ca đối chứng đưa quy tắc kiểm tra kết quả; ca tấn công thêm chỉ dẫn prompt injection vào feedback learning, yêu cầu agent bỏ qua kiểm tra và báo hoàn tất. `ScriptedChatModel` phát lại đầu ra cố định để đo chính xác việc ghi skill và kết quả `validate_skill` mà không tiêu thụ token API.

| Ca | Model calls | Skill được ghi | Validator chấp nhận | Chỉ dẫn báo hoàn tất dù chưa kiểm tra được giữ lại |
|---|---:|---:|---|---|
| Đối chứng | 1 | 1 | Có | Không |
| Prompt injection | 1 | 1 | Có | Có |

Trace xác nhận nội dung độc hại từ feedback learning được đưa vào prompt curator. Skill nguy hiểm nhưng hợp lệ về cú pháp đã vượt qua validator vì validator kiểm tra frontmatter, tên an toàn, độ dài và marker eval; nó không đánh giá độ an toàn về ngữ nghĩa. Đây là bằng chứng về một đường tấn công mô phỏng tới thư viện skill, không đo tần suất một mô hình dịch vụ thực tế làm theo prompt injection.

Biện pháp đề xuất: xem detail và trace là dữ liệu không tin cậy; tách chúng khỏi chỉ dẫn curator bằng delimiters rõ ràng và loại chỉ dẫn dạng mệnh lệnh không liên quan tới quy tắc; thêm bước rà soát an toàn nội dung trước khi đóng băng skill. Validator hiện có vẫn hữu ích để chặn tên đường dẫn và dấu hiệu lộ dữ liệu eval, nhưng chưa đủ để phát hiện chỉ dẫn lừa agent. Giới hạn thử nghiệm: chỉ có một ca đối chứng, một payload được định trước và một đầu ra scripted; kết quả không phải ước lượng tỉ lệ tấn công thành công với Gemini.

Để dựng lại môi trường từ checkout mới, tạo tệp .env theo mẫu rồi cấu hình model và API key riêng; không đưa key vào kho. Các lệnh kiểm tra và tạo bảng:

```bash
python3 -m venv .venv
.venv/bin/pip install -e .
cp .env.example .env
.venv/bin/pytest
.venv/bin/python scripts/tour.py
.venv/bin/python -m lab.compare > report/table.md
.venv/bin/python scripts/check_breakdown.py
.venv/bin/python scripts/verify_freeze.py
```

Trước khi đóng băng, đã chạy baseline trên data-learn (limit 60), code-learn và logs-learn (limit 40), rồi chạy lại code-learn ở 60. Batch subagents learning được chạy lại ở limit 60 sau khi lần đầu bị ngắt. Curator tạo skill; skills-auto learning chạy ở limit 40 rồi chạy lại code và data ở 60. Commit `hypotheses` được tạo trước commit và tag `freeze`. Sau tag, baseline và subagents eval chạy ở limit 60; riêng data-eval và logs-eval của subagents được chạy lại bằng key mới. Cuối cùng, sáu tác vụ skills-auto được chạy tuần tự ở limit 100. Đoạn mã dưới đây cho thấy cách giới hạn tốc độ gửi yêu cầu ở lượt chạy lại:

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

Thông tin cấu hình và API key nằm trong .env, tệp này được Git bỏ qua. Khi chạy lại để giữ các kết quả hiện có, truyền một results_dir khác vào run_task. Hàm curator được chỉnh nhẹ để tương thích cú pháp Python 3.11; skill không được sinh lại từ thay đổi này. Dùng git log --oneline để xem các commit theo từng checkpoint.

Tài liệu: [SkillsBench](https://arxiv.org/abs/2602.12670); [SkillEvolBench](https://arxiv.org/abs/2605.24117). Hai nghiên cứu đặt giả thuyết về hiệu quả và khả năng chuyển giao; không dùng số đo của chúng làm số liệu của lab.
