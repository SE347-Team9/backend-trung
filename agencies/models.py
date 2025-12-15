from django.db import models
from django.conf import settings

# ============================================================
# AGENCY MODEL - Thông tin đại lý
# ============================================================
# Giải thích:
# - Mỗi đại lý thuộc 1 loại (1, 2, 3, 4)
# - Mỗi đại lý thuộc 1 quận
# - Có thông tin công nợ, ngày tiếp nhận
# - Liên kết với User (tài khoản đăng nhập)
# ============================================================

class District(models.Model):
    """
    Quận - Dùng để phân loại đại lý theo khu vực
    """
    name = models.CharField(max_length=100, verbose_name='Tên quận')
    
    class Meta:
        verbose_name = 'Quận'
        verbose_name_plural = 'Danh sách quận'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class AgencyType(models.Model):
    """
    Loại đại lý (1, 2, 3, 4)
    - Mỗi loại có mức công nợ tối đa khác nhau
    """
    name = models.CharField(max_length=50, verbose_name='Tên loại đại lý')
    max_debt = models.DecimalField(
        max_digits=15, 
        decimal_places=0, 
        default=0,
        verbose_name='Công nợ tối đa'
    )
    
    class Meta:
        verbose_name = 'Loại đại lý'
        verbose_name_plural = 'Danh sách loại đại lý'
    
    def __str__(self):
        return f"{self.name} (Nợ tối đa: {self.max_debt:,.0f} VNĐ)"


class Agency(models.Model):
    """
    Đại lý - Thông tin chi tiết của mỗi đại lý
    """
    # Liên kết với tài khoản user (nếu đại lý có tài khoản đăng nhập)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, 
        blank=True,
        related_name='agency_profile',
        verbose_name='Tài khoản'
    )
    
    name = models.CharField(max_length=200, verbose_name='Tên đại lý')
    agency_type = models.ForeignKey(
        AgencyType, 
        on_delete=models.PROTECT,
        related_name='agencies',
        verbose_name='Loại đại lý'
    )
    district = models.ForeignKey(
        District,
        on_delete=models.PROTECT,
        related_name='agencies',
        verbose_name='Quận'
    )
    
    phone = models.CharField(max_length=15, verbose_name='Số điện thoại')
    email = models.EmailField(blank=True, null=True, verbose_name='Email')
    address = models.TextField(verbose_name='Địa chỉ')
    
    # Công nợ hiện tại
    current_debt = models.DecimalField(
        max_digits=15, 
        decimal_places=0, 
        default=0,
        verbose_name='Công nợ hiện tại'
    )
    
    reception_date = models.DateField(verbose_name='Ngày tiếp nhận')
    is_active = models.BooleanField(default=True, verbose_name='Đang hoạt động')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Ngày tạo')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Ngày cập nhật')
    
    class Meta:
        verbose_name = 'Đại lý'
        verbose_name_plural = 'Danh sách đại lý'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.agency_type.name}"
    
    @property
    def remaining_debt_limit(self):
        """Hạn mức công nợ còn lại"""
        return self.agency_type.max_debt - self.current_debt
    
    @property
    def can_order(self):
        """Kiểm tra có thể đặt hàng không (công nợ chưa vượt quá)"""
        return self.current_debt < self.agency_type.max_debt
