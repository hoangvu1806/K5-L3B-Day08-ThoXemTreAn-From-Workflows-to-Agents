# Decision record

Điền sau dấu `:` trên cùng dòng, không xóa nhãn. Giảng viên và `python -m lab8.check_submission` (chạy trong `src/`) đọc các dòng này bằng máy. Không đổi tên hay dời file này khỏi `report/team/`.
`Shape chọn` phải là đúng một trong: `workflow`, `single`, `orchestrator`, `swarm`. Đây là shape được chấm cổng hidden.

- Shape chọn: workflow
- Commit hash: 0828b99
- Run id dẫn chứng: src/reports/benchmark.json (4 shape × seed 11,22,33,44,55; ví dụ R-workflow-C-001-s11)
- Pass rate / pass^5 / seed min-max / variance: 1.000 / 1.000 / 1.000–1.000 / 0.000000
- Cost per success (mô phỏng, VND): 27.86
- Crash safety: 20/20 (src/reports/crash.json)
- Secret leak / approval bypass: 0 / 0

Ví dụ một dòng đã điền: `- Shape chọn: workflow`, `- Crash safety: 20/20 (src/reports/crash.json)`.

## Vì sao shape này

Chạy cùng 14 claim public, cùng 5 seed, cùng bảng giá, cả bốn shape ra số trong `src/reports/benchmark.json`:

| Shape | pass | pass^5 | variance | cost/success | steps |
| --- | --- | --- | --- | --- | --- |
| workflow | 1.000 | 1.000 | 0.000000 | 27.86 | 4.43 |
| single | 1.000 | 1.000 | 0.000000 | 38.37 | 6.79 |
| orchestrator | 1.000 | 1.000 | 0.000000 | 55.71 | 3.71 |
| swarm | 0.986 | 0.929 | 0.000816 | 49.57 | 2.80 |

Workflow đúng hết mọi trial, pass^5 bằng 1, variance bằng 0, mà cost/success thấp nhất trong bốn shape. Ba shape có model không thêm được gì về độ đúng trên corpus này, chỉ thêm chi phí: single và orchestrator đắt hơn nhưng pass vẫn 1.0, còn swarm vừa đắt vừa là shape duy nhất trượt. Nhiệm vụ hoàn phí ship có luật rõ, số tiền do code tính, nên phần tự chủ của model không có việc để làm. Chọn workflow là chọn shape ít tự chủ nhất mà vẫn làm đủ.

## Có đáng đổi lấy multi-agent không

Không. Swarm pass nhỉnh hơn workflow ở đâu cũng không có, mà ngược lại: pass^5 của swarm chỉ 0.929 và variance 0.000816, do nó trượt đúng một chỗ là C-002 ở seed 55 (`R-swarm-C-002-s55`, `status resolved != denied`). Ở seed đó swarm tin số ngày trễ ghi trong ticket (5 ngày) thay vì số trong order (2 ngày) nên hoàn nhầm. Đổi sang multi-agent ở đây là trả thêm tiền để nhận về độ dao động.

Quyết định sẽ đảo lại nếu nhiệm vụ đổi bản chất: luật không viết hết được thành code, hoặc phần việc tách song song thật sự được và cái cần tối ưu là độ trễ chứ không phải độ đúng. Trên LogiX hiện tại thì không có điều kiện nào trong số đó.

## Trace và bằng chứng

Trace workflow ghi từng bước: `get_claim_view` (chỉ cờ found và có order_id hay không), `lookup_order` (order_id, status, delay_days, phí, paid, damage_verified), `compute_compensation` (số tiền, lý do, clause), `issue_refund` (ok, reason, conflict) và `decision` cuối. Những field cố ý không ghi: nội dung ticket, số điện thoại, địa chỉ, tên hàng, internal note và mọi `CANARY_SECRET_*`. Lý do là trace do grader đọc, nên nó là ranh giới bảo mật chứ không phải chỗ debug.

Cách chứng minh không lộ secret: workflow xây trace từ danh sách field cho phép ngay từ đầu, không ghi thô rồi lọc. Test `tests/test_workflow_edge_cases.py` quét cả file trace lẫn `RunResult` của từng claim public, so với danh sách `forbid_substrings` trong dữ liệu, và kiểm luôn rằng nguyên văn ticket không lọt vào. Grader fail-closed với `missing_trace`, `stale_trace`, `invalid_trace`, nên file nằm ngoài vùng quét bị tính là trượt. Crash suite 20/20 và `Secret leak / approval bypass: 0 / 0` là bằng chứng cho ba must-pass.

## Giới hạn

MockLLM không phải model sản xuất, nên số pass của các shape có model có thể khác khi chạy model thật. Latency để `unavailable` vì MockLLM không đo được thời gian, cost là VND mô phỏng chứ không phải hóa đơn API. Số trong file là số chạy ra, nhóm không sửa JSON cho đủ ngưỡng.
