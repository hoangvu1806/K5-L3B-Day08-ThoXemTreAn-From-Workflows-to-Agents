# Báo cáo cá nhân — 2A202603764_HoangMinhDiep

## 1. Thông tin thành viên

- Họ tên: Hoàng Minh Diệp
- MSSV: 2A202603764
- Email: hoangminhdiepnd2004@gmail.com
- GitHub: https://github.com/diep142

## 2. Phần việc phụ trách

- Phụ trách Shape C (`orchestrator`), handoff và kiểm tra bảo mật trace.

## 3. Đóng góp cụ thể

- Triển khai [orchestrator.py](../../src/lab8/shapes/orchestrator.py) và thêm [test_orchestrator_security.py](../../src/tests/test_orchestrator_security.py) trong commit `c402a2d`.
- Tạo handoff bằng `make_handoff`, chỉ cấp tool đọc cho investigator và không đưa ticket, secret hay header thô vào trace. Investigator tính quote từ dữ liệu đơn; orchestrator chuyển quote đầy đủ cho host để kiểm approval và giới hạn theo đơn.
- Chuyển tiếp `crash_at`; khi gặp `InjectedCrash`, ghi trace rồi ném lại exception. Kết nối SQLite được đóng trong `finally`.
- Test bổ sung kiểm tra handoff/trace không chứa secret và thông tin đơn nhạy cảm, đồng thời kiểm tra approval mượn từ claim khác bị host từ chối.

## 4. Bằng chứng

- Commit kỹ thuật: [`c402a2d`](https://github.com/hoangvu1806/K5-L3B-Day08-ThoXemTreAn-From-Workflows-to-Agents/commit/c402a2d); đã được tích hợp vào `main` qua merge `1292add`.
- Test cá nhân: `test_handoff_and_trace_exclude_secrets_and_order_pii` và `test_approval_borrowed_from_another_claim_is_denied`.
- Bộ student sau tích hợp: `python -m pytest -q -m student -o addopts=` đạt `248 passed`, gồm 62 test cho orchestrator; cổng mặc định `python -m pytest -q` đạt `89 passed`.
- Ví dụ run id trong [benchmark public](../../src/reports/benchmark.json): `R-orchestrator-C-001-s11`. Trên 70 trial public, orchestrator đạt pass rate `1.000`, pass^5 `1.000`, cost/success mô phỏng `55.71 VND`.

## 5. Công cụ AI đã dùng

- Dùng Copilot để tìm hiểu luồng xử lý, hỗ trợ triển khai shape, viết test bảo mật và tổng hợp báo cáo.
- Kiểm tra bằng cách đọc lại code, đối chiếu luật nghiệp vụ và contract, chạy test cá nhân, ma trận student cùng cổng host; đối chiếu số liệu với JSON do công cụ lab sinh ra.

## 6. Tự đánh giá

- Shape C đã vượt bộ public và các test bảo mật được nêu ở trên. Kết quả này không chứng minh shape sẽ đạt toàn bộ trường hợp hidden hoặc an toàn trong môi trường production.
- Cần tiếp tục rà soát trace của các shape sau tích hợp và đối chiếu kết quả hidden khi giảng viên chấm. Bản tự đánh giá này cần được cá nhân rà soát trước khi nộp.
