# Checklist Kiểm Thử API (Swagger / Postman)

Checklist này cung cấp các kịch bản kiểm thử (test cases) từ luồng đúng (Positive) đến luồng lỗi (Negative) để xác minh tính ổn định, bảo mật và phân quyền của toàn bộ hệ thống API.

---

## 🔑 1. Nhóm API AUTH (Xác thực)

### [POST] Đăng ký tài khoản (`/auth/register`)
- [ ] **Case Đúng**: Đăng ký với Email chưa tồn tại, mật khẩu từ 6-30 ký tự, họ tên từ 3-50 ký tự.
  - *Kỳ vọng*: Trả về `201 Created`, chứa thông tin user (đã ẩn `password_hash`).
- [ ] **Case Lỗi (Trùng lặp)**: Gửi lại email đã đăng ký ở bước trước.
  - *Kỳ vọng*: Trả về `400 Bad Request` ("Email đã tồn tại").
- [ ] **Case Lỗi (Validation)**: Gửi email sai định dạng (ví dụ: `abc`), mật khẩu quá ngắn (<6 kí tự), hoặc tên quá dài.
  - *Kỳ vọng*: Trả về `422 Unprocessable Entity` của Pydantic.

### [POST] Đăng nhập tài khoản (`/auth/login`)
- [ ] **Case Đúng**: Nhập đúng email và mật khẩu.
  - *Kỳ vọng*: Trả về `200 OK`, chứa `access_token` và `refresh_token`.
- [ ] **Case Lỗi (Sai mật khẩu/email)**: Nhập sai mật khẩu hoặc email không tồn tại.
  - *Kỳ vọng*: Trả về `401 Unauthorized` ("Email hoặc mật khẩu không chính xác").

### [POST] Làm mới Token (`/auth/refresh`)
- [ ] **Case Đúng**: Truyền `refresh_token` hợp lệ thu được từ đăng nhập vào query parameter.
  - *Kỳ vọng*: Trả về `200 OK` chứa một `access_token` mới.
- [ ] **Case Lỗi (Sai loại Token)**: Truyền `access_token` vào API refresh.
  - *Kỳ vọng*: Trả về `401 Unauthorized` ("Token này không phải là Refresh Token hợp lệ").
- [ ] **Case Lỗi (Token hết hạn/Hỏng)**: Truyền token bị sửa đổi hoặc hết hạn.
  - *Kỳ vọng*: Trả về `401 Unauthorized`.

---

## 👤 2. Nhóm API USER (Thông tin Cá nhân & Quản trị)

### [GET] Lấy thông tin cá nhân (`/user/`)
- [ ] **Case Đúng**: Gửi kèm `access_token` hợp lệ trong header Authorization.
  - *Kỳ vọng*: Trả về `200 OK` chứa thông tin chi tiết và mới nhất của người dùng hiện tại từ Database.
- [ ] **Case Lỗi (Không gửi token)**: Gọi API không truyền Access Token.
  - *Kỳ vọng*: Trả về `401 Unauthorized` (HTTPBearer).

### [GET] Danh sách người dùng của Admin (`/admin/users`)
- [ ] **Case Đúng**: Đăng nhập tài khoản có role `ADMIN` -> Gọi API lấy danh sách.
  - *Kỳ vọng*: Trả về `200 OK` danh sách toàn bộ người dùng trong hệ thống kèm tổng số lượng.
- [ ] **Case Lỗi (Sai quyền)**: Đăng nhập tài khoản có role `USER` -> Gọi API này.
  - *Kỳ vọng*: Trả về `401 Unauthorized` ("Quyền admin không hợp lệ").
- [ ] **Case Đúng (Bộ lọc)**: Thử tìm kiếm với `?name=Nguyen` hoặc `?is_active=true` để kiểm duyệt kết quả lọc.

---

## 📁 3. Nhóm API PROJECT (Dự án & Thành viên)

### [POST] Tạo dự án mới (`/project/`)
- [ ] **Case Đúng**: Đăng nhập -> Gửi tên dự án và mô tả.
  - *Kỳ vọng*: Trả về `201 Created` chứa thông tin dự án, đồng thời tự động thêm người tạo làm `OWNER` trong bảng `project_members`.

### [GET] Lấy danh sách dự án (`/project/`)
- [ ] **Case Đúng (Không tìm kiếm)**: Trả về danh sách dự án người dùng tham gia/sở hữu.
- [ ] **Case Đúng (Tìm kiếm)**: Truyền `?search_name_project=Alpha` -> Chỉ trả về dự án có tên chứa chữ "Alpha".
- [ ] **Case Đúng (Đã xóa mềm)**: Dự án bị xóa mềm (`is_deleted = True`) không được xuất hiện trong danh sách này.

### [POST] Thêm thành viên vào dự án (`/project/{id}/members`)
- [ ] **Case Đúng**: OWNER dự án -> Thêm một `user_id` tồn tại với vai trò `MEMBER`.
  - *Kỳ vọng*: Trả về `201 Created`.
- [ ] **Case Lỗi (Sai quyền)**: MEMBER dự án thực hiện -> Trả về `403 Forbidden` ("Bạn không có quyền thêm thành viên mới").
- [ ] **Case Lỗi (User không tồn tại)**: Thêm một `user_id` không tồn tại -> Trả về `404 Not Found`.
- [ ] **Case Lỗi (Trùng lặp)**: Thêm một người đã có sẵn trong dự án -> Trả về `400 Bad Request` ("Người dùng này đã tham gia dự án rồi").

### [GET] Danh sách thành viên trong dự án (`/project/{id}/members`)
- [ ] **Case Đúng**: Thành viên dự án (Owner/Member) gọi API.
  - *Kỳ vọng*: Trả về `200 OK` chứa danh sách thành viên (làm phẳng JSON gồm email, tên, vai trò trong dự án).
