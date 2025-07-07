# Báo cáo phân tích mã nguồn dự án `attendee-labs/attendee`

## 1. Giới thiệu

Dự án `attendee-labs/attendee` là một mã nguồn mở cung cấp API để quản lý các bot họp trên các nền tảng như Zoom hoặc Google Meet. Mục tiêu chính của dự án là giúp các nhà phát triển dễ dàng tích hợp các tính năng ghi âm và chép lời cuộc họp vào sản phẩm của họ. Dự án được xây dựng trên nền tảng Django và sử dụng Docker để triển khai, với PostgreSQL và Redis là các dịch vụ bên ngoài.

Báo cáo này sẽ đi sâu vào cấu trúc dự án, các công nghệ được sử dụng, các dependencies, chức năng chính và các vấn đề tiềm ẩn. Ngoài ra, báo cáo cũng sẽ cung cấp hướng dẫn về cách chuyển đổi dự án từ Django sang FastAPI.

## 2. Công nghệ và Dependencies

Dự án này được phát triển chủ yếu bằng Python và sử dụng framework Django. Dưới đây là danh sách các thư viện và framework chính được tìm thấy trong `requirements.txt`:

### 2.1. Core Frameworks & Libraries

* **Django**: Framework web chính được sử dụng để xây dựng ứng dụng.
* **Django REST Framework (DRF)**: Mở rộng của Django để xây dựng các API RESTful.
* **Celery**: Hệ thống hàng đợi tác vụ phân tán, được sử dụng cho các tác vụ nền (background tasks) như xử lý ghi âm, chép lời.
* **Redis**: Cơ sở dữ liệu trong bộ nhớ, thường được sử dụng với Celery làm message broker và cache.
* **psycopg2**: Adapter PostgreSQL cho Python, dùng để kết nối với cơ sở dữ liệu PostgreSQL.
* **gunicorn**: WSGI HTTP Server cho Unix, dùng để phục vụ ứng dụng Django trong môi trường production.

### 2.2. Authentication & Authorization

* **django-allauth**: Bộ ứng dụng tích hợp để xử lý xác thực, đăng ký và quản lý tài khoản người dùng.
* **PyJWT**: Thư viện để mã hóa và giải mã JSON Web Tokens (JWT).
* **oauthlib** và **requests-oauthlib**: Hỗ trợ triển khai OAuth.

### 2.3. Cloud & Storage

* **boto3** và **botocore**: AWS SDK cho Python, được sử dụng để tương tác với các dịch vụ AWS (có thể là S3 cho lưu trữ file ghi âm).
* **django-storages**: Hỗ trợ lưu trữ file trên các backend khác nhau như Amazon S3.

### 2.4. Meeting Bot Integrations

* **zoom-meeting-sdk**: SDK để tương tác với Zoom Meeting API.
* **google-api-core**, **google-auth**, **google-cloud-texttospeech**: Các thư viện của Google Cloud, có thể được sử dụng cho các dịch vụ liên quan đến Google Meet hoặc xử lý văn bản thành giọng nói.

### 2.5. Utilities & Others

* **requests**: Thư viện HTTP phổ biến để gửi các yêu cầu web.
* **python-dotenv**: Tải các biến môi trường từ tệp `.env`.
* **PyVirtualDisplay** và **selenium**: Có thể được sử dụng cho các tác vụ tự động hóa trình duyệt hoặc kiểm thử.
* **opencv-python**: Thư viện xử lý ảnh và thị giác máy tính.
* **pydub**: Thư viện xử lý âm thanh.
* **webrtcvad**: Thư viện phát hiện hoạt động giọng nói (Voice Activity Detection).
* **watchdog**: API để giám sát các sự kiện hệ thống tệp.
* **ruff**: Công cụ định dạng và linter mã Python.
* **kubernetes**: Thư viện Python client cho Kubernetes API, có thể được sử dụng để quản lý các pod bot.
* **stripe**: Thư viện client cho Stripe API, dùng để xử lý thanh toán.

Nhìn chung, dự án sử dụng một bộ công nghệ khá toàn diện, tập trung vào việc xây dựng một ứng dụng web mạnh mẽ với các tính năng xử lý tác vụ nền, tích hợp bên thứ ba (Zoom, Google Cloud, Stripe) và khả năng triển khai trên cloud (AWS, Kubernetes).

