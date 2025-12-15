# 📚 Backend API Endpoints Documentation

**Base URL:** `http://localhost:8000/api/`

---

## 🔐 Authentication

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| POST | `/token/` | Lấy JWT access token |
| POST | `/token/refresh/` | Refresh token |
| POST | `/auth/register/` | Đăng ký tài khoản mới |
| POST | `/auth/login/` | Đăng nhập |
| POST | `/auth/logout/` | Đăng xuất |
| GET | `/auth/profile/` | Xem profile |
| PUT | `/auth/profile/` | Cập nhật profile |
| POST | `/auth/change-password/` | Đổi mật khẩu |

---

## 👥 Agencies (Quản lý Đại lý)

### Districts (Quận)
```
GET     /agencies/districts/              # Danh sách quận
POST    /agencies/districts/              # Tạo quận mới
GET     /agencies/districts/{id}/         # Chi tiết quận
PUT     /agencies/districts/{id}/         # Cập nhật quận
DELETE  /agencies/districts/{id}/         # Xóa quận
```

### Agency Types (Loại Đại lý)
```
GET     /agencies/types/                  # Danh sách loại
POST    /agencies/types/                  # Tạo loại mới
GET     /agencies/types/{id}/             # Chi tiết loại
PUT     /agencies/types/{id}/             # Cập nhật loại
DELETE  /agencies/types/{id}/             # Xóa loại
```

### Agencies (Đại lý)
```
GET     /agencies/                        # Danh sách đại lý
POST    /agencies/                        # Tạo đại lý mới
GET     /agencies/{id}/                   # Chi tiết đại lý
PUT     /agencies/{id}/                   # Cập nhật đại lý
DELETE  /agencies/{id}/                   # Xóa đại lý

# Actions
GET     /agencies/{id}/debt_info/         # Xem công nợ
GET     /agencies/{id}/debt_history/      # Lịch sử công nợ (phiếu xuất + thanh toán)
GET     /agencies/statistics/             # Thống kê đại lý
```

#### Query Filters
- `?is_active=true` - Chỉ đại lý hoạt động
- `?agency_type=2` - Filter theo loại đại lý
- `?district=3` - Filter theo quận
- `?search=ABC` - Tìm kiếm theo tên
- `?debt_status=overdue` - Công nợ vượt hạn
- `?debt_status=safe` - Công nợ an toàn

---

## 📦 Products (Quản lý Sản phẩm)

### Units (Đơn vị tính)
```
GET     /products/units/                  # Danh sách đơn vị
POST    /products/units/                  # Tạo đơn vị mới
GET     /products/units/{id}/             # Chi tiết đơn vị
PUT     /products/units/{id}/             # Cập nhật đơn vị
DELETE  /products/units/{id}/             # Xóa đơn vị
```

### Products (Sản phẩm)
```
GET     /products/                        # Danh sách sản phẩm
POST    /products/                        # Tạo sản phẩm mới
GET     /products/{id}/                   # Chi tiết sản phẩm
PUT     /products/{id}/                   # Cập nhật sản phẩm
DELETE  /products/{id}/                   # Xóa sản phẩm

# Actions
GET     /products/low_stock/              # Sản phẩm sắp hết hàng (< 10)
GET     /products/statistics/             # Thống kê sản phẩm
```

#### Query Filters
- `?is_active=true` - Chỉ sản phẩm hoạt động
- `?unit=1` - Filter theo đơn vị
- `?search=ABC` - Tìm kiếm theo tên
- `?min_price=100000` - Giá tối thiểu
- `?max_price=500000` - Giá tối đa
- `?sort_by=price` - Sắp xếp (name, price, -price, stock_quantity, -stock_quantity)

### Goods Receipts (Phiếu Nhập Kho)
```
GET     /products/receipts/               # Danh sách phiếu nhập
POST    /products/receipts/               # Tạo phiếu nhập mới
GET     /products/receipts/{id}/          # Chi tiết phiếu nhập
```

#### Example POST Body
```json
{
  "receipt_date": "2025-12-14",
  "note": "Nhập hàng từ nhà cung cấp",
  "items": [
    {
      "product": 1,
      "quantity": 10,
      "unit_price": 50000
    },
    {
      "product": 2,
      "quantity": 20,
      "unit_price": 75000
    }
  ]
}
```

---

## 📋 Orders (Quản lý Phiếu Xuất Hàng)

```
GET     /orders/                          # Danh sách phiếu xuất
POST    /orders/                          # Tạo phiếu xuất mới
GET     /orders/{id}/                     # Chi tiết phiếu xuất
PUT     /orders/{id}/                     # Cập nhật phiếu xuất
DELETE  /orders/{id}/                     # Xóa phiếu xuất

# Actions
POST    /orders/{id}/confirm/             # Xác nhận phiếu
POST    /orders/{id}/ship/                # Chuyển sang đang giao
POST    /orders/{id}/complete/            # Hoàn thành phiếu
POST    /orders/{id}/cancel/              # Hủy phiếu (hoàn lại tồn kho & công nợ)
GET     /orders/statistics/               # Thống kê đơn hàng
```

