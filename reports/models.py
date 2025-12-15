from django.db import models
from django.conf import settings
from agencies.models import Agency

# ============================================================
# REGULATION & REPORT MODELS
# ============================================================
# Giải thích:
# - Regulation: Các quy định hệ thống (số đại lý tối đa/quận, ...)
# - Report: Báo cáo doanh thu, công nợ theo tháng
# ============================================================


class Regulation(models.Model):
    """
    Quy định hệ thống - Các tham số điều khiển hoạt động
    """
    code = models.CharField(max_length=50, unique=True, verbose_name='Mã quy định')
    name = models.CharField(max_length=200, verbose_name='Tên quy định')
    value = models.CharField(max_length=100, verbose_name='Giá trị')
    description = models.TextField(blank=True, null=True, verbose_name='Mô tả')
    is_active = models.BooleanField(default=True, verbose_name='Đang áp dụng')
    
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='updated_regulations',
        verbose_name='Người cập nhật'
    )
    
    class Meta:
        verbose_name = 'Quy định'
        verbose_name_plural = 'Danh sách quy định'
    
    def __str__(self):
        return f"{self.name}: {self.value}"
    
    @classmethod
    def get_value(cls, code, default=None):
        """Lấy giá trị quy định theo mã"""
        try:
            reg = cls.objects.get(code=code, is_active=True)
            return reg.value
        except cls.DoesNotExist:
            return default


class RevenueReport(models.Model):
    """
    Báo cáo doanh số tháng - Theo đại lý
    """
    agency = models.ForeignKey(
        Agency,
        on_delete=models.CASCADE,
        related_name='revenue_reports',
        verbose_name='Đại lý'
    )
    
    month = models.IntegerField(verbose_name='Tháng')
    year = models.IntegerField(verbose_name='Năm')
    
    # Số phiếu xuất trong tháng
    order_count = models.IntegerField(default=0, verbose_name='Số phiếu xuất')
    
    # Tổng doanh thu
    total_revenue = models.DecimalField(
        max_digits=15, 
        decimal_places=0, 
        default=0,
        verbose_name='Tổng doanh thu'
    )
    
    # Tỷ lệ so với tổng
    ratio = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0,
        verbose_name='Tỷ lệ (%)'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Báo cáo doanh số'
        verbose_name_plural = 'Danh sách báo cáo doanh số'
        unique_together = ['agency', 'month', 'year']
        ordering = ['-year', '-month']
    
    def __str__(self):
        return f"{self.agency.name} - {self.month}/{self.year}"


class DebtReport(models.Model):
    """
    Báo cáo công nợ tháng - Theo đại lý
    """
    agency = models.ForeignKey(
        Agency,
        on_delete=models.CASCADE,
        related_name='debt_reports',
        verbose_name='Đại lý'
    )
    
    month = models.IntegerField(verbose_name='Tháng')
    year = models.IntegerField(verbose_name='Năm')
    
    # Nợ đầu kỳ
    opening_debt = models.DecimalField(
        max_digits=15, 
        decimal_places=0, 
        default=0,
        verbose_name='Nợ đầu'
    )
    
    # Phát sinh trong kỳ (tiền hàng mua)
    incurred = models.DecimalField(
        max_digits=15, 
        decimal_places=0, 
        default=0,
        verbose_name='Phát sinh'
    )
    
    # Đã thanh toán
    paid = models.DecimalField(
        max_digits=15, 
        decimal_places=0, 
        default=0,
        verbose_name='Đã thu'
    )
    
    # Nợ cuối kỳ = Nợ đầu + Phát sinh - Đã thanh toán
    closing_debt = models.DecimalField(
        max_digits=15, 
        decimal_places=0, 
        default=0,
        verbose_name='Nợ cuối'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Báo cáo công nợ'
        verbose_name_plural = 'Danh sách báo cáo công nợ'
        unique_together = ['agency', 'month', 'year']
        ordering = ['-year', '-month']
    
    def __str__(self):
        return f"{self.agency.name} - {self.month}/{self.year}"
