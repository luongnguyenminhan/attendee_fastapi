# Attendee FastAPI - API Documentation

## Tổng quan

Attendee FastAPI là hệ thống quản lý meeting bots với kiến trúc Clean Architecture. Sau khi migrate từ PostgreSQL sang MySQL và gộp admin module vào các modules chính, hệ thống hiện có:

- **4 modules chính**: Users, Bots, Organizations, Projects  
- **1 module system**: Cho dashboard và settings
- **Admin APIs** được phân tán vào từng module tương ứng
- **Comprehensive logging** cho tất cả admin operations

## Base URL

```
http://localhost:8000
```

## Authentication

Hiện tại sử dụng simplified admin authentication. Production cần implement proper JWT/OAuth.

---

## 🏥 Health Check

### GET /health
Kiểm tra trạng thái hệ thống

**Response:**
```json
{
  "status": "healthy",
  "message": "Attendee FastAPI is running",
  "version": "0.1.0"
}
```

---

## 👥 Users Module

### Public APIs

#### POST /api/v1/auth/login
Đăng nhập người dùng

#### POST /api/v1/auth/register  
Đăng ký tài khoản mới

#### GET /api/v1/users/
Lấy danh sách users (có phân trang)

**Query Parameters:**
- `page`: Trang (default: 1)
- `page_size`: Số items per page (default: 10, max: 100)

#### GET /api/v1/users/{user_id}
Lấy thông tin user theo ID

#### PUT /api/v1/users/{user_id}
Cập nhật thông tin user

#### DELETE /api/v1/users/{user_id}
Xóa user (soft delete)

#### POST /api/v1/users/{user_id}/activate
Kích hoạt tài khoản user

#### POST /api/v1/users/{user_id}/deactivate
Vô hiệu hóa tài khoản user

### Admin APIs

#### GET /api/v1/admin/users/
Admin lấy danh sách users với filtering nâng cao

**Query Parameters:**
- `page`: Trang (default: 1)
- `page_size`: Số items (default: 50, max: 100)  
- `search`: Tìm kiếm theo email/username
- `status`: Filter theo trạng thái (active/inactive)
- `role`: Filter theo role (admin/user)
- `organization_id`: Filter theo organization

**Response Example:**
```json
{
  "users": [
    {
      "id": "uuid",
      "email": "user@example.com",
      "username": "username",
      "name": "Full Name",
      "first_name": "First",
      "last_name": "Last",
      "is_active": true,
      "is_superuser": false,
      "is_email_verified": true,
      "status": "active",
      "role": "user",
      "organization_id": "uuid",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 100,
  "page": 1,
  "page_size": 50,
  "total_pages": 2
}
```

#### POST /api/v1/admin/users/create
Admin tạo user mới với comprehensive logging

**Form Data:**
- `email`: Email (required)
- `username`: Username (required)
- `password`: Password (required)
- `first_name`: Tên (optional)
- `last_name`: Họ (optional)
- `role`: Role - "user" hoặc "admin" (default: "user")
- `organization_id`: Organization UUID (optional)

#### GET /api/v1/admin/users/{user_id}
Admin lấy chi tiết user

#### POST /api/v1/admin/users/{user_id}/activate
Admin kích hoạt user

#### POST /api/v1/admin/users/{user_id}/deactivate
Admin vô hiệu hóa user

#### DELETE /api/v1/admin/users/{user_id}
Admin xóa user

---

## 🤖 Bots Module

### Public APIs

#### POST /api/v1/bots/
Tạo bot mới

**Request Body:**
```json
{
  "name": "Bot Name",
  "meeting_url": "https://meet.google.com/abc-def-ghi",
  "project_id": "uuid",
  "meeting_uuid": "meeting-uuid",
  "settings": {},
  "join_at": "2024-01-01T10:00:00Z"
}
```

#### GET /api/v1/bots/project/{project_id}
Lấy bots theo project

**Query Parameters:**
- `state`: Filter theo trạng thái bot
- `search`: Tìm kiếm theo tên
- `page`: Trang
- `size`: Số items per page

#### GET /api/v1/bots/{bot_id}
Lấy thông tin bot theo ID

#### PATCH /api/v1/bots/{bot_id}
Cập nhật bot

#### DELETE /api/v1/bots/{bot_id}
Xóa bot

#### POST /api/v1/bots/{bot_id}/join
Cho bot join meeting

#### POST /api/v1/bots/{bot_id}/leave
Cho bot leave meeting

#### POST /api/v1/bots/{bot_id}/start-recording
Bắt đầu recording

#### GET /api/v1/bots/{bot_id}/stats
Lấy thống kê bot

#### GET /api/v1/bots/{bot_id}/events
Lấy events của bot

### Admin APIs

#### GET /api/v1/admin/bots/
Admin lấy danh sách bots với filtering nâng cao

**Query Parameters:**
- `page`, `page_size`: Phân trang
- `search`: Tìm kiếm
- `state`: Filter theo state
- `project_id`: Filter theo project
- `organization_id`: Filter theo organization