## 3. Cấu trúc dự án

Dự án `attendee` có cấu trúc thư mục rõ ràng, tuân thủ theo quy ước của Django, với các ứng dụng (apps) riêng biệt cho từng module chức năng. Dưới đây là tổng quan về cấu trúc thư mục chính:

```text
attendee/
├── accounts/                   # Ứng dụng Django quản lý tài khoản người dùng, xác thực, đăng ký.
│   ├── migrations/             # Các file migration của Django cho models trong ứng dụng accounts.
│   ├── templates/              # Các template HTML cho ứng dụng accounts.
│   ├── admin.py                # Cấu hình admin site cho models accounts.
│   ├── apps.py                 # Cấu hình ứng dụng accounts.
│   ├── forms.py                # Các form Django cho ứng dụng accounts.
│   ├── models.py               # Định nghĩa các model cơ sở dữ liệu cho người dùng và tài khoản.
│   ├── adapters.py             # Các adapter cho django-allauth.
│   └── views.py                # Các view xử lý logic cho ứng dụng accounts.
├── attendee/                   # Thư mục chứa cấu hình chính của dự án Django.
│   ├── settings/               # Các file cấu hình settings của Django (development, production, base, etc.).
│   │   ├── base.py             # Cấu hình cơ bản áp dụng cho tất cả môi trường.
│   │   ├── development.py      # Cấu hình cho môi trường phát triển.
│   │   ├── production.py       # Cấu hình cho môi trường production.
│   │   └── ...                 # Các cấu hình khác (test, gke).
│   ├── asgi.py                 # Cấu hình ASGI cho ứng dụng (dùng cho WebSocket).
│   ├── celery.py               # Cấu hình Celery cho các tác vụ nền.
│   ├── urls.py                 # Định nghĩa các URL patterns chính của dự án.
│   └── wsgi.py                 # Cấu hình WSGI cho ứng dụng.
├── bots/                       # Ứng dụng Django chính quản lý các bot họp và tích hợp với các nền tảng.
│   ├── bot_controller/         # Logic điều khiển bot.
│   ├── bot_pod_creator/        # Logic tạo và quản lý các pod bot (có thể liên quan đến Kubernetes).
│   ├── google_meet_bot_adapter/# Adapter cho Google Meet bot.
│   ├── teams_bot_adapter/      # Adapter cho Microsoft Teams bot.
│   ├── zoom_bot_adapter/       # Adapter cho Zoom bot.
│   ├── transcription_providers/# Các module cung cấp dịch vụ chép lời.
│   ├── management/             # Các lệnh quản lý tùy chỉnh của Django.
│   ├── migrations/             # Các file migration của Django cho models trong ứng dụng bots.
│   ├── templates/              # Các template HTML cho ứng dụng bots.
│   ├── admin.py                # Cấu hình admin site cho models bots.
│   ├── apps.py                 # Cấu hình ứng dụng bots.
│   ├── authentication.py       # Logic xác thực cho API bot.
│   ├── models.py               # Định nghĩa các model cơ sở dữ liệu liên quan đến bot, cuộc họp, v.v.
│   ├── serializers.py          # Các serializer cho Django REST Framework.
│   ├── tasks/                  # Các tác vụ Celery.
│   ├── urls.py                 # Định nghĩa các URL patterns cho API bot.
│   ├── views.py                # Các view xử lý logic cho API bot.
│   └── utils.py                # Các hàm tiện ích.
├── docs/                       # Tài liệu dự án.
├── static/                     # Các file tĩnh (CSS, JavaScript, hình ảnh).
├── templates/                  # Các template HTML chung của dự án.
├── Dockerfile                  # Định nghĩa Docker image để đóng gói ứng dụng.
├── entrypoint.sh               # Script khởi động ứng dụng trong Docker container.
├── manage.py                   # Tiện ích dòng lệnh của Django.
├── pyproject.toml              # Cấu hình dự án Python (bao gồm các công cụ như Ruff).
├── requirements.txt            # Danh sách các dependencies của Python.
└── README.md                   # File README của dự án.
```

