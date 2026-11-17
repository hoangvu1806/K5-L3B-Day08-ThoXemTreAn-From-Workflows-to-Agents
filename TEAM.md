# Team

## Thông tin nhóm

- Tên nhóm: ThoXemTreAn
- Lớp: L3B
- Repo nhóm: `K5-L3B-Day08-ThoXemTreAn-From-Workflows-to-Agents` (xem [SUBMISSION.md](SUBMISSION.md))
- URL repo, nhánh nộp, commit chốt: `https://github.com/hoangvu1806/K5-L3B-Day08-ThoXemTreAn-From-Workflows-to-Agents` · nhánh `main` · commit chốt *(cập nhật ở CP5)*

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 | Đỗ Hoàng Vũ | 2A202603920 | dohoangvu.nt1806@gmail.com | hoangvu1806 | Shape A (`workflow`) + Integration, Benchmark, Crash, ADR |
|   2 | Minh | | | | Shape B (`single`) + Research Card (`research_card.md`) |
| 3 | Hoàng Minh Diệp | 2A202603764 | hoangminhdiepnd2004@gmail.com | [diep142](https://github.com/diep142) | Shape C (`orchestrator`) + Handoff, Bảo mật/Trace & Group Report |
Gợi ý chia vai:

- Nhóm 6 người: integration; workflow; single agent; orchestrator; ledger/policy/crash; eval/report.
- Nhóm 4 người: workflow + integration; single; orchestrator + handoff; ledger + evaluation.

## Bảng đóng góp

`python -m lab8.check_submission` đọc bảng này bằng máy: giữ nguyên tiêu đề `## Bảng đóng góp` và các cột. Mỗi người một dòng: commit có nội dung và ít nhất một test đã thêm hoặc sửa.

| Người | Vai | Commit | Test đã thêm hoặc sửa |
| --- | --- | --- | --- |
| Đỗ Hoàng Vũ | Shape A (`workflow`) + Integration, Benchmark, Crash, ADR | `7a3c0b5` | `src/tests/test_workflow_edge_cases.py` |
| Minh | Shape B (`single`) + Research Card | | |
| Hoàng Minh Diệp | Shape C (`orchestrator`) + Handoff, Bảo mật/Trace & Group Report | `c402a2d` | `src/tests/test_orchestrator_security.py` |

## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

Ví dụ: `report/team/20241234_NguyenVanAn.md`.

Sao chép mục dưới đây cho từng thành viên.

## 2A202603920_DoHoangVu

### Phần việc phụ trách

- Thiết kế và triển khai Shape A (`src/lab8/shapes/workflow.py`) theo quy trình Python cố định.
- Đầu mối tích hợp repo, chạy `lab8.crash_test` (`src/reports/crash.json`), `lab8.benchmark` (`src/reports/benchmark.json`), tự kiểm `student_drop/`, viết `report/team/decision_adr.md` và chạy `python -m lab8.check_submission`.

### Đóng góp cụ thể

- Tạo tài liệu phân công nhóm tại `docs/assignment.md` (`4ffdea3`).
- *(Cập nhật thêm commit triển khai `workflow.py`, file test `src/tests/test_workflow_edge_cases.py`, benchmark/crash và `decision_adr.md` khi hoàn thành.)*

### Bằng chứng

- Commit phân công: `4ffdea3` (`docs: add team assignment for Vu, Minh, and Diep`)
- *(Bổ sung run id, test và commit chốt ở CP4–CP5.)*


## 2A202603764_HoangMinhDiep

### Phần việc phụ trách

- Thiết kế và triển khai Shape C (orchestrator) tại `src/lab8/shapes/orchestrator.py`.
- Xây dựng cơ chế handoff giữa orchestrator, investigator và host, đảm bảo phân quyền công cụ và luồng xử lý đúng contract.
- Kiểm tra bảo mật handoff/trace, ngăn lộ secret và thông tin đơn hàng nhạy cảm.
- Bổ sung unit test cho cơ chế approval, xử lý crash và bảo mật trace.
- Tham gia tổng hợp, rà soát báo cáo nhóm.

### Đóng góp cụ thể

- Triển khai src/lab8/shapes/orchestrator.py và bổ sung `src/tests/test_orchestrator_security.py` trong commit c402a2d.
- Xây dựng handoff bằng make_handoff, chỉ cấp quyền sử dụng tool đọc cho investigator; không đưa ticket, secret hoặc header thô vào trace.
- Investigator tính quote từ dữ liệu đơn; orchestrator chuyển quote đầy đủ cho host để kiểm tra approval và giới hạn theo từng đơn.
- Bổ sung test kiểm tra handoff/trace không chứa secret hoặc thông tin đơn nhạy cảm, đồng thời xác minh host từ chối approval được mượn từ claim khác.

### Bằng chứng

- Commit triển khai: c402a2d.
- Commit tích hợp vào main: 1292add.
- File triển khai: src/lab8/shapes/orchestrator.py.
- File kiểm thử: src/tests/test_orchestrator_security.py.
- Kết quả kiểm thử sau tích hợp: `python -m pytest -q -m student -o addopts=` 248 passed, trong đó có 62 test cho orchestrator, `python -m pytest -q` 89 passed.

## MSSV_HoTen

### Phần việc phụ trách

-

### Đóng góp cụ thể

-

### Bằng chứng

-
