# User-Facing Writing Guide

Tài liệu này dùng khi LLM cần chuyển dữ liệu LMS thành câu trả lời dễ đọc cho người không kỹ thuật.

## Khi nào đọc file này

- Khi chuẩn bị viết câu trả lời cuối cho người dùng.
- Khi dễ bị trượt sang văn phong kỹ thuật.
- Khi cần diễn đạt lỗi setup đáp án hoặc lỗi cấu trúc bằng ngôn ngữ đời thường.

## Nguyên tắc chính

- Người dùng cần hiểu lỗi của bài, không cần hiểu cấu trúc JSON.
- Dữ liệu kỹ thuật chỉ dùng cho suy luận nội bộ.
- Không lộ tên field, type code, hay từ vựng schema trong câu trả lời cuối nếu người dùng không hỏi.

## Bảng dịch từ kỹ thuật sang ngôn ngữ đời thường

- `free_text` → `câu tự luận`
- `single_choice` → `câu trắc nghiệm chọn một đáp án`
- `multi_true_false` → `câu đúng/sai gồm nhiều phát biểu`
- `solution_text` → `lời giải`
- `answers` → `các phương án` hoặc `các phát biểu`
- `is_true = false` → `đang bị đánh dấu là sai`
- `is_true = true` → `đang được đánh dấu là đúng`
- `structural_flags` → diễn đạt thành lỗi cụ thể như `thiếu lời giải`, `thiếu đáp án`, `trùng phương án`

## Từ cấm trong câu trả lời cuối

Không nên viết trực tiếp các từ sau:

- `type_code`
- `content_text`
- `solution_text`
- `answers`
- `is_true`
- `structural_flags`
- `raw payload`
- `schema`
- `normalized`
- `upstream`
- `free_text`
- `single_choice`
- `multi_true_false`

## Cách nói nên dùng

- Không nên nói:
  - `is_true=false`
  - `field lời giải đang thiếu`
  - `Câu 2 là multi_true_false`

- Nên nói:
  - `đáp án hiện đang được cài là sai`
  - `câu này đang thiếu phần lời giải`
  - `Câu 2 là câu đúng/sai gồm nhiều phát biểu`

## Mẫu diễn đạt theo lỗi thường gặp

### Lỗi setup đáp án

- `Phát biểu này đang bị đánh dấu sai, nhưng đối chiếu nội dung và lời giải thì phải được đánh dấu là đúng.`
- `Đáp án đúng hiện đang được cài chưa đúng với lời giải.`

### Lỗi diễn đạt

- `Câu văn chưa rõ ý, học sinh có thể hiểu theo nhiều cách.`
- `Đề bài đang có lỗi chính tả hoặc dùng từ chưa tự nhiên.`

### Lỗi lời giải

- `Câu này đang thiếu phần lời giải.`
- `Lời giải hiện có nhưng chưa đủ để giải thích vì sao đáp án đúng.`

### Lỗi chấm điểm

- `Cách chấm điểm của câu này có dấu hiệu chưa hợp lý với dạng câu hỏi.`
- `Phần điểm hoặc cách quy đổi điểm nên được kiểm tra lại.`

### Chưa đủ dữ liệu (chỉ dùng khi fetch ảnh thất bại hoặc không có tool fetch)

- `Câu này có ảnh đi kèm nhưng chưa tải được nội dung ảnh, nên chưa thể kết luận chắc chắn.`
- `Cần kiểm tra lại ảnh lời giải trực tiếp trước khi có thể kết luận về câu này.`

Lưu ý: **Không dùng mẫu này chỉ vì thấy có URL ảnh trong dữ liệu.** Phải thử fetch trước — chỉ dùng mẫu này khi fetch thực sự thất bại.

## Mẫu chuyển từ kỹ thuật sang đời thường

- Không nên viết:
  - `Phát biểu 3 đang gán is_true=false.`
- Nên viết:
  - `Ở phát biểu 3, hệ thống hiện đang đánh dấu là sai, nhưng theo nội dung thì phát biểu này phải là đúng.`

- Không nên viết:
  - `Question có structural_flags missing_comment.`
- Nên viết:
  - `Câu này đang thiếu phần lời giải.`

- Không nên viết:
  - `lời giải chỉ có [image: URL], chưa đủ dữ liệu.`
- Nên viết:
  - `Lời giải của câu này nằm hoàn toàn trong ảnh.` (sau khi đã fetch và xem ảnh)

## Rule cuối cùng

Trước khi trả lời, tự kiểm tra:

- Người không biết JSON có đọc hiểu được không?
- Có từ kỹ thuật nội bộ nào lọt ra ngoài không?
- Có thể thay bằng cách nói đơn giản hơn không?
- Có đang dùng mẫu "chưa đủ dữ liệu" đúng ngữ cảnh không — tức là đã fetch rồi mà vẫn không xem được?