Cấu trúc này cho thấy dự án được tổ chức theo module, giúp dễ dàng quản lý và mở rộng. Các ứng dụng `accounts` và `bots` là hai module chức năng chính, tách biệt rõ ràng các trách nhiệm.

## 4. Chức năng và Cấu trúc Code

Dự án `attendee` được thiết kế để cung cấp một API mạnh mẽ cho việc quản lý các bot họp và tích hợp chúng với các nền tảng hội nghị trực tuyến phổ biến. Các chức năng chính được phân chia rõ ràng giữa các ứng dụng Django (`accounts` và `bots`) và các thành phần khác.

### 4.1. Chức năng tổng quan

* **Quản lý tài khoản người dùng (User Account Management):** Cho phép người dùng đăng ký, đăng nhập, quản lý hồ sơ và xác thực thông qua các phương thức khác nhau (bao gồm cả OAuth).
* **Quản lý Bot họp (Meeting Bot Management):** Cung cấp khả năng tạo, cấu hình, triển khai và quản lý các bot tham gia vào các cuộc họp trên Zoom, Google Meet, và có thể cả Microsoft Teams.
* **Ghi âm và Chép lời (Recording and Transcription):** Tích hợp các dịch vụ để ghi lại nội dung cuộc họp và chuyển đổi giọng nói thành văn bản (speech-to-text).
* **Xử lý tác vụ nền (Background Task Processing):** Sử dụng Celery để xử lý các tác vụ nặng và tốn thời gian như xử lý ghi âm, chép lời, hoặc các hoạt động liên quan đến bot mà không làm chặn luồng chính của ứng dụng.
* **Tích hợp thanh toán (Payment Integration):** Sử dụng Stripe để xử lý các giao dịch thanh toán liên quan đến dịch vụ.
* **API RESTful:** Cung cấp các endpoint API để các ứng dụng bên ngoài có thể tương tác và điều khiển các chức năng của hệ thống.

### 4.2. Phân tích cấu trúc Code chi tiết

#### 4.2.1. Ứng dụng `accounts`

Ứng dụng `accounts` chịu trách nhiệm quản lý người dùng và xác thực. Nó sử dụng `django-allauth` để đơn giản hóa quá trình này.

* **`models.py`**: Định nghĩa các model liên quan đến người dùng, mở rộng User model mặc định của Django nếu cần, hoặc thêm các profile người dùng.
* **`views.py`**: Chứa các view xử lý logic cho các trang liên quan đến tài khoản như đăng ký, đăng nhập, quên mật khẩu. Các view này có thể là Django views truyền thống hoặc các API view nếu có.
* **`forms.py`**: Định nghĩa các form để thu thập thông tin từ người dùng (ví dụ: form đăng ký, form đăng nhập).
* **`admin.py`**: Đăng ký các model của ứng dụng `accounts` vào Django admin site để quản trị viên có thể quản lý dữ liệu người dùng.
* **`adapters.py`**: Chứa các tùy chỉnh cho `django-allauth`, ví dụ như cách xử lý email hoặc các hành vi sau khi đăng ký/đăng nhập.

#### 4.2.2. Ứng dụng `bots`

Đây là ứng dụng cốt lõi của dự án, xử lý tất cả logic liên quan đến bot họp và tích hợp với các nền tảng bên ngoài.

