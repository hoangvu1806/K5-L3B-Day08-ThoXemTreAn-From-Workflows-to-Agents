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
|   3 | Diệp | | | | Shape C (`orchestrator`) + Bảo mật/Trace & Group Report |

Gợi ý chia vai:

- Nhóm 6 người: integration; workflow; single agent; orchestrator; ledger/policy/crash; eval/report.
- Nhóm 4 người: workflow + integration; single; orchestrator + handoff; ledger + evaluation.

## Bảng đóng góp

`python -m lab8.check_submission` đọc bảng này bằng máy: giữ nguyên tiêu đề `## Bảng đóng góp` và các cột. Mỗi người một dòng: commit có nội dung và ít nhất một test đã thêm hoặc sửa.

| Người | Vai | Commit | Test đã thêm hoặc sửa |
| --- | --- | --- | --- |
| Đỗ Hoàng Vũ | Shape A (`workflow`) + Integration, Benchmark, Crash, ADR | *(cập nhật sau khi hoàn thành CP2–CP5)* | *(dự kiến: `src/tests/test_workflow_edge_cases.py`)* |
| Minh | Shape B (`single`) + Research Card | | |
| Diệp | Shape C (`orchestrator`) + Bảo mật/Trace & Group Report | | |

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

## MSSV_HoTen

### Phần việc phụ trách

-

### Đóng góp cụ thể

-

### Bằng chứng

-
