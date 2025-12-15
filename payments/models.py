from django.db import models
from django.conf import settings
from agencies.models import Agency

# ============================================================
# PAYMENT MODELS - Phiếu thu tiền (thanh toán công nợ)
# ============================================================
# Giải thích:
# - Khi đại lý thanh toán -> Trừ công nợ
# - Có thể thanh toán một phần hoặc toàn bộ
# ============================================================


class Payment(models.Model):
    """
    Phiếu thu tiền - Đại lý thanh toán công nợ
    """
    agency = models.ForeignKey(
        Agency,
        on_delete=models.PROTECT,
        related_name='payments',
        verbose_name='Đại lý'
    )
    
    payment_date = models.DateField(verbose_name='Ngày thu')
    amount = models.DecimalField(
        max_digits=15, 
        decimal_places=0,
        verbose_name='Số tiền thu'
    )
    
    # Người thu tiền
    received_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='received_payments',
        verbose_name='Người thu'
    )
    
    note = models.TextField(blank=True, null=True, verbose_name='Ghi chú')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Phiếu thu tiền'
        verbose_name_plural = 'Danh sách phiếu thu tiền'
        ordering = ['-payment_date', '-created_at']
    
    def __str__(self):
        return f"PT-{self.id} - {self.agency.name} - {self.amount:,.0f} VNĐ"
    
    def save(self, *args, **kwargs):
        """Khi lưu phiếu thu -> Cập nhật công nợ đại lý"""
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:
            # Trừ công nợ khi tạo phiếu thu mới
            self.agency.current_debt -= self.amount
            self.agency.save()
