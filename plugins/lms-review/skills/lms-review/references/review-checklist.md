# Review Checklist Guide

Tài liệu này dùng khi LLM cần rà tiêu chí review một cách đầy đủ và nhất quán.

## Khi nào đọc file này

- Khi chuẩn bị review một bài `revise` hoặc `practice`.
- Khi cần hệ thống lại tiêu chí thay vì đọc cảm tính.
- Khi cần quyết định mức độ lỗi và kết luận tổng thể.
- Khi cần rà lại tính nhất quán trước khi chốt severity cho từng câu.

## Các nhóm tiêu chí bắt buộc

### 1. Ngôn ngữ và diễn đạt

- Có lỗi chính tả không?
- Câu văn có sai ngữ pháp hoặc khó hiểu không?
- Yêu cầu đề bài có mơ hồ hoặc gây hiểu nhầm không?
- Bối cảnh của câu có hợp lý không?

### 2. Độ đúng kiến thức

- Đề bài có sai kiến thức không?
- Lời giải có sai kiến thức không?
- Đáp án đang được cài có khớp với nội dung và lời giải không?

### 3. Setup đáp án và chấm điểm

- Có thiếu phương án không?
- Có phương án trùng nhau không?
- Số lượng phương án có hợp với dạng câu không?
- Đáp án đúng/sai có đang được cài sai không?
- Cách chấm điểm có dấu hiệu bất thường không?

### 4. Tính nhất quán giữa các phần

- Đề bài, đáp án và lời giải có mâu thuẫn nhau không?
- Ảnh/audio có khớp với nội dung câu không?
- Bảng biểu hoặc hình trong lời giải có đang hỗ trợ đúng cho kết luận không?

### 5. Khả năng làm bài thực tế

- Học sinh có đủ dữ kiện để làm câu này không?
- Câu có phụ thuộc vào image/audio không? Nếu có, phải fetch ảnh/audio trước khi kết luận — không được mặc định coi là thiếu dữ liệu khi chưa thử fetch.
- Nếu fetch thất bại hoặc không có tool fetch, mới được hạ mức chắc chắn của nhận định và ghi rõ lý do.

### 6. Chất lượng sư phạm

- Lời giải có đủ giúp học sinh hiểu vì sao đúng/sai không?
- Nội dung có gây nhiễu hoặc rườm rà không?
- Mức độ câu hỏi có dấu hiệu không phù hợp không?

## Phân loại mức độ lỗi

- `Nghiêm trọng`
  - Sai kiến thức
  - Sai setup đáp án đúng
  - Sai logic chấm điểm làm ảnh hưởng kết quả
  - Thiếu dữ kiện khiến câu không làm được

- `Trung bình`
  - Diễn đạt gây hiểu nhầm
  - Lời giải chưa hợp lý
  - Media hoặc bảng biểu chưa khớp hoàn toàn

- `Nhẹ`
  - Lỗi chính tả
  - Trình bày chưa gọn
  - Câu chữ chưa tự nhiên nhưng chưa làm đổi bản chất câu

## Mapping mức độ sang kết luận tổng thể

- `Đạt`
  - Không có lỗi đáng kể, hoặc chỉ có lỗi nhẹ nhỏ.
- `Cần sửa`
  - Có lỗi trung bình hoặc một số lỗi nhẹ lặp lại.
- `Lỗi nghiêm trọng`
  - Có lỗi kiến thức, lỗi setup đáp án/chấm điểm nghiêm trọng, hoặc câu không đủ dữ kiện để làm.

Chi tiết format báo cáo cuối cùng (các section bắt buộc, cách trình bày từng câu lỗi, khuyến nghị ưu tiên) thực hiện theo `Output Contract` trong `lms-review/SKILL.md`.

## Khi nào phải nói chưa đủ dữ liệu

- Fetch ảnh/audio thất bại và nội dung câu phụ thuộc vào ảnh/audio đó.
- Không có tool để fetch và câu phụ thuộc hoàn toàn vào media.
- Dữ liệu normalize chưa đủ và raw resource cũng không bổ sung thêm được.

Khi đó phải nói rõ:

- `Chưa đủ dữ liệu để kết luận chắc chắn — lý do: [fetch thất bại / không có tool fetch]`

Không được khẳng định mạnh nếu bằng chứng còn thiếu, nhưng cũng không được mặc định báo thiếu khi chưa thử fetch.
