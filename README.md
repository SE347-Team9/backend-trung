# Hệ thống Quản lý Đại lý - Backend API

## 📋 Mô tả

Backend API cho hệ thống quản lý đại lý, được xây dựng bằng Django REST Framework.
Hệ thống phân quyền cho 3 loại người dùng: Admin, Staff, Agency.

## 🏗️ Cấu trúc dự án

```
backend-trung/
├── accounts/       # Quản lý tài khoản (User với phân quyền)
├── agencies/       # Quản lý đại lý
├── products/       # Quản lý sản phẩm và nhập kho
├── orders/         # Quản lý phiếu xuất hàng
├── payments/       # Quản lý thanh toán
├── reports/        # Quy định và báo cáo
└── config/         # Cấu hình Django
```

## 🔑 Phân quyền

| Role | Mô tả | Quyền |
|------|-------|-------|
| `admin` | Quản trị viên | Full quyền |
| `staff` | Nhân viên | Xử lý đơn hàng, nhập xuất kho |
| `agency` | Đại lý | Xem thông tin, đặt hàng |

## 🚀 Cài đặt và Chạy

### Bước 1: Cài đặt dependencies

```bash
cd backend-trung
pip install -r requirements.txt
```

### Bước 2: Xóa database cũ (nếu có)

```bash
# Windows PowerShell
Remove-Item db.sqlite3 -ErrorAction SilentlyContinue
```

### Bước 3: Tạo migrations

```bash
python manage.py makemigrations accounts
python manage.py makemigrations agencies
python manage.py makemigrations products
python manage.py makemigrations orders
python manage.py makemigrations payments
python manage.py makemigrations reports
```

### Bước 4: Chạy migrations

```bash
python manage.py migrate
```

### Bước 5: Khởi tạo dữ liệu mẫu

```bash
python init_data.py
```

### Bước 6: Chạy server

```bash
python manage.py runserver
```

Server sẽ chạy tại: `http://localhost:8000`

## 📡 API Endpoints

### Authentication (`/api/auth/`)

| Method | URL | Mô tả | Quyền |
|--------|-----|-------|-------|
| POST | `/api/auth/register/` | Đăng ký tài khoản | Public |
| POST | `/api/auth/login/` | Đăng nhập | Public |
| POST | `/api/auth/logout/` | Đăng xuất | Authenticated |
| GET | `/api/auth/profile/` | Xem profile | Authenticated |
| PUT | `/api/auth/profile/` | Cập nhật profile | Authenticated |
| POST | `/api/auth/change-password/` | Đổi mật khẩu | Authenticated |
| GET | `/api/auth/users/` | Danh sách user | Admin |
| POST | `/api/auth/users/` | Tạo user mới | Admin |

### Agencies (`/api/agencies/`)

| Method | URL | Mô tả | Quyền |
|--------|-----|-------|-------|
| GET | `/api/agencies/` | Danh sách đại lý | Authenticated |
| POST | `/api/agencies/` | Tạo đại lý | Admin/Staff |
| GET | `/api/agencies/{id}/` | Chi tiết đại lý | Authenticated |
| PUT | `/api/agencies/{id}/` | Cập nhật đại lý | Admin/Staff |
| DELETE | `/api/agencies/{id}/` | Xóa đại lý | Admin |
| GET | `/api/agencies/{id}/debt_info/` | Thông tin công nợ | Authenticated |
| GET | `/api/agencies/statistics/` | Thống kê | Admin/Staff |
| GET | `/api/agencies/districts/` | Danh sách quận | Authenticated |
| GET | `/api/agencies/types/` | Loại đại lý | Authenticated |

### Products (`/api/products/`)

| Method | URL | Mô tả | Quyền |
|--------|-----|-------|-------|
| GET | `/api/products/` | Danh sách sản phẩm | Authenticated |
| POST | `/api/products/` | Thêm sản phẩm | Admin/Staff |
| GET | `/api/products/{id}/` | Chi tiết sản phẩm | Authenticated |
| GET | `/api/products/low_stock/` | SP sắp hết hàng | Authenticated |
| GET | `/api/products/statistics/` | Thống kê | Admin/Staff |
| GET | `/api/products/units/` | Đơn vị tính | Authenticated |
| POST | `/api/products/receipts/` | Tạo phiếu nhập | Admin/Staff |

### Orders (`/api/orders/`)