* **`models.py`**: Chứa các model quan trọng như `Meeting`, `Bot`, `Transcription`, `Recording`, v.v. Đây là nơi định nghĩa cấu trúc dữ liệu cho các cuộc họp, trạng thái bot, và dữ liệu liên quan đến ghi âm/chép lời.
* **`views.py` (và `bots_api_views.py`, `projects_views.py`, `external_webhooks_views.py`)**: Định nghĩa các API endpoint cho phép tương tác với các bot, quản lý cuộc họp, và nhận các webhook từ các nền tảng như Zoom/Google Meet. Các view này thường sử dụng Django REST Framework để xây dựng API.
* **`serializers.py`**: Các serializer của DRF, dùng để chuyển đổi dữ liệu giữa các Python object và các định dạng như JSON/XML khi gửi/nhận qua API.
* **`urls.py` (và `bots_api_urls.py`, `projects_urls.py`, `external_webhooks_urls.py`)**: Định nghĩa các URL patterns cho các API endpoint và các webhook. Dự án có vẻ phân chia URL theo từng module nhỏ hơn để dễ quản lý.
* **`tasks/`**: Thư mục này chứa các tác vụ Celery. Ví dụ: `tasks.py` có thể chứa các hàm được đánh dấu là `@shared_task` để xử lý ghi âm, gửi thông báo, hoặc các hoạt động bot phức tạp khác trong nền.
* **`bot_adapter.py`**: Có thể là một interface hoặc base class cho các adapter bot cụ thể (Zoom, Google Meet, Teams). Điều này giúp chuẩn hóa cách các bot tương tác với hệ thống.
* **`zoom_bot_adapter/`, `google_meet_bot_adapter/`, `teams_bot_adapter/`**: Các thư mục này chứa logic cụ thể để tích hợp với từng nền tảng họp. Mỗi adapter sẽ xử lý các API, webhook và luồng điều khiển riêng của nền tảng đó.
* **`transcription_providers/`**: Chứa các module để tích hợp với các dịch vụ chép lời khác nhau (ví dụ: Google Cloud Speech-to-Text, AWS Transcribe, hoặc các dịch vụ bên thứ ba khác).
* **`bot_controller/`**: Có thể chứa logic điều khiển cấp cao cho các bot, quản lý vòng đời của bot (khởi tạo, tham gia, rời đi, kết thúc cuộc họp).
* **`bot_pod_creator/`**: Với việc sử dụng Kubernetes, module này có thể chịu trách nhiệm tạo và quản lý các pod (container) riêng biệt cho mỗi bot hoặc mỗi cuộc họp, đảm bảo khả năng mở rộng và cô lập tài nguyên.
* **`utils.py` (và `bots_api_utils.py`, `webhook_utils.py`)**: Chứa các hàm tiện ích chung được sử dụng trong ứng dụng `bots` để tránh trùng lặp code.
* **`stripe_utils.py`**: Chứa các hàm và logic liên quan đến tích hợp thanh toán với Stripe.

#### 4.2.3. Cấu hình dự án chính (`attendee/attendee/`)

* **`settings/`**: Thư mục này rất quan trọng, chứa các file cấu hình Django cho các môi trường khác nhau (`base.py`, `development.py`, `production.py`, v.v.). Việc phân chia này giúp quản lý cấu hình linh hoạt và an toàn.
* **`urls.py`**: File này tổng hợp tất cả các URL patterns từ các ứng dụng con (`accounts`, `bots`) và các URL cấp dự án.
* **`celery.py`**: Cấu hình Celery worker và scheduler cho dự án.
* **`asgi.py` / `wsgi.py`**: Các file cấu hình cho server ứng dụng, hỗ trợ cả ASGI (cho WebSocket và các tác vụ bất đồng bộ) và WSGI (cho các yêu cầu HTTP truyền thống).

Nhìn chung, cấu trúc code của dự án rất có tổ chức, tuân thủ các nguyên tắc của Django và DRF, đồng thời phân chia rõ ràng các trách nhiệm giữa các module. Việc sử dụng Celery và các adapter cho thấy dự án được thiết kế để xử lý các tác vụ phức tạp và tích hợp với nhiều dịch vụ bên ngoài một cách hiệu quả.

## 5. Vấn đề tiềm ẩn và Chất lượng mã

Để đánh giá chất lượng mã và tìm kiếm các vấn đề tiềm ẩn như lỗi cú pháp, lỗi logic hoặc vi phạm quy tắc coding style, tôi đã sử dụng công cụ `ruff` - một linter và formatter mã Python hiệu suất cao.

Sau khi chạy `ruff check` trên toàn bộ mã nguồn của dự án `attendee`, kết quả cho thấy:

```bash
All checks passed!
```

Điều này cho thấy mã nguồn của dự án `attendee` tuân thủ tốt các quy tắc coding style phổ biến và không chứa các lỗi cú pháp rõ ràng hoặc các vấn đề logic thông thường mà `ruff` có thể phát hiện thông qua phân tích tĩnh. Đây là một dấu hiệu tích cực về chất lượng mã và sự tuân thủ các tiêu chuẩn phát triển.

