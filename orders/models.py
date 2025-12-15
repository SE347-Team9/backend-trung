from django.db import models
from django.conf import settings
from agencies.models import Agency
from products.models import Product

# ============================================================
# ORDER MODELS - Phiếu xuất hàng cho đại lý
# ============================================================
# Giải thích:
# - ExportOrder: Phiếu xuất hàng (đại lý đặt mua)
# - ExportOrderItem: Chi tiết sản phẩm trong phiếu
# - Khi xuất hàng -> Cộng vào công nợ đại lý
# ============================================================


class ExportOrder(models.Model):
    """
    Phiếu xuất hàng - Đơn hàng bán cho đại lý
    """
    STATUS_CHOICES = (
        ('pending', 'Chờ xử lý'),
        ('confirmed', 'Đã xác nhận'),
        ('shipping', 'Đang giao'),
        ('completed', 'Hoàn thành'),
        ('cancelled', 'Đã hủy'),
    )
    
    # Đại lý đặt hàng
    agency = models.ForeignKey(
        Agency,
        on_delete=models.PROTECT,
        related_name='orders',
        verbose_name='Đại lý'
    )
    
    order_date = models.DateField(verbose_name='Ngày lập phiếu')
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending',
        verbose_name='Trạng thái'
    )
    
    # Người tạo phiếu (Staff hoặc Admin)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='created_orders',
        verbose_name='Người tạo'
    )
    
    note = models.TextField(blank=True, null=True, verbose_name='Ghi chú')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Phiếu xuất hàng'
        verbose_name_plural = 'Danh sách phiếu xuất hàng'
        ordering = ['-order_date', '-created_at']
    
    def __str__(self):
        return f"PX-{self.id} - {self.agency.name} ({self.order_date})"
    
    @property
    def total_amount(self):
        """Tổng tiền đơn hàng"""
        return sum(item.total_price for item in self.items.all())
    
    @property
    def total_quantity(self):
        """Tổng số lượng sản phẩm"""
        return sum(item.quantity for item in self.items.all())


class ExportOrderItem(models.Model):
    """
    Chi tiết phiếu xuất hàng
    """
    order = models.ForeignKey(
        ExportOrder,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Phiếu xuất'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='order_items',
        verbose_name='Sản phẩm'
    )
    quantity = models.IntegerField(verbose_name='Số lượng')
    unit_price = models.DecimalField(
        max_digits=15, 
        decimal_places=0,
        verbose_name='Đơn giá'
    )
    
    class Meta:
        verbose_name = 'Chi tiết phiếu xuất'
        verbose_name_plural = 'Chi tiết phiếu xuất'
    
    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
    
    @property
    def total_price(self):
        """Thành tiền"""
        return self.quantity * self.unit_price