#### GET /api/v1/admin/bots/stats
Admin lấy thống kê tổng quan bots

#### GET /api/v1/admin/bots/{bot_id}
Admin lấy chi tiết bot

#### POST /api/v1/admin/bots/{bot_id}/force-leave
Admin ép bot leave meeting

#### DELETE /api/v1/admin/bots/{bot_id}
Admin xóa bot

#### GET /api/v1/admin/bots/{bot_id}/events
Admin lấy events của bot

---

## 🏢 Organizations Module

### Public APIs

#### POST /api/v1/organizations/
Tạo organization mới

#### GET /api/v1/organizations/
Lấy danh sách organizations

#### GET /api/v1/organizations/{organization_id}
Lấy thông tin organization

#### PATCH /api/v1/organizations/{organization_id}
Cập nhật organization

#### DELETE /api/v1/organizations/{organization_id}
Xóa organization

#### POST /api/v1/organizations/{organization_id}/credits
Quản lý credits

#### POST /api/v1/organizations/{organization_id}/suspend
Suspend organization

#### POST /api/v1/organizations/{organization_id}/activate
Activate organization

### Admin APIs

#### GET /api/v1/admin/organizations/
Admin lấy danh sách organizations

**Query Parameters:**
- `page`, `page_size`: Phân trang
- `search`: Tìm kiếm theo tên
- `status`: Filter theo trạng thái

#### GET /api/v1/admin/organizations/stats
Admin lấy thống kê organizations

#### GET /api/v1/admin/organizations/low-credits
Admin lấy organizations có credits thấp

**Query Parameters:**
- `threshold`: Ngưỡng credits (default: 100)

#### GET /api/v1/admin/organizations/{organization_id}
Admin lấy chi tiết organization

#### POST /api/v1/admin/organizations/{organization_id}/credits
Admin quản lý credits

**Form Data:**
- `amount`: Số credits
- `operation`: "add" hoặc "deduct"

#### POST /api/v1/admin/organizations/{organization_id}/suspend
Admin suspend organization

#### POST /api/v1/admin/organizations/{organization_id}/activate  
Admin activate organization

#### DELETE /api/v1/admin/organizations/{organization_id}
Admin xóa organization

---

## 📋 Projects Module

### Public APIs

#### POST /api/v1/projects/
Tạo project mới

#### GET /api/v1/projects/organization/{organization_id}
Lấy projects theo organization

#### GET /api/v1/projects/{project_id}
Lấy thông tin project

#### PATCH /api/v1/projects/{project_id}
Cập nhật project

#### DELETE /api/v1/projects/{project_id}
Xóa project

#### POST /api/v1/projects/{project_id}/archive
Archive project

#### POST /api/v1/projects/{project_id}/activate
Activate project

#### GET /api/v1/projects/{project_id}/stats
Lấy thống kê project

#### POST /api/v1/projects/{project_id}/api-keys
Tạo API key

#### GET /api/v1/projects/{project_id}/api-keys
Lấy danh sách API keys

### Admin APIs

#### GET /api/v1/admin/projects/
Admin lấy danh sách projects

**Query Parameters:**
- `page`, `page_size`: Phân trang
- `search`: Tìm kiếm
- `status`: Filter theo status
- `organization_id`: Filter theo organization

#### GET /api/v1/admin/projects/stats
Admin lấy thống kê tổng quan projects

#### GET /api/v1/admin/projects/{project_id}
Admin lấy chi tiết project

#### GET /api/v1/admin/projects/{project_id}/stats
Admin lấy thống kê individual project

#### POST /api/v1/admin/projects/{project_id}/archive
Admin archive project

#### POST /api/v1/admin/projects/{project_id}/activate
Admin activate project

#### DELETE /api/v1/admin/projects/{project_id}
Admin xóa project

#### GET /api/v1/admin/projects/{project_id}/api-keys
Admin lấy API keys của project

---

## ⚙️ System Module (Admin Dashboard)

### Admin APIs

#### GET /api/v1/admin/dashboard
Admin dashboard với thống kê tổng quan

**Response Example:**
```json
{
  "success": true,
  "data": {
    "total_users": 150,
    "active_users": 120,
    "total_organizations": 25,
    "active_organizations": 20,
    "total_projects": 75,
    "active_projects": 60,
    "total_bots": 200,
    "active_bots": 15,
    "webhook_deliveries": 1250,
    "transcriptions": 500,
    "celery_workers": 2,
    "active_pods": 5
  }
}
```

#### GET /api/v1/admin/settings
Admin lấy system settings

**Response Example:**
```json
{
  "success": true,
  "data": {
    "system": {
      "maintenance_mode": false,
      "registration_enabled": true,
      "email_verification_required": true,
      "max_users_per_organization": 100,
      "default_credits": 1000
    },
    "webhooks": {
      "enabled": true,
      "timeout_seconds": 30,
      "retry_attempts": 3,
      "batch_size": 100
    },
    "bots": {
      "max_concurrent_bots": 10,
      "default_recording_duration": 3600,
      "auto_leave_timeout": 7200
    },
    "transcription": {
      "default_provider": "deepgram",
      "language": "en",
      "real_time": true
    }
  }
}
```

