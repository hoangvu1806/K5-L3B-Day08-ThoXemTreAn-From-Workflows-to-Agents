# Báo cáo nhóm — Lab 8 LogiX-VN

## 1. Thông tin nhóm

- Tên nhóm: ThoXemTreAn; lớp L3B.
- Thành viên và phân công: xem [TEAM.md](../../TEAM.md).
- Commit dẫn chứng trong [ADR](decision_adr.md): `0828b99` (code và báo cáo benchmark/crash). Nhóm cần đồng bộ lại nếu chốt commit đánh giá khác.

## 2. Mục tiêu và cách tiếp cận

Nhóm xử lý yêu cầu hoàn phí vận chuyển hoặc bồi thường hàng hỏng của LogiX-VN theo bốn kiến trúc: workflow, single agent, orchestrator và swarm tham chiếu. Mục tiêu là chọn kiến trúc ít tự chủ nhất vẫn đáp ứng nghiệp vụ, bảo mật và khả năng phục hồi.

Vũ phụ trách workflow, tích hợp và benchmark; Minh phụ trách single và research card; Diệp phụ trách orchestrator, handoff và bảo mật trace. Nhóm triển khai ba shape theo cùng `run_claim`, dùng host chung và so sánh với swarm trên cùng 14 claim public và năm seed. Ticket là dữ liệu không đáng tin; số tiền được tính bằng code từ order và policy hiện hành.

## 3. Giải pháp

**Workflow (A).** Luồng Python cố định đọc claim qua `get_claim_view`, kiểm tra phạm vi đơn qua `lookup_order`, tính quote bằng `compute_compensation` và gửi quote dương đầy đủ đến host. Không phân tích ticket để xác định tiền; không gọi model. Các nhánh thiếu thông tin, không có quyền hoặc quote bằng 0 trả kết quả và trace tương ứng.

**Single (B).** Một vòng `run_react` tối đa tám bước chọn các tool đọc claim, đơn, lịch sử hoàn và tính quote. `MockLLM` được gọi để tính chi phí mô phỏng cho các quyết định, còn lựa chọn hành động trong implementation được viết bằng code. Sau vòng lặp, shape gọi host; model và worker không có quyền ghi refund.

**Orchestrator (C).** Orchestrator tạo `handoff.v1` bằng `make_handoff`, với `facts` rỗng và danh sách tool chỉ đọc. `run_readonly_investigators` lần lượt tra đơn, policy, lịch sử hoàn và tính quote. Investigator không được cấp tool ghi; orchestrator gửi quote đầy đủ cho host. Shape C hiện là mô phỏng bằng code, không gọi model và không chạy investigator song song.

**Swarm (D).** Shape tham chiếu có sẵn, sử dụng thêm các lượt model mô phỏng. Ở seed chia hết cho 5, swarm có điểm yếu cố ý: có thể tin số ngày trễ trong ticket thay vì order.

**Ranh giới và an toàn chung.** `compute_compensation` tính entitlement; `issue_refund` là cửa ghi duy nhất, kiểm approval đúng claim, trần theo đơn và idempotency. Shape không tự trừ khoản đã hoàn trước khi gửi quote. Ledger và audit committed được ghi trong cùng transaction; crash được truyền ra để thử resume. Trace ghi các bước và kết quả đã chọn lọc, không ghi ticket thô, secret, header, số điện thoại, địa chỉ, tên hàng hay ghi chú nội bộ. Handoff được lọc theo allowlist, không dựa vào tóm tắt của model.

## 4. Kết quả

Nguồn: [benchmark.json](../../src/reports/benchmark.json), 14 claim × 5 seed `11,22,33,44,55`, mỗi trial dùng SQLite mới. Chi phí là VND **mô phỏng**; steps là số event trong trace.

