from django.db import models
from django.contrib.auth.models import AbstractUser

# ============================================================
# CUSTOM USER MODEL - Tài khoản người dùng với phân quyền
# ============================================================
# Giải thích:
# - AbstractUser: Kế thừa từ User mặc định của Django, có sẵn username, password, email
# - Thêm field 'role' để phân biệt Admin, Staff, Agency
# ============================================================

class User(AbstractUser):
    """
    Custom User Model với phân quyền
    
    Roles:
    - admin: Quản trị viên - quản lý toàn bộ hệ thống
    - staff: Nhân viên - xử lý đơn hàng, nhập xuất kho
    - agency: Đại lý - đặt hàng, xem công nợ
    """
    
    ROLE_CHOICES = (
        ('admin', 'Quản trị viên'),
        ('staff', 'Nhân viên'),
        ('agency', 'Đại lý'),
    )
    
    role = models.CharField(
        max_length=10, 
        choices=ROLE_CHOICES, 
        default='agency',
        verbose_name='Vai trò'
    )
    phone = models.CharField(max_length=15, blank=True, null=True, verbose_name='Số điện thoại')
    address = models.TextField(blank=True, null=True, verbose_name='Địa chỉ')
    is_active = models.BooleanField(default=True, verbose_name='Đang hoạt động')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Ngày tạo')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Ngày cập nhật')
    
    class Meta:
        verbose_name = 'Tài khoản'
        verbose_name_plural = 'Danh sách tài khoản'
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    @property
    def is_admin(self):
        return self.role == 'admin'
    
    @property
    def is_staff_role(self):
        return self.role == 'staff'
    
    @property
    def is_agency(self):
        return self.role == 'agency'