**Lưu ý:** Mặc dù `ruff` là một công cụ mạnh mẽ, nhưng nó chủ yếu tập trung vào phân tích tĩnh. Các lỗi logic phức tạp hơn, các vấn đề về hiệu suất trong môi trường runtime, hoặc các lỗ hổng bảo mật tinh vi có thể không được phát hiện bởi các công cụ phân tích tĩnh. Để đảm bảo chất lượng toàn diện, cần kết hợp thêm các phương pháp như kiểm thử đơn vị (unit testing), kiểm thử tích hợp (integration testing), kiểm thử hiệu năng (performance testing) và đánh giá bảo mật chuyên sâu.

## 6. Hướng dẫn chuyển đổi từ Django sang FastAPI

Với kinh nghiệm của bạn về FastAPI, việc chuyển đổi một dự án từ Django sang FastAPI có thể mang lại nhiều lợi ích, đặc biệt là về hiệu suất (do FastAPI dựa trên ASGI và Starlette), tự động tạo tài liệu API (OpenAPI/Swagger UI), và một cấu trúc code hiện đại, dễ bảo trì hơn cho các ứng dụng API-centric. Dưới đây là hướng dẫn chi tiết các bước và cân nhắc khi chuyển đổi dự án `attendee` từ Django sang FastAPI.

### 6.1. Tại sao lại chuyển đổi?

* **Hiệu suất cao:** FastAPI được xây dựng trên Starlette (ASGI framework) và Pydantic, cho phép xử lý các yêu cầu bất đồng bộ (asynchronous requests) một cách hiệu quả, lý tưởng cho các ứng dụng I/O-bound như API.
* **Tự động tạo tài liệu API:** FastAPI tự động tạo tài liệu API tương tác (Swagger UI và ReDoc) từ code của bạn, giúp việc phát triển và kiểm thử API dễ dàng hơn rất nhiều.
* **Kiểm tra dữ liệu (Data Validation):** Pydantic cung cấp khả năng kiểm tra dữ liệu mạnh mẽ và tự động, giúp đảm bảo tính toàn vẹn của dữ liệu đầu vào và đầu ra.
* **Dependency Injection:** Hệ thống Dependency Injection của FastAPI giúp quản lý các phụ thuộc (dependencies) một cách rõ ràng và dễ kiểm thử.
* **Cộng đồng phát triển:** FastAPI đang có một cộng đồng phát triển mạnh mẽ và ngày càng lớn mạnh.

### 6.2. Các khác biệt chính giữa Django và FastAPI

Trước khi đi sâu vào các bước, hãy hiểu rõ những khác biệt cơ bản:

| Tính năng             | Django (DRF)                                 | FastAPI                                      |
| :-------------------- | :------------------------------------------- | :------------------------------------------- |
| **Kiến trúc**         | MVT (Model-View-Template) hoặc MVC (Model-View-Controller) | API-centric, ASGI-based                      |
| **ORM**               | Django ORM (mặc định)                        | SQLAlchemy, Tortoise ORM, Pony ORM (tùy chọn) |
| **Kiểm tra dữ liệu**  | Django Forms, DRF Serializers                | Pydantic models                              |
| **Routing**           | `urls.py` với path/re_path                   | Decorators (`@app.get`, `@app.post`, v.v.)   |
| **Xử lý bất đồng bộ** | WSGI (truyền thống), ASGI (mới hơn)          | ASGI (mặc định)                              |
| **Tài liệu API**      | Tùy chọn (drf-spectacular, drf-yasg)         | Tự động (Swagger UI, ReDoc)                  |
| **Admin Panel**       | Tích hợp sẵn                                 | Không có (cần xây dựng hoặc dùng thư viện bên ngoài) |
| **Templates**         | Tích hợp sẵn (Django Templates, Jinja2)      | Không có (cần thư viện bên ngoài như Jinja2) |

### 6.3. Chiến lược chuyển đổi từng bước

Việc chuyển đổi một dự án lớn như `attendee` không thể thực hiện trong một sớm một chiều. Bạn nên áp dụng chiến lược từng bước, có thể bắt đầu bằng việc chuyển đổi từng module hoặc từng API endpoint nhỏ.