- [ ] **Case Lỗi (Xem trộm)**: Người ngoài dự án gọi API -> Trả về `403 Forbidden` ("Bạn không có quyền xem danh sách thành viên của dự án này").

### [DELETE] Xóa thành viên khỏi dự án (`/project/{id}/members/{user_id}`)
- [ ] **Case Đúng**: OWNER thực hiện xóa một member.
  - *Kỳ vọng*: Trả về `200 OK` ("Xóa thành viên khỏi dự án thành công!").
- [ ] **Case Lỗi (Xóa OWNER)**: OWNER tự xóa mình hoặc xóa OWNER khác -> Trả về `400 Bad Request` ("Không thể xóa chủ sở hữu dự án").
- [ ] **Case Lỗi (Sai quyền)**: MEMBER thực hiện xóa -> Trả về `403 Forbidden`.

### [DELETE] Xóa mềm dự án (`/project/{id}`)
- [ ] **Case Đúng**: OWNER thực hiện xóa dự án.
  - *Kỳ vọng*: Trả về `200 OK`. (Dữ liệu vẫn còn trong DB nhưng `is_deleted = True` và `deleted_at` có giá trị).
- [ ] **Case Lỗi (Sai quyền)**: MEMBER yêu cầu xóa dự án -> Trả về `403 Forbidden`.

---

## 📝 4. Nhóm API TASK (Công việc, Bình luận & Đính kèm)

### [POST] Tạo công việc mới (`/task/project/{id}`)
- [ ] **Case Đúng (OWNER giao việc)**: OWNER tạo task và gán `assignee_id` cho một member bất kỳ trong dự án.
- [ ] **Case Đúng (MEMBER tự giao việc)**: MEMBER tạo task và gán `assignee_id` bằng chính ID của mình, hoặc để trống (`null`).
- [ ] **Case Lỗi (MEMBER giao việc cho người khác)**: MEMBER gán `assignee_id` bằng ID của người khác -> Trả về `403 Forbidden`.
- [ ] **Case Lỗi (Giao cho người ngoài dự án)**: Gán `assignee_id` cho một user không tham gia dự án -> Trả về `400 Bad Request`.
- [ ] **Case Lỗi (Không thuộc dự án)**: Người ngoài dự án gọi tạo task -> Trả về `403 Forbidden`.

### [GET] Danh sách công việc của dự án (`/task/project/{id}`)
- [ ] **Case Đúng**: Lấy danh sách task kèm các bộ lọc `?status=TODO&priority=HIGH&search=Database&page=1&limit=5`.
  - *Kỳ vọng*: Trả về `200 OK` kèm cấu trúc phân trang (`tasks`, `total`, `page`, `limit`).
- [ ] **Case Lỗi (Xem trộm)**: Người ngoài dự án gọi -> Trả về `403 Forbidden`.

### [GET] Chi tiết công việc (`/task/{id}`)
- [ ] **Case Đúng**: Thành viên dự án xem chi tiết task thuộc dự án.
  - *Kỳ vọng*: Trả về `200 OK` chi tiết task.
- [ ] **Case Lỗi (Xem trộm)**: Người ngoài dự án gọi xem chi tiết task -> Trả về `403 Forbidden`.

### [PATCH] Cập nhật công việc (`/task/{id}`)
- [ ] **Case Đúng (OWNER sửa toàn bộ)**: OWNER đổi tiêu đề, độ ưu tiên, hạn chót và giao việc cho người khác -> Trả về `200 OK`.
- [ ] **Case Đúng (MEMBER đổi trạng thái)**: MEMBER đổi trạng thái `status: "IN_PROGRESS"` -> Trả về `200 OK`.
- [ ] **Case Lỗi (MEMBER sửa trường cấm)**: MEMBER đổi tiêu đề hoặc gán việc cho người khác -> Trả về `422 Unprocessable Entity` (báo lỗi ValidationError của Pydantic).

### [DELETE] Xóa công việc (`/task/{id}`)
- [ ] **Case Đúng**: OWNER thực hiện xóa task -> Trả về `200 OK` và dữ liệu bị xóa khỏi database.
- [ ] **Case Lỗi (MEMBER xóa)**: MEMBER thực hiện xóa task -> Trả về `403 Forbidden`.

### [POST] Viết bình luận cho task (`/task/{id}/comments`)
- [ ] **Case Đúng**: Thành viên dự án bình luận thành công -> Trả về `201 Created` kèm thông tin bình luận và họ tên người dùng.
- [ ] **Case Lỗi (Không thuộc dự án)**: Người ngoài dự án bình luận -> Trả về `403 Forbidden`.

### [GET] Lấy danh sách bình luận (`/task/{id}/comments`)
- [ ] **Case Đúng**: Thành viên dự án xem danh sách bình luận sắp xếp theo thời gian tăng dần -> Trả về `200 OK`.

### [POST] Tải lên tệp đính kèm (`/task/{id}/attachments`)
- [ ] **Case Đúng**: Thành viên dự án tải lên tệp tin hợp lệ dưới 5MB (ví dụ PDF, PNG) -> Trả về `201 Created` và lưu file trên ổ đĩa server.
- [ ] **Case Lỗi (Quá kích thước)**: Tải lên file > 5MB -> Trả về `400 Bad Request`.
- [ ] **Case Lỗi (Sai định dạng)**: Tải lên file `.exe`, `.py` -> Trả về `400 Bad Request`.

### [GET] Lấy danh sách tệp đính kèm (`/task/{id}/attachments`)
- [ ] **Case Đúng**: Thành viên dự án xem danh sách toàn bộ các file đính kèm của task -> Trả về `200 OK`.
