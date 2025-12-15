"""
Script khởi tạo dữ liệu mẫu cho hệ thống
Chạy: python manage.py shell < init_data.py
Hoặc: python manage.py runscript init_data (cần django-extensions)
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from agencies.models import District, AgencyType, Agency
from products.models import Unit, Product
from reports.models import Regulation
from datetime import date

User = get_user_model()

print("=" * 60)
print("KHỞI TẠO DỮ LIỆU MẪU")
print("=" * 60)

# ============================================================
# 1. TẠO TÀI KHOẢN
# ============================================================
print("\n📌 Tạo tài khoản...")

# Admin
if not User.objects.filter(username='admin').exists():
    admin = User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='admin123',
        role='admin'
    )
    print("  ✓ Tạo tài khoản admin (admin / admin123)")

# Staff
if not User.objects.filter(username='staff01').exists():
    staff = User.objects.create_user(
        username='staff01',
        email='staff01@example.com',
        password='staff123',
        role='staff',
        first_name='Nhân viên',
        last_name='01'
    )
    print("  ✓ Tạo tài khoản staff01 (staff01 / staff123)")

# Agency users
for i in range(1, 4):
    username = f'agency0{i}'
    if not User.objects.filter(username=username).exists():
        User.objects.create_user(
            username=username,
            email=f'agency0{i}@example.com',
            password='agency123',
            role='agency',
            first_name=f'Đại lý',
            last_name=f'0{i}'
        )
        print(f"  ✓ Tạo tài khoản {username} ({username} / agency123)")

# ============================================================
# 2. TẠO QUẬN
# ============================================================
print("\n📌 Tạo danh sách quận...")

districts = [
    'Quận 1', 'Quận 2', 'Quận 3', 'Quận 4', 'Quận 5',
    'Quận 6', 'Quận 7', 'Quận 8', 'Quận 9', 'Quận 10',
    'Quận 11', 'Quận 12', 'Quận Bình Thạnh', 'Quận Gò Vấp',
    'Quận Phú Nhuận', 'Quận Tân Bình', 'Quận Tân Phú',
    'Quận Thủ Đức', 'Huyện Bình Chánh', 'Huyện Hóc Môn'
]

for name in districts:
    District.objects.get_or_create(name=name)
print(f"  ✓ Đã tạo {len(districts)} quận")

# ============================================================
# 3. TẠO LOẠI ĐẠI LÝ
# ============================================================
print("\n📌 Tạo loại đại lý...")

agency_types = [
    {'name': 'Loại 1', 'max_debt': 20000000},
    {'name': 'Loại 2', 'max_debt': 50000000},
    {'name': 'Loại 3', 'max_debt': 100000000},
    {'name': 'Loại 4', 'max_debt': 200000000},
]

for at in agency_types:
    AgencyType.objects.get_or_create(name=at['name'], defaults={'max_debt': at['max_debt']})
    print(f"  ✓ {at['name']} - Công nợ tối đa: {at['max_debt']:,} VNĐ")

# ============================================================
# 4. TẠO ĐẠI LÝ MẪU
# ============================================================
print("\n📌 Tạo đại lý mẫu...")

agency_data = [
    {
        'name': 'Đại lý Minh Anh',
        'agency_type': 'Loại 1',
        'district': 'Quận 1',
        'phone': '0901234567',
        'email': 'minhanh@example.com',
        'address': '123 Nguyễn Huệ, Quận 1',
        'user': 'agency01'
    },
    {
        'name': 'Đại lý Hoàng Long',
        'agency_type': 'Loại 2',
        'district': 'Quận 3',
        'phone': '0912345678',
        'email': 'hoanglong@example.com',
        'address': '456 Võ Văn Tần, Quận 3',
        'user': 'agency02'
    },
    {
        'name': 'Đại lý Phương Nam',
        'agency_type': 'Loại 3',
        'district': 'Quận 7',
        'phone': '0923456789',
        'email': 'phuongnam@example.com',
        'address': '789 Nguyễn Thị Thập, Quận 7',
        'user': 'agency03'
    },
]

for data in agency_data:
    if not Agency.objects.filter(name=data['name']).exists():
        Agency.objects.create(
            name=data['name'],
            agency_type=AgencyType.objects.get(name=data['agency_type']),
            district=District.objects.get(name=data['district']),
            phone=data['phone'],
            email=data['email'],
            address=data['address'],
            user=User.objects.get(username=data['user']),
            reception_date=date.today()
        )
        print(f"  ✓ {data['name']}")

# ============================================================
# 5. TẠO ĐƠN VỊ TÍNH
# ============================================================
print("\n📌 Tạo đơn vị tính...")

units = ['Cái', 'Hộp', 'Thùng', 'Kg', 'Lít', 'Chai', 'Gói', 'Bộ']
for name in units:
    Unit.objects.get_or_create(name=name)
print(f"  ✓ Đã tạo {len(units)} đơn vị tính")

# ============================================================
# 6. TẠO SẢN PHẨM MẪU
# ============================================================
print("\n📌 Tạo sản phẩm mẫu...")

products = [
    {'name': 'Nước ngọt Coca Cola 330ml', 'unit': 'Thùng', 'price': 180000, 'stock': 100},
    {'name': 'Nước ngọt Pepsi 330ml', 'unit': 'Thùng', 'price': 175000, 'stock': 80},
    {'name': 'Nước suối Aquafina 500ml', 'unit': 'Thùng', 'price': 95000, 'stock': 200},
    {'name': 'Sữa Vinamilk 180ml', 'unit': 'Thùng', 'price': 280000, 'stock': 50},
    {'name': 'Mì Hảo Hảo', 'unit': 'Thùng', 'price': 120000, 'stock': 150},
    {'name': 'Dầu ăn Neptune 1L', 'unit': 'Chai', 'price': 45000, 'stock': 60},
    {'name': 'Gạo ST25 5kg', 'unit': 'Bộ', 'price': 150000, 'stock': 40},
    {'name': 'Đường Biên Hòa 1kg', 'unit': 'Gói', 'price': 25000, 'stock': 100},
]

for p in products:
    if not Product.objects.filter(name=p['name']).exists():
        Product.objects.create(
            name=p['name'],
            unit=Unit.objects.get(name=p['unit']),
            price=p['price'],
            stock_quantity=p['stock']
        )
        print(f"  ✓ {p['name']} - {p['price']:,} VNĐ")

# ============================================================
# 7. TẠO QUY ĐỊNH MẪU
# ============================================================
print("\n📌 Tạo quy định...")

regulations = [
    {
        'code': 'MAX_AGENCY_PER_DISTRICT',
        'name': 'Số đại lý tối đa trong quận',
        'value': '4',
        'description': 'Mỗi quận chỉ được có tối đa 4 đại lý'
    },
    {
        'code': 'MAX_AGENCY_TYPES',
        'name': 'Số loại đại lý',
        'value': '4',
        'description': 'Hệ thống có 4 loại đại lý'
    },
    {
        'code': 'ALLOW_DEBT_ORDER',
        'name': 'Cho phép đặt hàng khi còn nợ',
        'value': 'true',
        'description': 'Đại lý có thể đặt hàng khi chưa thanh toán hết công nợ'
    },
]

for r in regulations:
    Regulation.objects.get_or_create(
        code=r['code'],
        defaults={
            'name': r['name'],
            'value': r['value'],
            'description': r['description']
        }
    )
    print(f"  ✓ {r['name']}: {r['value']}")

# ============================================================
# HOÀN THÀNH
# ============================================================
print("\n" + "=" * 60)
print("✅ HOÀN THÀNH KHỞI TẠO DỮ LIỆU!")
print("=" * 60)

print("\n📋 TÀI KHOẢN ĐÃ TẠO:")
print("  • Admin:   admin / admin123")
print("  • Staff:   staff01 / staff123")
print("  • Agency:  agency01 / agency123")
print("  • Agency:  agency02 / agency123")
print("  • Agency:  agency03 / agency123")

print("\n🌐 TRUY CẬP:")
print("  • Admin Dashboard:  http://localhost:5173")
print("  • Staff Dashboard:  http://localhost:5174")
print("  • Agency Dashboard: http://localhost:5175")
print("  • Django Admin:     http://localhost:8000/admin")
print("  • API Root:         http://localhost:8000/api")