#### 6.3.1. Thiết lập môi trường FastAPI

1. **Tạo dự án FastAPI mới:**

    ```bash
    mkdir attendee_fastapi
    cd attendee_fastapi
    python -m venv venv
    source venv/bin/activate
    pip install fastapi uvicorn[standard] sqlalchemy asyncpg psycopg2-binary
    ```

2. **Cấu hình cơ sở dữ liệu:**
    * FastAPI không có ORM tích hợp. Bạn sẽ cần chọn một ORM bất đồng bộ như SQLAlchemy 2.0 (với `asyncio`) hoặc Tortoise ORM. Với dự án `attendee` đang dùng PostgreSQL, SQLAlchemy là lựa chọn tốt để duy trì sự quen thuộc với SQL.
    * Tạo file `database.py` để cấu hình kết nối DB và session:

        ```python
        # attendee_fastapi/database.py
        from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
        from sqlalchemy.orm import sessionmaker, declarative_base

        DATABASE_URL = "postgresql+asyncpg://user:password@host:port/dbname"

        engine = create_async_engine(DATABASE_URL, echo=True)
        AsyncSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)
        Base = declarative_base()

        async def get_db():
            async with AsyncSessionLocal() as session:
                yield session
        ```

#### 6.3.2. Chuyển đổi Data Models (Django ORM sang SQLAlchemy/Pydantic)

Đây là một trong những bước quan trọng nhất. Bạn sẽ cần định nghĩa lại các model từ `attendee/accounts/models.py` và `attendee/bots/models.py` sang SQLAlchemy models và Pydantic models.

1. **SQLAlchemy Models:** Định nghĩa các bảng cơ sở dữ liệu. Ví dụ, từ `accounts/models.py`:

    ```python
    # Django model
    # class User(AbstractUser):
    #     # ... fields
    ```

    Chuyển sang SQLAlchemy:

    ```python
    # attendee_fastapi/models.py
    from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
    from sqlalchemy.orm import relationship
    from .database import Base

    class User(Base):
        __tablename__ = "auth_user" # Hoặc tên bảng tương ứng trong Django
        id = Column(Integer, primary_key=True, index=True)
        username = Column(String, unique=True, index=True)
        email = Column(String, unique=True, index=True)
        is_active = Column(Boolean, default=True)
        # ... các trường khác

    class Meeting(Base):
        __tablename__ = "bots_meeting"
        id = Column(Integer, primary_key=True, index=True)
        title = Column(String)
        # ... các trường khác
    ```

2. **Pydantic Models (Schemas):** Định nghĩa cấu trúc dữ liệu cho request và response của API. Đây là nơi bạn sẽ sử dụng Pydantic để kiểm tra dữ liệu.

    ```python
    # attendee_fastapi/schemas.py
    from pydantic import BaseModel, EmailStr
    from datetime import datetime

    class UserBase(BaseModel):
        username: str
        email: EmailStr

    class UserCreate(UserBase):
        password: str

    class User(UserBase):
        id: int
        is_active: bool

        class Config:
            from_attributes = True # Hoặc orm_mode = True trong Pydantic v1

    class MeetingBase(BaseModel):
        title: str
        # ...

    class MeetingCreate(MeetingBase):
        pass

    class Meeting(MeetingBase):
        id: int
        # ...

        class Config:
            from_attributes = True
    ```

#### 6.3.3. Chuyển đổi API Endpoints (DRF Views/Serializers sang FastAPI Path Operations)

Đây là phần chính của việc chuyển đổi logic nghiệp vụ.