| Shape | Pass rate | Pass^5 | Seed min–max | Variance | Cost/success | Steps mean / p95 |
| --- | ---: | ---: | --- | ---: | ---: | --- |
| Workflow | 1.000 | 1.000 | 1.000–1.000 | 0.000000 | 27.86 | 4.43 / 5 |
| Single | 1.000 | 1.000 | 1.000–1.000 | 0.000000 | 38.37 | 6.79 / 8 |
| Orchestrator | 1.000 | 1.000 | 1.000–1.000 | 0.000000 | 55.71 | 3.71 / 4 |
| Swarm | 0.986 | 0.929 | 0.929–1.000 | 0.000816 | 49.57 | 2.80 / 3 |

Swarm sai một trial `R-swarm-C-002-s55`: ticket nói trễ 5 ngày nhưng order ghi 2 ngày; kết quả `resolved` thay vì `denied`. Theo [crash.json](../../src/reports/crash.json), crash safety là **20/20**. Suite này chủ yếu kiểm host và swarm; crash của các shape nhóm còn được kiểm qua T12 trong ma trận student.

Sau tích hợp, chạy lần lượt `python -m pytest -q` đạt **89 passed**, và `python -m pytest -q -m student -o addopts=` đạt **248 passed**. Các test swarm xem lỗi cố ý ở T02/seed 55 là kết quả mong đợi, nên pass số test không đồng nghĩa benchmark swarm đạt 100%.

Nhóm chọn workflow trong [ADR](decision_adr.md): trên bộ public, shape này đạt cùng pass rate với single và orchestrator, đồng thời có cost/success mô phỏng thấp nhất. Kết quả hidden và các chỉ số an toàn chính thức chưa được xác minh bởi report của giảng viên. Phiếu nghiên cứu và ablation: xem [research card](research_card.md).

## 5. Khó khăn và cách xử lý

- Sau khi workflow và single được nhập vào `main`, test orchestrator báo 62 lỗi vì nhánh Shape C chưa được tích hợp: `main` vẫn chứa stub `not_implemented`. Nhóm đã merge nhánh orchestrator; ma trận student chạy lại đạt 248 test.
- Khi chạy cổng host và ma trận student đồng thời, có một lần T01 orchestrator báo `invalid_trace`. Hai lượt có thể cùng ghi đường dẫn trace theo run id; chạy lại ma trận riêng, không đồng thời, đạt 248 test. Khi tái lập, chạy các bộ test tuần tự để tránh tranh chấp file trace.

## 6. Tổng hợp đóng góp

Phân công và bằng chứng từng thành viên được ghi trong [TEAM.md](../../TEAM.md) và các báo cáo cá nhân. Diệp đóng góp Shape C và test bảo mật trong commit `c402a2d`; Vũ đóng góp workflow trong commit `7a3c0b5`; Minh đóng góp single trong commit `ccccecb`.

## 7. Hạn chế và hướng cải thiện

- MockLLM và giá token/tool là mô phỏng, không đại diện cho hiệu năng hay chi phí model production; latency là `unavailable`.
- Corpus public nhỏ và không thay thế hidden 40 claim × 5 seed. Không suy diễn pass rate public thành điểm hidden; tự kiểm trên `student_drop` không có nhãn cũng không cho pass rate.
- Các shape hiện khác nhau cả cách gọi tool và số lần gọi model; chênh lệch không thể quy toàn bộ cho topology. Cần ablation kiểm soát từng biến như [research card](research_card.md) yêu cầu.
- Nếu bài toán cần xử lý ngôn ngữ phức tạp hơn, hoặc có các phần điều tra độc lập thực sự chạy song song, cần đo lại trước khi quyết định workflow còn là lựa chọn phù hợp.

## 8. Tài liệu tham khảo

- [Luật nghiệp vụ](../../docs/business_rules.md), [contract kết quả và trace](../../docs/contracts.md).
- [Kiến trúc](../../docs/architecture.md), [định nghĩa metric](../../docs/metrics.md), [rubric](../../RUBRIC.md).
- [Hướng dẫn chạy và bộ test](../../src/README.md).
