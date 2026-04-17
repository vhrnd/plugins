# Revise Data Interpretation Guide

Tài liệu này chỉ mô tả phần cấp bài của dữ liệu từ `lms_get_revise(revise_id)`.

## Khi nào đọc file này

- Khi đang review `revise` và cần hiểu field top-level.
- Khi cần biết lúc nào nên đọc raw resource `lms://revise/{revise_id}`.
- Không dùng file này cho logic đọc `questions[]`; phần đó nằm ở `question-data-interpretation.md`.

## Tool và Resource dùng khi nào

- `lms_get_revise(revise_id)`
  - Dùng cho dữ liệu revise đã normalize.
- `lms://revise/{revise_id}`
  - Chỉ đọc khi dữ liệu normalize chưa đủ để kết luận hoặc cần đối chiếu payload gốc.

## Field Semantics Cấp Bài

- `domain`: luôn là `revise`.
- `revise_id`: mã bài revise đang review.
- `title`: tên bài, dùng làm context cấp bài khi đọc từng câu nhưng không thay thế nội dung của câu hiện tại.
- `questions`: danh sách câu đã normalize; cách đọc chi tiết nằm ở `question-data-interpretation.md`.

## Khi nào phải đọc raw resource

- Cần debug vì dữ liệu normalize có dấu hiệu lệch payload thật.
- Có mâu thuẫn cần đối chiếu field gốc.
- Câu phụ thuộc mạnh vào media hoặc ngữ cảnh mà dữ liệu normalize chưa đủ.
