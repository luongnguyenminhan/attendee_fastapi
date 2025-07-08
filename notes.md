# Code Formatting Script

## Đã hoàn thành:
- ✅ Tạo bash script `format_code.sh` 
- ✅ Cấp quyền thực thi cho script

## Cách sử dụng:
```bash
./format_code.sh
```

## Script sẽ chạy:
- `ruff format --select I .` - Format imports
- `ruff format .` - Format toàn bộ documents 
- `ruff check --fix .` - Fix tất cả lỗi tự động

## Để test:
- [ ] Chạy script và kiểm tra kết quả
- [ ] Xem git diff để xem những thay đổi
- [ ] Commit nếu hài lòng với kết quả 