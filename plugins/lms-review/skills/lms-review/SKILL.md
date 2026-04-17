---
name: lms-review
description: Use when the user asks for an audit or quality review of LMS revise/practice questions.
---

# LMS Review

## Overview

Audit chất lượng câu hỏi `revise`/`practice` theo ngôn ngữ đời thường, nhưng dựa trên bằng chứng từ dữ liệu chuẩn hóa và media thực tế.

## Required Workflow

1. Xác định domain + ID (`revise` hoặc `practice`) và gọi tool tương ứng:
   - `lms_get_revise(revise_id)`
   - `lms_get_practice(practice_id)`
   - Chỉ mở `references/revise-data-interpretation.md` khi cần hiểu sâu nghĩa field hoặc gặp mâu thuẫn dữ liệu trong revise.
   - Chỉ mở `references/practice-data-interpretation.md` khi cần hiểu sâu nghĩa field hoặc gặp mâu thuẫn dữ liệu trong practice.
   - Chỉ mở `references/question-data-interpretation.md` khi cần hiểu sâu nghĩa field hoặc gặp mâu thuẫn dữ liệu trong question.
2. Dùng `title` làm context cấp bài, sau đó review `questions[]` tuần tự từng câu theo `index`
3. Khi bắt đầu một câu, khóa phạm vi review vào đúng câu hiện tại. Chỉ sau khi câu này đã được đánh giá xong hoàn toàn mới được chuyển sang câu tiếp theo.
4. Với câu hiện tại, collect toàn bộ URL của riêng câu đó từ các nguồn sau:
   - `context_images[]`
   - placeholder `[image: URL]` trong `solution_text`
   - `audio_url`
   - `answers[].answer_image_url`
   - `answers[].answer_audio_url`
5. Deduplicate URL theo từng câu, rồi fetch toàn bộ media của câu đó bằng script. Khi cần manifest map đúng vai trò media trong câu, dùng structured input thay vì truyền `--url` trần.

   LLM phải map structured input theo đúng quy tắc sau:
   - URL lấy từ `context_images[]` -> `media_role = "question"` và `source_field = "context_images"`
   - URL scan từ placeholder `[image: URL]` trong `solution_text` -> `media_role = "solution"` và `source_field = "solution_text"`
   - URL lấy từ `audio_url` -> `media_role = "question"` và `source_field = "audio_url"`
   - URL lấy từ `answers[].answer_image_url` -> `media_role = "answer"` và `source_field = "answers.answer_image_url"` + giữ `answer_index`
   - URL lấy từ `answers[].answer_audio_url` -> `media_role = "answer"` và `source_field = "answers.answer_audio_url"` + giữ `answer_index`

```json
{
  "items": [
    {
      "url": "https://example.com/question.png",
      "question_index": 1,
      "media_role": "question",
      "source_field": "context_images"
    },
    {
      "url": "https://example.com/solution.png",
      "question_index": 1,
      "media_role": "solution",
      "source_field": "solution_text"
    },
    {
      "url": "https://example.com/answer-a.png",
      "question_index": 1,
      "media_role": "answer",
      "source_field": "answers.answer_image_url",
      "answer_index": 1
    }
  ]
}
```

```bash
python scripts/fetch_images.py \
  --input-json media-items.json
```

   Chỉ dùng `--url` trần cho mode tải nhanh khi bạn tự giữ mapping role ở ngoài script. Không dùng mode này nếu muốn manifest tự giữ `question/solution/answer`.

6. Giữ manifest của câu hiện tại để map `URL -> local_path` và map thêm vai trò của từng media:
   - media đề bài
   - media lời giải
   - media phương án / phát biểu
7. Sau khi fetch xong, LLM phải đọc manifest và gắn media local đúng chỗ trước khi review:
   - item có `media_role = "question"` -> đọc cùng `content_text`
   - item có `media_role = "solution"` -> đọc cùng `solution_text`
   - item có `media_role = "answer"` + `answer_index = N` -> đọc cùng item trong `answers[]` có `answer_index = N`