#### GET /api/v1/admin/webhooks
Admin lấy webhook deliveries

**Query Parameters:**
- `page`, `page_size`: Phân trang
- `status`: Filter theo status

#### GET /api/v1/admin/transcriptions
Admin lấy transcription information

#### GET /api/v1/admin/health
Admin system health check

**Response Example:**
```json
{
  "success": true,
  "data": {
    "database": {
      "status": "healthy",
      "response_time_ms": 25,
      "connections": 5,
      "max_connections": 100
    },
    "redis": {
      "status": "healthy",
      "response_time_ms": 5,
      "memory_usage_mb": 45,
      "max_memory_mb": 512
    },
    "celery": {
      "status": "healthy",
      "active_workers": 2,
      "pending_tasks": 0,
      "failed_tasks": 0
    },
    "storage": {
      "status": "healthy",
      "disk_usage_gb": 25,
      "disk_total_gb": 100
    }
  }
}
```

---

## 🔌 WebSocket

#### GET /api/v1/websocket/
WebSocket connection cho real-time communication

---

## 📊 Logging & Monitoring

### Admin Logging Features

Tất cả admin APIs có **comprehensive logging** với:

#### 🔍 Request Logging
- Input parameters và current user
- Pagination, search, filter parameters
- Form data validation

#### 📈 Processing Logging  
- Database query steps
- Repository method calls
- Data transformation steps
- Business logic execution

#### ✅ Success Logging
- Response data summary
- Performance metrics
- Success indicators với emojis

#### ❌ Error Logging
- Exception types và messages
- Full stack traces
- Database rollback confirmation
- Error categorization

#### 📋 Log Examples

**User Creation:**
```
=== ADMIN CREATE USER REQUEST ===
Email: test@example.com
Username: testuser
Password length: 10
Role: user
Current user: {'username': 'admin', 'email': 'admin@attendee.dev'}
==================================

=== VALIDATION STEP ===
Email cleaned: 'test@example.com'
Username cleaned: 'testuser'
Password provided: True
=======================

=== CHECKING EMAIL UNIQUENESS ===
Email 'test@example.com' exists: False

=== CHECKING USERNAME UNIQUENESS ===
Username 'testuser' exists: False

=== CREATING USER OBJECT ===
✅ User object created:
   - Email: test@example.com
   - Username: testuser
   - Is superuser: False

=== DATABASE OPERATIONS ===
1. Adding user to session...
2. Flushing to get ID...
3. Refreshing user object...
   - Generated User ID: 18eaa8bc-2e7f-4735-9c8b-e00a2f242b88
4. Committing transaction...
✅ User created successfully in database

🎉 SUCCESS: Returning 201 response
========================================
```

---

## 🚀 Migration Notes

### Admin Module Migration

**Đã hoàn thành:**
✅ Gộp admin APIs vào các modules tương ứng  
✅ Tạo system module cho dashboard  
✅ Thêm comprehensive logging cho tất cả admin operations  
✅ Cập nhật main.py với admin routes mới  
✅ Xóa module admin cũ khỏi codebase  
✅ Chuyển từ PostgreSQL sang MySQL với PyMySQL  
✅ AsyncSessionWrapper cho sync/async compatibility  

**Kết quả:**
- Clean Architecture maintained
- Admin functionality distributed logically  
- Comprehensive monitoring via logging
- No functional regressions
- Better separation of concerns

---

## 🛠️ Development

### Running the Application

```bash
# Start with Docker Compose
docker-compose up -d

# Check logs
docker-compose logs attendee-app

# Access APIs
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/admin/dashboard
```

### Testing Admin APIs

```bash
# Test admin user creation
curl -X POST http://localhost:8000/api/v1/admin/users/create \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "email=test@example.com&username=testuser&password=password123&first_name=Test&last_name=User&role=user"

# Test admin dashboard
curl http://localhost:8000/api/v1/admin/dashboard

# Test admin users list
curl "http://localhost:8000/api/v1/admin/users/?page=1&page_size=10"
```

### Database

- **Engine**: MySQL 8.0 với PyMySQL driver
- **Connection**: mysql+pymysql://admin:11minhan@mysql:3306/attendee_fastapi_db
- **Features**: Real CRUD operations, migration từ PostgreSQL hoàn tất

### Monitoring

- **Logs**: Docker logs `docker-compose logs attendee-app`
- **Database**: Adminer tại http://localhost:8080
- **Health**: GET /health endpoint
- **Admin Health**: GET /api/v1/admin/health

---

## 📝 API Response Formats

### Success Response
```json
{
  "success": true,
  "data": { ... },
  "message": "Operation completed successfully"
}
```

### Error Response  
```json
{
  "success": false,
  "message": "Error description",
  "error": "Detailed error info"
}
```

### Paginated Response
```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "page_size": 50,
  "total_pages": 2
}
``` 