1. **Xác định các API Endpoint:** Duyệt qua `attendee/bots/views.py`, `attendee/bots/bots_api_views.py`, `attendee/bots/projects_views.py`, `attendee/bots/external_webhooks_views.py` và `attendee/accounts/views.py` để xác định tất cả các API endpoint hiện có.
2. **Viết lại Path Operations:** Mỗi Django REST Framework ViewSet hoặc APIView sẽ được chuyển đổi thành một hoặc nhiều FastAPI path operation.
    * **DRF Serializers** sẽ được thay thế bằng **Pydantic Models** cho request body và response model.
    * **DRF Permissions/Authentication** sẽ được thay thế bằng **FastAPI Security Dependencies**.
    * **Logic nghiệp vụ** từ các phương thức của ViewSet (như `list`, `retrieve`, `create`, `update`, `destroy`) sẽ được chuyển vào các hàm path operation.

    Ví dụ chuyển đổi một API View đơn giản:

    **Django REST Framework (ví dụ từ `bots/bots_api_views.py`):**

    ```python
    # Django REST Framework
    from rest_framework import viewsets
    from .models import Meeting
    from .serializers import MeetingSerializer

    class MeetingViewSet(viewsets.ModelViewSet):
        queryset = Meeting.objects.all()
        serializer_class = MeetingSerializer
        # ... authentication, permissions
    ```

    **FastAPI:**

    ```python
    # attendee_fastapi/main.py
    from fastapi import FastAPI, Depends, HTTPException, status
    from sqlalchemy.ext.asyncio import AsyncSession
    from typing import List

    from . import models, schemas, crud # crud là module chứa logic tương tác DB
    from .database import engine, get_db

    app = FastAPI()

    # Tạo bảng trong DB (chỉ chạy khi khởi tạo)
    @app.on_event("startup")
    async def startup_event():
        async with engine.begin() as conn:
            await conn.run_sync(models.Base.metadata.create_all)

    @app.post("/meetings/", response_model=schemas.Meeting, status_code=status.HTTP_201_CREATED)
    async def create_meeting(meeting: schemas.MeetingCreate, db: AsyncSession = Depends(get_db)):
        db_meeting = await crud.create_meeting(db=db, meeting=meeting)
        return db_meeting

    @app.get("/meetings/", response_model=List[schemas.Meeting])
    async def read_meetings(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
        meetings = await crud.get_meetings(db, skip=skip, limit=limit)
        return meetings

    @app.get("/meetings/{meeting_id}", response_model=schemas.Meeting)
    async def read_meeting(meeting_id: int, db: AsyncSession = Depends(get_db)):
        db_meeting = await crud.get_meeting(db, meeting_id=meeting_id)
        if db_meeting is None:
            raise HTTPException(status_code=404, detail="Meeting not found")
        return db_meeting
    ```

    Bạn sẽ cần tạo một module `crud.py` để chứa các hàm tương tác với cơ sở dữ liệu (Create, Read, Update, Delete) để tách biệt logic nghiệp vụ và logic DB.

#### 6.3.4. Chuyển đổi Authentication và Authorization

Django sử dụng hệ thống xác thực tích hợp và `django-allauth`. FastAPI sử dụng các Security Dependencies.

1. **Xác thực người dùng:**
    * Thay thế `django-allauth` bằng việc triển khai xác thực JWT (JSON Web Token) hoặc OAuth2 trong FastAPI.
    * Sử dụng `python-jose` hoặc `PyJWT` để tạo và xác minh JWT.
    * Tạo các endpoint `/token` để người dùng đăng nhập và nhận JWT.
2. **Ủy quyền (Authorization):**
    * Sử dụng `Depends` để inject người dùng hiện tại vào các path operation.
    * Viết các hàm dependency để kiểm tra quyền của người dùng (ví dụ: `is_admin`, `can_edit_meeting`).

    ```python
    # attendee_fastapi/auth.py
    from fastapi import Depends, HTTPException, status
    from fastapi.security import OAuth2PasswordBearer
    from jose import JWTError, jwt
    from . import schemas, crud
    from .database import get_db
    from sqlalchemy.ext.asyncio import AsyncSession

    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

    SECRET_KEY = "your-secret-key"
    ALGORITHM = "HS256"

    async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                raise credentials_exception
            token_data = schemas.TokenData(username=username)
        except JWTError:
            raise credentials_exception
        user = await crud.get_user_by_username(db, username=token_data.username)
        if user is None:
            raise credentials_exception
        return user

    async def get_current_active_user(current_user: schemas.User = Depends(get_current_user)):
        if not current_user.is_active:
            raise HTTPException(status_code=400, detail="Inactive user")
        return current_user
    ```

#### 6.3.5. Chuyển đổi Background Tasks (Celery)