8. Đọc đề bài của câu hiện tại từ `content_text`, kết hợp `title` và media đề bài đã tải để hiểu đầy đủ câu hỏi trước khi kết luận bất cứ điều gì.
9. Đọc `solution_text` và media lời giải của chính câu đó để hiểu lời giải đầy đủ; nếu lời giải nằm trong ảnh thì phải đọc ảnh lời giải trước.
10. Xác định `type_code` của câu hiện tại để biết cách đọc và đánh giá câu.
11. Nếu `type_code != free_text`, đọc toàn bộ `answers[]` cùng media/audio của từng phương án hoặc từng phát biểu; nếu `type_code = free_text`, coi là câu tự luận và không suy diễn đáp án từ `answers`.
12. Sau khi đã hiểu đề bài, lời giải, loại câu, và các phương án (nếu có), đánh giá tính đúng đắn và tính nhất quán giữa:
   - câu hỏi
   - lời giải
   - phương án / phát biểu
   - media
   - setup đáp án hiện tại
13. Nếu cần siết tiêu chí hoặc chốt severity, đọc `references/review-checklist.md`. Chỉ khi câu hiện tại đã được review xong hoàn toàn mới chuyển sang câu tiếp theo. Sau khi đã review hết toàn bộ câu, mới tổng hợp kết quả toàn bài; khi cần chuẩn hóa cách viết non-technical thì đọc `references/user-facing-writing.md`.

## Rules

- Có media (ảnh/audio) thì phải fetch và kiểm tra media trước khi kết luận câu.
- Manifest của từng câu phải giữ được cả `URL -> local_path` và vai trò của media trong câu đó.
- Trường `is_true` trong `answers` chỉ là trạng thái đang cài trong hệ thống, không phải sự thật đã kiểm chứng.
- Câu hỏi có `type_code` là `free_text`, coi là câu tự luận; không suy diễn đáp án từ mảng `answers`.
- Chỉ nói `chưa đủ dữ liệu để kết luận chắc chắn` khi fetch/open media thất bại hoặc môi trường không xem được.
- `structural_flags` là tín hiệu lỗi chắc chắn, nhưng không thay thế việc tự đọc câu hỏi/lời giải/media.
- Câu trả lời cuối cho user phải non-technical, không được nói thuật ngữ field/schema nội bộ. Sẽ được diễn giải bằng ngôn ngữ tự nhiên.

## Output Contract

- Luôn có: `Kết luận tổng thể`, `Thống kê nhanh`, `Checklist tiêu chí đã kiểm`.
- `Kết luận tổng thể` chỉ dùng một trong ba trạng thái: `Đạt` | `Cần sửa` | `Lỗi nghiêm trọng`.
- Chỉ liệt kê chi tiết các câu có vấn đề; gọi theo dạng `Câu 1`, `Câu 2`, ...
- Mỗi câu có lỗi dùng đúng khung: `Mức độ` / `Mô tả` / `Bằng chứng` / `Đề xuất sửa`.
  - `Mức độ`: `Nghiêm trọng` | `Trung bình` | `Nhẹ`
     + Sắp xếp theo thứ tự: Nghiêm trọng -> Trung bình -> Nhẹ
  - `Mô tả`: Mô tả chi tiết vấn đề
  - `Bằng chứng`: Bằng chứng cụ thể từ câu hỏi/lời giải/media
  - `Đề xuất sửa`: Đề xuất sửa cụ thể, chi tiết
- Kết thúc bằng `Khuyến nghị ưu tiên chỉnh sửa`: `Sửa ngay` / `Nên sửa` / `Cần rà soát thêm`.

## References

Chỉ đọc file nào cần cho case hiện tại, không bắt buộc load tất cả từ đầu.

- `references/revise-data-interpretation.md`: nghĩa field cấp bài và lưu ý riêng của `revise`.
- `references/practice-data-interpretation.md`: nghĩa field cấp bài và lưu ý riêng của `practice`.
- `references/question-data-interpretation.md`: cách đọc `questions[]`, `answers[]`, media, và thứ tự review từng câu.
- `references/review-checklist.md`: rubric đánh giá đầy đủ + phân mức độ lỗi.
- `references/user-facing-writing.md`: quy tắc diễn đạt non-technical cho câu trả lời cuối.
