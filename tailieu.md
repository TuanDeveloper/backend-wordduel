# WordDuel — Đấu từ vựng tiếng Anh real-time

## 📦 Phase 0 — Chuẩn bị môi trường

- [ ] Cài Docker Desktop
- [ ] Chạy thử PostgreSQL bằng Docker (`docker run postgres`)
- [ ] Cài DBeaver hoặc TablePlus để xem dữ liệu trực quan
- [ ] Chạy thử Redis bằng Docker (`docker run redis`)
- [ ] Tạo repository GitHub
- [ ] Tạo cấu trúc thư mục `backend/` và `frontend/`

## 🗄️ Phase 1 — Database & Schema (PostgreSQL)

- [ ] Thiết kế các bảng:
  - [ ] `users`
  - [ ] `word_sets` — bộ từ vựng
  - [ ] `words` — từ, nghĩa, ví dụ
  - [ ] `rooms`
  - [ ] `room_players`
  - [ ] `submissions`
- [ ] Viết migration bằng Alembic
- [ ] Seed dữ liệu mẫu: 1 bộ từ vựng khoảng 20 từ để test

## 🔧 Phase 2 — Backend CRUD cơ bản

- [ ] API đăng ký / đăng nhập bằng JWT
- [ ] API CRUD cho `word_sets` và `words`
- [ ] API tạo phòng: `POST /rooms`
  - [ ] Sinh mã phòng
- [ ] API tham gia phòng: `POST /rooms/{code}/join`

## ⚡ Phase 3 — Real-time: WebSocket + Redis

- [ ] Viết `ConnectionManager` quản lý WebSocket theo `room_code`
- [ ] Broadcast danh sách người chơi khi có người vào hoặc rời phòng
- [ ] API nộp đáp án: `POST /rooms/{code}/submit`
  - [ ] So sánh đáp án đúng / sai
- [ ] Lưu tiến độ tạm thời vào Redis
  - [ ] Số câu đúng
  - [ ] Tổng số câu
- [ ] Broadcast `progress_update` real-time cho toàn bộ phòng
- [ ] Xác định người thắng
- [ ] Lưu kết quả vào PostgreSQL
- [ ] Test nhiều người nộp bài gần như cùng lúc
  - [ ] Làm quen với race condition ở quy mô nhỏ

## 🎨 Phase 4 — Frontend

- [ ] Trang đăng nhập / đăng ký
- [ ] Trang tạo và quản lý bộ từ vựng
- [ ] Trang phòng chờ (waiting room)
  - [ ] Hiển thị danh sách người chơi real-time
- [ ] Trang chơi
  - [ ] Hiển thị câu hỏi
  - [ ] Ô nhập hoặc chọn đáp án
  - [ ] Thanh tiến độ của tất cả người chơi
- [ ] Kết nối WebSocket bằng custom hook `useRoomSocket`
- [ ] Trang kết quả / bảng xếp hạng cuối ván

## 🐳 Phase 5 — Docker & Deploy

- [ ] Viết `Dockerfile` cho backend
- [ ] Viết `docker-compose.yml` kết nối backend, PostgreSQL và Redis
- [ ] Chạy toàn bộ hệ thống bằng một lệnh:

  ```bash
  docker-compose up