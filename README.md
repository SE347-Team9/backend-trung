# Backend API - Django REST Framework

Backend API cho hệ thống quản lý Admin, Staff và Agency.

## 🚀 Cài đặt

### 1. Clone repository
```bash
git clone https://github.com/SE347-Team9/backend-trung.git
cd backend-trung
```

### 2. Tạo môi trường ảo
```bash
python -m venv venv
```

### 3. Kích hoạt môi trường ảo

**Windows (PowerShell):**
```bash
.\venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```bash
.\venv\Scripts\activate.bat
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 4. Cài đặt dependencies
```bash
pip install -r requirements.txt
```

### 5. Chạy migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Tạo superuser (admin)
```bash
python manage.py createsuperuser
```

### 7. Chạy server
```bash
python manage.py runserver
```

Server sẽ chạy tại: `http://localhost:8000`

## 📡 API Endpoints

### Authentication

- **POST** `/api/auth/register/` - Đăng ký tài khoản mới
  ```json
  {
    "username": "user123",
    "email": "user@example.com",
    "password": "password123"
  }
  ```

- **POST** `/api/auth/login/` - Đăng nhập
  ```json
  {
    "username": "user123",
    "password": "password123"
  }
  ```

- **POST** `/api/auth/logout/` - Đăng xuất (cần token)

- **GET** `/api/auth/profile/` - Xem thông tin user (cần token)

### JWT Token

- **POST** `/api/token/` - Lấy access & refresh token
- **POST** `/api/token/refresh/` - Refresh access token

## 🔑 Sử dụng API với Token

Sau khi đăng nhập, bạn sẽ nhận được `access_token`. Sử dụng token này trong header:

```
Authorization: Bearer <access_token>
```

## 🛠️ Công nghệ sử dụng

- **Django 5.2.8** - Web framework
- **Django REST Framework 3.16.1** - RESTful API
- **djangorestframework-simplejwt 5.5.1** - JWT authentication
- **django-cors-headers 4.9.0** - CORS support

## 📦 Cấu trúc thư mục

```
backend-trung/
├── accounts/           # App xử lý authentication
├── config/            # Cấu hình Django project
├── venv/              # Môi trường ảo
├── manage.py          # Django management script
└── requirements.txt   # Python packages
```

## 🔧 Development

### Tạo app mới
```bash
python manage.py startapp <app_name>
```

### Tạo migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Chạy tests
```bash
python manage.py test
```

## 📝 TODO

- [ ] Thêm models cho Agency, Staff, Products
- [ ] API cho quản lý đơn hàng
- [ ] API cho báo cáo
- [ ] API cho quy định
- [ ] Phân quyền user (Admin, Staff, Agency)

## 👥 Team

SE347-Team9
