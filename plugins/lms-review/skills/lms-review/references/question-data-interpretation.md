# Question Data Interpretation Guide

Tài liệu này chứa phần dùng chung cho cả `lms_get_revise` và `lms_get_practice` ở cấp câu hỏi.

## Khi nào đọc file này

- Khi cần hiểu nghĩa của `questions[]`, `answers[]`, media, và `structural_flags`.
- Khi chưa rõ thứ tự đọc dữ liệu và bằng chứng ở từng câu.
- Khi thấy mâu thuẫn giữa đề bài, đáp án, lời giải, hoặc media.
- Không dùng file này để bê nguyên tên field kỹ thuật vào câu trả lời cuối.

## Quick Reading Order Cho Mỗi Câu

1. `content_text`
2. media của câu (`context_images`, `audio_url`)
3. `solution_text` và media trong lời giải
4. `answers[]` và media/audio của từng phương án hoặc phát biểu
5. `structural_flags` để bắt lỗi cấu trúc chắc chắn

## Media Evidence Rules (bắt buộc)

Media của từng câu nằm ở:

- `context_images[]`
- Placeholder `[image: URL]` trong `solution_text`
- `audio_url`
- `answers[].answer_image_url`
- `answers[].answer_audio_url`

Quy trình bắt buộc cho mỗi câu:

1. Collect đủ URL từ các nguồn trên.
2. Deduplicate theo từng câu.
3. Fetch bằng `scripts/fetch_images.py`. Nếu muốn manifest tự giữ vai trò media thì phải dùng structured input với `url`, `question_index`, `media_role`, `source_field`, và `answer_index` nếu áp dụng. `--url` trần chỉ phù hợp khi LLM tự giữ mapping role ở ngoài script.
   - `context_images[]` -> `media_role = "question"`, `source_field = "context_images"`
   - Placeholder `[image: URL]` trong `solution_text` -> `media_role = "solution"`, `source_field = "solution_text"`
   - `audio_url` -> `media_role = "question"`, `source_field = "audio_url"`
   - `answers[].answer_image_url` -> `media_role = "answer"`, `source_field = "answers.answer_image_url"`, kèm `answer_index`
   - `answers[].answer_audio_url` -> `media_role = "answer"`, `source_field = "answers.answer_audio_url"`, kèm `answer_index`
4. Giữ manifest map `URL -> local_path` và ghi rõ media đó thuộc đề bài, lời giải, hay phương án.
5. Sau khi có manifest, gắn lại media local đúng chỗ:
   - `media_role = "question"` -> đọc cùng `content_text`
   - `media_role = "solution"` -> đọc cùng `solution_text`
   - `media_role = "answer"` + `answer_index = N` -> đọc cùng item trong `answers[]` có `answer_index = N`
6. Mở media local và kiểm tra nội dung thực tế trước khi kết luận câu.

Không được kết luận chỉ dựa trên việc nhìn URL như chuỗi text.

Chỉ được nói `chưa đủ dữ liệu để kết luận chắc chắn` khi fetch/open media thất bại hoặc môi trường không xem được.

## Field Semantics Cấp Câu

- `index`: số thứ tự câu; khi viết cho user dùng `Câu 1`, `Câu 2`, ...
- `question_id`: ID của câu hỏi.
- `type_code`: loại câu kỹ thuật, dùng cho suy luận nội bộ.
- `content_text`: nội dung đề đã clean.
- `solution_text`: lời giải đã clean + có thể chứa placeholder ảnh.
- `context_images`, `audio_url`: media của đề.
- `answers`: phương án/phát biểu sau normalize.
- `structural_flags`: lỗi cấu trúc có độ tin cậy cao.

## Field Semantics Cấp Đáp Án

- `answer_index`: thứ tự phương án.
- `content`: nội dung phương án/phát biểu.
- `is_true`: trạng thái đúng/sai đang cài trong hệ thống, không phải tri thức đã xác minh.
- `answer_image_url`, `answer_audio_url`: media của phương án.

## Phụ thuộc quan trọng giữa các field

- `type_code` quyết định cách đọc `answers`:
  - `free_text`: coi là câu tự luận; `answers` rỗng là hợp lệ.
  - `single_choice`: cần đối chiếu giữa phương án, lời giải, và setup đáp án.
  - `multi_true_false`: đọc từng phương án như phát biểu riêng.
- `content_text` + media đề + `solution_text` là một cụm bằng chứng; không tách rời khi đánh giá.
- Không có `structural_flags` không có nghĩa là câu chắc chắn đúng.

## Các lỗi hiểu sai thường gặp

- Xem `is_true` như “sự thật kiến thức”.
- Thấy `answers = []` ở `free_text` rồi kết luận thiếu đáp án.
- Thấy `[image: URL]` trong `solution_text` rồi kết luận thiếu lời giải mà chưa mở ảnh.
- Không thử fetch media nhưng vẫn nói thiếu dữ liệu.

## Guardrails cho câu trả lời cuối

- Dùng file này để hiểu dữ liệu, không copy tên field kỹ thuật ra ngoài.
- Khi trả lời user, đổi sang ngôn ngữ đời thường và chỉ nêu kết luận có bằng chứng.