| Method | URL | Mô tả | Quyền |
|--------|-----|-------|-------|
| GET | `/api/orders/` | Danh sách phiếu xuất | Authenticated |
| POST | `/api/orders/` | Tạo phiếu xuất | Admin/Staff |
| GET | `/api/orders/{id}/` | Chi tiết phiếu | Authenticated |
| POST | `/api/orders/{id}/confirm/` | Xác nhận đơn | Admin/Staff |
| POST | `/api/orders/{id}/ship/` | Đang giao | Admin/Staff |
| POST | `/api/orders/{id}/complete/` | Hoàn thành | Admin/Staff |
| POST | `/api/orders/{id}/cancel/` | Hủy đơn | Admin/Staff |

### Payments (`/api/payments/`)

| Method | URL | Mô tả | Quyền |
|--------|-----|-------|-------|
| GET | `/api/payments/` | Danh sách phiếu thu | Authenticated |
| POST | `/api/payments/` | Tạo phiếu thu | Admin/Staff |
| GET | `/api/payments/{id}/` | Chi tiết phiếu | Authenticated |

### Reports (`/api/reports/`)

| Method | URL | Mô tả | Quyền |
|--------|-----|-------|-------|
| GET | `/api/reports/regulations/` | Danh sách quy định | Authenticated |
| PUT | `/api/reports/regulations/{id}/` | Sửa quy định | Admin |
| GET | `/api/reports/revenue/` | Báo cáo doanh số | Admin/Staff |
| POST | `/api/reports/revenue/generate/` | Tạo BC doanh số | Admin/Staff |
| GET | `/api/reports/debt/` | Báo cáo công nợ | Admin/Staff |
| POST | `/api/reports/debt/generate/` | Tạo BC công nợ | Admin/Staff |

## 🔐 Sử dụng API với Token

### Đăng nhập

```bash
POST /api/auth/login/
Content-Type: application/json

{
    "username": "admin",
    "password": "admin123"
}
```

Response:
```json
{
    "message": "Đăng nhập thành công",
    "access_token": "eyJ...",
    "refresh_token": "eyJ...",
    "user": {
        "id": 1,
        "username": "admin",
        "role": "admin",
        "role_display": "Quản trị viên"
    }
}
```

### Sử dụng Token

Sau khi đăng nhập, bạn sẽ nhận được `access_token`. Sử dụng token này trong header:

```
Authorization: Bearer <access_token>
```

## 👥 Tài khoản mẫu

| Username | Password | Role |
|----------|----------|------|
| admin | admin123 | Quản trị viên |
| staff01 | staff123 | Nhân viên |
| agency01 | agency123 | Đại lý |
| agency02 | agency123 | Đại lý |
| agency03 | agency123 | Đại lý |

## 🌐 Frontend URLs

- Admin Dashboard: http://localhost:5173
- Staff Dashboard: http://localhost:5174  
- Agency Dashboard: http://localhost:5175
- Django Admin: http://localhost:8000/admin

## 📦 Models

### User (accounts)
- username, email, password
- role: admin/staff/agency
- phone, address

### Agency (agencies)
- name, phone, email, address
- agency_type (FK to AgencyType)
- district (FK to District)
- current_debt (công nợ hiện tại)
- user (FK to User - tài khoản đăng nhập)

### Product (products)
- name, price, stock_quantity
- unit (FK to Unit)

### ExportOrder (orders)
- agency (FK to Agency)
- status: pending/confirmed/shipping/completed/cancelled
- items (nhiều ExportOrderItem)

### Payment (payments)
- agency (FK to Agency)
- amount (số tiền thu)
- payment_date

## 🛠️ Công nghệ sử dụng

- **Django 5.2.8** - Web framework
- **Django REST Framework 3.16.1** - RESTful API
- **djangorestframework-simplejwt 5.5.1** - JWT authentication
- **django-cors-headers 4.9.0** - CORS support

## 🔧 Development

### Tạo migrations mới
```bash
python manage.py makemigrations <app_name>
python manage.py migrate
```

### Tạo superuser
```bash
python manage.py createsuperuser
```

## ✅ Completed Features

- [x] Custom User Model với phân quyền (admin/staff/agency)
- [x] API cho quản lý tài khoản
- [x] API cho quản lý đại lý
- [x] API cho quản lý sản phẩm
- [x] API cho quản lý đơn hàng
- [x] API cho thanh toán
- [x] API cho quy định và báo cáo

## 👥 Team

SE347-Team9
