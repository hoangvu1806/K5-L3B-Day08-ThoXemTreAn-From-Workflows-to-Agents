# Research card

File này nằm cố định ở `report/team/research_card.md`; `python -m lab8.check_submission` đọc cột "Nhóm điền" bằng máy.

Phần này nối tiếp phần mini research ở buổi lý thuyết (slide 62–63). Chọn **một** câu R1–R4, điền 6 dòng, rồi biến nó thành **một ablation** chạy được trong lab: giữ nguyên model (MockLLM), tool, seed, corpus và giá, chỉ thay đổi một biến.

| Câu | Nguồn (thư viện tham khảo, slide 68–69) | Câu hỏi gợi ý cho lab |
| --- | --- | --- |
| R1 · Scaling | Google Research 2026, *Towards a Science of Scaling Agent Systems* | Task claims chủ yếu tuần tự hay song song được? Dự đoán thêm investigator sẽ làm pass rate và cost/success thay đổi thế nào. |
| R2 · Failure taxonomy | MAST, NeurIPS 2025, *Why Do Multi-Agent LLM Systems Fail?* | Các trial fail của swarm (seed 55) thuộc nhóm nào: lỗi giao việc, lệch mục tiêu, hay lỗi kiểm chứng? |
| R3 · Architecture choices | AgentArch, AACL 2026 | Nếu đổi topology mà giữ nguyên mọi thứ khác, biến nào phải cố định để kết luận còn đúng? |
| R4 · Evaluation confounders | EMNLP 2026, *Rethinking Evaluation of MAS Efficiency* | Làm sao chứng minh chênh lệch giữa A/B/C/D là do topology, không phải do prompt, tool hay seed? |

## Phiếu của nhóm

Điền vào cột cuối. Không xóa hai cột đầu.

| Field | Hướng dẫn | Nhóm điền |
| --- | --- | --- |
| CÂU | R1 / R2 / R3 / R4 | R2: Failure taxonomy. |
| SOURCE | Paper/blog, năm, URL, loại bằng chứng (benchmark, production report, blog kinh nghiệm) | Mert Cemri và cộng sự, *Why Do Multi-Agent LLM Systems Fail?*, NeurIPS 2025 (Datasets and Benchmarks Track), https://proceedings.neurips.cc/paper_files/paper/2025/hash/b1041e52d3be19f0a9bc491657488e4a-Abstract-Datasets_and_Benchmarks_Track.html. Nguồn là nghiên cứu phân tích trace, có gán nhãn bởi người và so sánh trên nhiều framework. |
| CLAIM | Một kết luận gốc của nguồn. Không viết rộng hơn phạm vi paper | MAST phân loại 14 failure mode của hệ multi-agent thành ba nhóm: lỗi thiết kế hệ thống, lệch phối hợp giữa agent và lỗi kiểm chứng tác vụ. Đây là taxonomy để phân tích lỗi, không phải cam kết rằng một cách sửa cụ thể sẽ tăng pass rate. |
| BOUNDARY | Model / dataset / setup giới hạn kết luận đó | Bài báo phân tích hơn 1.600 trace từ 7 framework multi-agent; taxonomy được xây từ 150 trace với người gán nhãn. Các tác vụ gồm coding, toán và general agent. LogiX-VN dùng MockLLM, luật hoàn phí cố định và 14 claim public, nên cách gán nhóm lỗi ở đây là diễn giải của nhóm trên task riêng. |
| HYPOTHESIS | Nếu đổi shape A→B (hoặc bật/tắt một thành phần), metric X sẽ đổi theo hướng nào, khoảng bao nhiêu | Nếu swarm vẫn parse ticket nhưng không cho số ngày trong ticket ghi đè `order.delay_days`, trial `C-002` seed 55 sẽ chuyển từ fail sang pass. Dự đoán pass rate public tăng từ 69/70 lên 70/70, pass^5 từ 13/14 lên 14/14 và seed variance về 0. |
| METHOD | Biến giữ cố định: model, tools, seed, corpus, giá, evaluator. Biến duy nhất được thay đổi: … | Chạy `swarm` và `swarm_no_ticket_override` trên cùng 14 claim, 5 seed `11,22,33,44,55`, MockLLM, tập tool, bảng giá, evaluator và SQLite mới cho mỗi trial. Biến thay đổi là quyền ghi đè `delay_days` của order bằng số parse từ ticket. Biến thể vẫn gọi peer/parse/draft và đi qua cùng host gate; tên shape và run id khác để tách trace. |
| FAILURE / METRIC | Một lỗi dự kiến và cách đo nó: pass rate, pass^5, variance, cost/success, leak, bypass | Lỗi cần kiểm: `R-swarm-C-002-s55` trả `resolved` thay vì `denied`. Đối chiếu trạng thái trial đó và các trial còn lại; báo pass rate, pass^5, seed variance và cost/success từ `src/reports/research_ablation.json`. Không suy ra safety count từ report này vì nó không có trường tổng hợp leak/bypass. |

## Kết quả ablation

- Lệnh đã chạy (trong `src/`; trên Windows đặt thư mục tạm vào repo để tránh lỗi quyền của `%TEMP%`):

  ```powershell
  New-Item -ItemType Directory -Path '.bench-tmp' -Force | Out-Null
  $env:TEMP = (Resolve-Path '.bench-tmp').Path
  $env:TMP = $env:TEMP
  python -m lab8.benchmark --shapes swarm,swarm_no_ticket_override --extra-shape swarm_no_ticket_override=bonus.swarm_no_ticket_override:run_claim --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/research_ablation.json
  ```

- File report: `src/reports/research_ablation.json`. Run id đối chiếu: `R-swarm-C-002-s55` và `R-swarm_no_ticket_override-C-002-s55`.
- Kết quả: hypothesis đúng trên bộ public. Swarm gốc pass **69/70** (`pass_rate` 0,985714; `pass_5` 0,928571; variance 0,000816; cost/success 49,57 VND mô phỏng). Biến thể pass **70/70** (`pass_rate` 1,0; `pass_5` 1,0; variance 0; cost/success 48,72 VND mô phỏng). Ở `C-002` seed 55, bản gốc trả `resolved` và fail; biến thể trả `denied` và pass. Không có trial public nào khác fail trong report biến thể.
- Diễn giải lỗi: swarm thiếu bước đối chiếu kết quả parse ticket với dữ liệu order có cấu trúc trước khi quote; nhóm xếp lỗi này vào hướng **task verification** của MAST. Đây là cách phân tích trên LogiX, không phải nhãn do tác giả MAST gán cho trial này.
- Giới hạn: 14 claim public là bộ nhỏ; chưa có nhãn hidden cho ablation này. MockLLM không phải model sản xuất, cost chỉ là mô phỏng và latency là `unavailable`. Không thể từ kết quả này kết luận mọi hệ multi-agent đều có cùng lỗi hoặc cùng mức cải thiện.

Muốn đi xa hơn một ablation để lấy điểm cộng thì xem [docs/bonus_topics.md](../../docs/bonus_topics.md).
