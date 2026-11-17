# Bonus report: B4

- Topic + nguồn (tên, năm, slide): B4 · Baseline công bằng, ablation và thống kê. EMNLP 2026, *Rethinking Evaluation of MAS Efficiency* (slide 44, 59); AgentArch, AACL 2026 (slide 43).
- CLAIM của nguồn (1 câu): phần "efficiency gain" của multi-agent có thể đến từ cách dựng benchmark, nên phải so với single-agent và baseline đơn giản trong khi giữ cố định runtime, model và tool.
- BOUNDARY (model / dataset / setup): EMNLP đo trên hệ multi-agent LLM thật với nhiều task; kết luận là về cách thiết kế benchmark, không phải một con số cho LogiX. Ở đây model là MockLLM, corpus là 14 claim public, giá mô phỏng, latency `unavailable`.
- HYPOTHESIS trên LogiX: (1) bỏ các lần gọi model peer/parse/draft của swarm không làm đổi độ đúng, chỉ bớt cost; (2) bỏ quyền ghi đè `delay_days` từ ticket sẽ sửa trial fail `C-002` seed 55; (3) chênh lệch một trial đó quá nhỏ để có ý nghĩa thống kê trên 14 claim.
- Biến cố định / biến thay đổi: cố định MockLLM, tập tool, seed `11,22,33,44,55`, 14 claim public, bảng giá, evaluator, SQLite mới mỗi trial. Mỗi biến thể chỉ đổi một thứ: `swarm_pruned` bỏ ba lần gọi model (giữ nguyên mọi quyết định, kể cả override seed 55); `swarm_no_ticket_override` bỏ đúng bước ghi đè delay từ ticket (giữ nguyên các lần gọi model). `workflow` là baseline rules-only, không model.
- Lệnh tái lập (copy-paste được): chạy trong `src/`.

  ```bash
  python -m lab8.benchmark --shapes workflow,swarm,swarm_pruned,swarm_no_ticket_override \
    --extra-shape swarm_pruned=bonus.swarm_pruned:run_claim \
    --extra-shape swarm_no_ticket_override=bonus.swarm_no_ticket_override:run_claim \
    --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/bonus_ablation.json
  python -m bonus.stats --benchmark reports/bonus_ablation.json --baseline swarm --out reports/bonus_stats.json
  python -m pytest -q tests/test_bonus_stats.py
  ```

- File report + run id: `src/reports/bonus_ablation.json`, `src/reports/bonus_stats.json`. Run id đối chiếu: `R-swarm-C-002-s55` (fail), `R-swarm_pruned-C-002-s55` (fail, cùng lỗi), `R-swarm_no_ticket_override-C-002-s55` (pass).

## Kết quả

Số lấy từ `reports/bonus_ablation.json` và `reports/bonus_stats.json`. CI là bootstrap 95% resample theo claim; p-value là McNemar exact so với swarm.

| Shape | pass_rate | 95% CI | pass^5 | variance | cost/success (VND) | McNemar vs swarm |
| --- | --- | --- | --- | --- | --- | --- |
| workflow (rules-only) | 1.000 | [1.000, 1.000] | 1.000 | 0.000000 | 27.86 | 1 cặp lệch, p=1.0 |
| swarm | 0.986 | [0.957, 1.000] | 0.929 | 0.000816 | 49.57 | — |
| swarm_pruned | 0.986 | [0.957, 1.000] | 0.929 | 0.000816 | 47.25 | 0 cặp lệch, p=1.0 |
| swarm_no_ticket_override | 1.000 | [1.000, 1.000] | 1.000 | 0.000000 | 48.72 | 1 cặp lệch, p=1.0 |

- Ablation 1 (bỏ model chatter): `swarm_pruned` trùng swarm từng cell, 0 cặp lệch. Ba lần gọi model peer/parse/draft không mua thêm độ đúng nào, chỉ là cost.
- Ablation 2 (bỏ override ticket): `swarm_no_ticket_override` lật đúng một trial `C-002` seed 55 từ fail sang pass. Đây là chỗ swarm tin số ngày trễ ghi trong ticket thay vì số trong order.
- Baseline rules-only `workflow` đúng hết và rẻ nhất (27.86 so với 47–50 của nhóm swarm).

## Kết luận

Ủng hộ cả ba hypothesis, nhưng có một chỗ phải nói rõ. H1 và H3 đúng: bỏ model chatter không đổi kết quả (0 cặp lệch), và chênh lệch một trial giữa swarm và `swarm_no_ticket_override` cho p=1.0 theo McNemar, tức **chưa đủ ý nghĩa thống kê** trên 14 claim dù hướng cải thiện rõ. Đúng tinh thần EMNLP: một con số pass rate nhỉnh hơn trên corpus nhỏ chưa chứng minh được điều gì. H2 đúng về hướng (lật được trial seed 55) nhưng cỡ mẫu không cho kết luận mạnh.

Điều kiện làm kết luận đảo lại: nếu corpus đủ lớn để nhiều trial dính bẫy override ticket thì McNemar sẽ thành có ý nghĩa, và lúc đó bỏ override là cải thiện thật chứ không chỉ về hướng. Ngược lại, nếu swarm không còn override thì nó hết lỗi nhưng vẫn đắt hơn workflow mà không đúng hơn, nên rules-only vẫn là lựa chọn ít tự chủ nhất.

## Giới hạn

MockLLM không phải model sản xuất, cost là VND mô phỏng, latency để `unavailable`. 14 claim public là bộ nhỏ, chưa chạy trên hidden. Bootstrap resample theo claim nên CI phản ánh bất định ở mức claim; với corpus bé, CI của swarm chạm trần 1.0. McNemar exact đúng cho số cặp lệch ít ở đây, nhưng p=1.0 là do cỡ mẫu chứ không phải bằng chứng hai shape bằng nhau. Không suy ra safety count từ các report này; secret leak và approval bypass đo ở cổng chính (0/0).
