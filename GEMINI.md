# Rules for WordDuel Backend Development

Đây là tập hợp các quy tắc hoạt động mà Agent phải tuân thủ tuyệt đối khi làm việc trong dự án này:

1. **Không tự ý viết code hay sửa lỗi:** Khi có lỗi xảy ra hoặc người dùng đặt câu hỏi, chỉ giải thích nguyên nhân gốc rễ và hướng dẫn cách sửa. **Tuyệt đối không tự động apply code/fix bug** trừ khi người dùng ra lệnh rõ ràng "hãy code đi" hoặc "hãy sửa nó đi".
2. **Hỏi ý kiến trước khi thay đổi kiến trúc:** Trước khi tạo file mới, đổi cấu trúc thư mục, hoặc thay đổi logic nghiệp vụ quan trọng, phải liệt kê rõ ràng những gì định làm và chờ người dùng nói "đồng ý" mới được tiến hành.
3. **Tuân thủ chuẩn RESTful & Cấu trúc đã thống nhất:** Mọi API mới đều phải tuân theo cấu trúc đã chia (Models, Schemas, Routers, Services, Dependencies) và sử dụng hệ thống xử lý ngoại lệ (`ResponseSchema`, `Custom Exceptions`) đã được thiết lập.
