# Báo cáo cá nhân - Vũ Quang Minh

## 1. Thông tin thành viên

- Họ tên: Vũ Quang Minh
- MSSV: 2A202603727
- Email: vuquangminh240804@gmail.com
- GitHub: https://github.com/minh240804

## 2. Phần việc phụ trách

Tôi phụ trách Shape B (`single`) trong `src/lab8/shapes/single.py` và viết test cho phần này. Theo phân công ở `docs/assignment.md`, tôi còn phụ trách `report/team/research_card.md` và phần Single trong báo cáo nhóm. Hai mục báo cáo nhóm hiện chưa có nội dung hoàn chỉnh trong repo, nên tôi chưa tính là phần đã làm xong.

## 3. Đóng góp cụ thể

Commit `ccccecb` triển khai vòng ReAct bằng `lab8.runtime.run_react` với giới hạn 8 bước. Agent dùng các tool đọc để lấy claim, order và lịch sử hoàn tiền; `compute_compensation` tính quote từ dữ liệu order. Sau vòng ReAct, code gọi `durability.issue_refund` với quote đầy đủ. Host kiểm approval, trần hoàn theo đơn và ghi ledger. Tôi dùng `finish()` cho các nhánh trả về, ghi trace bằng những field đã chọn và đóng kết nối SQLite trong `finally`.

Tôi thêm `src/tests/test_single_react_bounds.py` để kiểm giới hạn bước, chặn tool ghi, trường hợp T14 chỉ hoàn phần chênh và retry sau crash không tạo thêm refund. Trong cùng commit, tôi đổi tên test chung ở `src/tests/test_public_matrix.py` từ `test_public_single_run_cases` thành `test_public_claim_cases`; nhờ vậy lệnh `-k single` chỉ chọn case của Shape B.

## 4. Bằng chứng

- Commit kỹ thuật: `ccccecb` (`feat: implement single ReAct agent with host-only refund gate and add focused tests`).
- Chạy từ `src/`: `python -m pytest -q -m student -o addopts= -k single -p no:cacheprovider --basetemp=./.pytest-minh-report-single` cho kết quả **62 passed**.
- Cổng test mặc định: `python -m pytest -q -p no:cacheprovider --basetemp=./.pytest-minh-report-host` cho kết quả **89 passed, 248 deselected**. Kết quả này bao gồm test của cả repo, không phải chỉ phần tôi viết.
- `src/reports/benchmark.json`: Shape B đạt **70/70 trial public** trên 14 claim × 5 seed, `pass_rate = 1.0`, `pass_5 = 1.0`, `seed_variance = 0`. `cost_per_success_vnd = 38.3714285714285` là giá mô phỏng, không phải chi phí API thật. Ví dụ run id: `R-single-C-014-s55`.
- Test T14 trong file test cá nhân xác nhận `proposal_amount = 150000` VND và ledger ghi `120000` VND sau khi host trừ khoản đã hoàn trước. Test crash trong cùng file xác nhận retry claim C-012 vẫn chỉ có một dòng refund.

## 5. Công cụ AI đã dùng

Tôi dùng Codex để đọc contract, hỗ trợ viết `single.py`, thêm test và tìm nguyên nhân lệnh `-k single` chọn nhầm case của các shape khác. Tôi kiểm lại bằng test riêng của Shape B, cổng pytest mặc định và số liệu trong `src/reports/benchmark.json`; không dùng AI để tạo số liệu benchmark hay run id.

## 6. Tự đánh giá

Shape B đã qua 62 case student và 70/70 trial public trong benchmark hiện có. Kết quả này chưa thay cho điểm hidden của giảng viên. `report/team/research_card.md` vẫn chưa được điền và chưa có ablation để báo cáo; đây là phần tôi còn phải hoàn thành theo phân công.