Celery là một hệ thống hàng đợi tác vụ độc lập với framework. Bạn có thể tiếp tục sử dụng Celery với FastAPI.

1. **Giữ nguyên Celery:** Các tác vụ Celery hiện có trong `attendee/bots/tasks/` có thể được giữ nguyên. Bạn chỉ cần đảm bảo rằng chúng có thể được gọi từ các FastAPI path operation.
2. **Gọi tác vụ từ FastAPI:**

    ```python
    # Trong FastAPI path operation
    from .celery_app import app as celery_app # Import Celery app của bạn

    @app.post("/process-recording/")
    async def process_recording(recording_id: int):
        celery_app.send_task('bots.tasks.process_recording_task', args=[recording_id])
        return {"message": "Recording processing started in background"}
    ```

    Bạn sẽ cần một file `celery_app.py` riêng biệt để cấu hình Celery cho dự án FastAPI của mình, tương tự như `attendee/attendee/celery.py`.

#### 6.3.6. Xử lý WebSockets

Dự án `attendee` có `asgi.py`, cho thấy nó có thể sử dụng WebSockets. FastAPI có hỗ trợ WebSocket tích hợp.

1. **Chuyển đổi WebSocket Endpoints:** Các WebSocket consumer của Django Channels sẽ được chuyển đổi thành FastAPI WebSocket endpoints.

    ```python
    # attendee_fastapi/main.py
    from fastapi import WebSocket, WebSocketDisconnect

    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        await websocket.accept()
        try:
            while True:
                data = await websocket.receive_text()
                await websocket.send_text(f"Message text was: {data}")
        except WebSocketDisconnect:
            print("Client disconnected")
    ```

#### 6.3.7. Các thành phần khác

* **Static Files:** FastAPI không phục vụ static files theo mặc định như Django. Bạn sẽ cần cấu hình `StaticFiles` từ `starlette.staticfiles`.

    ```python
    from fastapi.staticfiles import StaticFiles
    app.mount("/static", StaticFiles(directory="static"), name="static")
    ```

* **Templates:** Nếu bạn có các trang HTML được render từ template (như trong `attendee/accounts/templates/`), bạn sẽ cần sử dụng một thư viện template engine như Jinja2 với FastAPI.

    ```python
    from fastapi.templating import Jinja2Templates
    templates = Jinja2Templates(directory="templates")

    @app.get("/items/{id}", response_class=HTMLResponse)
    async def read_item(request: Request, id: str):
        return templates.TemplateResponse("item.html", {"request": request, "id": id})
    ```

* **Quản lý môi trường:** Tiếp tục sử dụng `python-dotenv` để quản lý các biến môi trường.
* **Admin Panel:** FastAPI không có admin panel tích hợp. Bạn có thể sử dụng các thư viện như `FastAPI-Admin` hoặc xây dựng một giao diện quản trị tùy chỉnh.

### 6.4. Các cân nhắc quan trọng

* **Kiểm thử (Testing):** Đảm bảo bạn có bộ kiểm thử toàn diện cho các API mới của FastAPI. FastAPI cung cấp các công cụ kiểm thử tích hợp rất tốt với `pytest`.
* **Logging:** Thiết lập hệ thống logging phù hợp trong FastAPI để theo dõi các hoạt động của ứng dụng.
* **Error Handling:** Xử lý lỗi một cách nhất quán bằng cách sử dụng `HTTPException` của FastAPI và các exception handler tùy chỉnh.
* **Triển khai (Deployment):** FastAPI được triển khai bằng Uvicorn (hoặc Hypercorn) và có thể được đóng gói trong Docker tương tự như dự án Django hiện tại. Cấu hình Gunicorn cho Uvicorn worker để production.
* **Từng bước một:** Đừng cố gắng chuyển đổi toàn bộ dự án cùng một lúc. Hãy chọn một module nhỏ, ít phụ thuộc để bắt đầu, sau đó mở rộng dần.

Việc chuyển đổi này sẽ đòi hỏi một lượng công sức đáng kể, nhưng với kiến thức về FastAPI, bạn sẽ có thể xây dựng một hệ thống API hiện đại, hiệu suất cao và dễ bảo trì hơn cho dự án `attendee`.