#### Query Filters
- `?status=pending` - Filter theo trạng thái (pending, confirmed, shipping, completed, cancelled)
- `?agency=1` - Filter theo đại lý
- `?from_date=2025-12-01` - Từ ngày
- `?to_date=2025-12-31` - Đến ngày
- `?created_by=1` - Filter theo người tạo
- `?search=ABC` - Tìm kiếm
- `?sort_by=-order_date` - Sắp xếp

#### Example POST Body
```json
{
  "agency": 1,
  "order_date": "2025-12-14",
  "note": "Đơn hàng từ khách",
  "items": [
    {
      "product": 1,
      "quantity": 5,
      "unit_price": 50000
    },
    {
      "product": 2,
      "quantity": 10,
      "unit_price": 75000
    }
  ]
}
```

---

## 💳 Payments (Quản lý Thanh Toán)

```
GET     /payments/                        # Danh sách phiếu thu
POST    /payments/                        # Tạo phiếu thu mới
GET     /payments/{id}/                   # Chi tiết phiếu thu
```

#### Query Filters
- `?agency=1` - Filter theo đại lý

#### Example POST Body
```json
{
  "agency": 1,
  "payment_date": "2025-12-14",
  "amount": 500000,
  "note": "Thanh toán công nợ"
}
```

---

## 📊 Reports (Báo cáo & Quy định)

### Regulations (Quy định)
```
GET     /reports/regulations/             # Danh sách quy định
POST    /reports/regulations/             # Tạo quy định (Admin only)
GET     /reports/regulations/{id}/        # Chi tiết quy định
PUT     /reports/regulations/{id}/        # Cập nhật (Admin only)
DELETE  /reports/regulations/{id}/        # Xóa (Admin only)
```

### Revenue Reports (Báo cáo Doanh số)
```
GET     /reports/revenue/                 # Danh sách báo cáo doanh số
GET     /reports/revenue/{id}/            # Chi tiết báo cáo
```

#### Query Filters
- `?month=12` - Filter theo tháng
- `?year=2025` - Filter theo năm

### Debt Reports (Báo cáo Công nợ)
```
GET     /reports/debt/                    # Danh sách báo cáo công nợ
GET     /reports/debt/{id}/               # Chi tiết báo cáo
```

---

## 📈 Dashboard (Thống kê Tổng Quan)

### Overview
```
GET     /reports/dashboard/overview/      # Tổng quan hệ thống
```

**Response:**
```json
{
  "agencies": {
    "total": 50,
    "active": 45,
    "inactive": 5,
    "total_debt": 5000000
  },
  "products": {
    "total": 100,
    "active": 95,
    "out_of_stock": 2,
    "low_stock": 3
  },
  "orders": {
    "total": 200,
    "pending": 10,
    "confirmed": 20,
    "shipping": 15,
    "completed": 150
  },
  "revenue": {
    "month": 12,
    "year": 2025,
    "total": 10000000
  }
}
```

### Revenue by Agency
```
GET     /reports/dashboard/revenue_by_agency/
```

### Debt by Agency
```
GET     /reports/dashboard/debt_by_agency/
```

### Order Status Summary
```
GET     /reports/dashboard/order_status_summary/
```

### Generate Reports
```
POST    /reports/revenue/generate/        # Tạo báo cáo doanh số & công nợ
```

**Request Body:**
```json
{
  "month": 12,
  "year": 2025
}
```

---

## ❌ Error Handling

Tất cả errors trả về format:

```json
{
  "error": "Mô tả lỗi"
}
```

hoặc

```json
{
  "field_name": ["Thông báo lỗi"]
}
```

---

## 🔐 Permissions

| Role | Quyền |
|------|-------|
| **Admin** | Full quyền tất cả |
| **Staff** | Xem + tạo + sửa (không xóa), Quản lý sản phẩm, phiếu |
| **Agency** | Chỉ xem/tạo đơn hàng của mình, xem công nợ |

---

## 📝 Notes

1. **JWT Authentication**: Thêm header: `Authorization: Bearer {token}`
2. **Pagination**: Sẽ thêm `?page=1&page_size=20` nếu cần
3. **Validations**: Tất cả fields bắt buộc được validate
4. **Timestamps**: Mọi response có `created_at`, `updated_at` (ISO 8601 format)
5. **Decimal Fields**: Giá tiền, công nợ được trả về dạng số thập phân

---

## 🔍 Common Filters Usage

### Tìm đại lý công nợ vượt hạn
```
GET /agencies/?debt_status=overdue
```

### Tìm sản phẩm sắp hết hàng
```
GET /products/?sort_by=-stock_quantity&max_price=500000
```

### Tìm phiếu xuất trong tháng 12
```
GET /orders/?from_date=2025-12-01&to_date=2025-12-31&status=completed
```

### Tìm kiếm đại lý theo tên
```
GET /agencies/?search=ABC&is_active=true
```
