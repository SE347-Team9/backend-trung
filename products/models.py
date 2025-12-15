from django.db import models
from django.conf import settings

# ============================================================
# PRODUCT MODELS - Quản lý sản phẩm và đơn vị tính
# ============================================================


class Unit(models.Model):
    """
    Đơn vị tính (cái, hộp, thùng, kg, ...)
    """
    name = models.CharField(max_length=50, verbose_name='Tên đơn vị')
    
    class Meta:
        verbose_name = 'Đơn vị tính'
        verbose_name_plural = 'Danh sách đơn vị tính'
    
    def __str__(self):
        return self.name


class Product(models.Model):
    """
    Sản phẩm
    """
    name = models.CharField(max_length=200, verbose_name='Tên sản phẩm')
    unit = models.ForeignKey(
        Unit,
        on_delete=models.PROTECT,
        related_name='products',
        verbose_name='Đơn vị tính'
    )
    
    # Giá bán
    price = models.DecimalField(
        max_digits=15, 
        decimal_places=0,
        verbose_name='Đơn giá'
    )
    
    # Số lượng tồn kho
    stock_quantity = models.IntegerField(
        default=0,
        verbose_name='Số lượng tồn kho'
    )
    
    description = models.TextField(blank=True, null=True, verbose_name='Mô tả')
    is_active = models.BooleanField(default=True, verbose_name='Đang kinh doanh')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Ngày tạo')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Ngày cập nhật')
    
    class Meta:
        verbose_name = 'Sản phẩm'
        verbose_name_plural = 'Danh sách sản phẩm'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} - {self.price:,.0f} VNĐ/{self.unit.name}"


class GoodsReceipt(models.Model):
    """
    Phiếu nhập hàng (nhập kho từ nhà cung cấp)
    """
    receipt_date = models.DateField(verbose_name='Ngày nhập')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='goods_receipts',
        verbose_name='Người tạo'
    )
    note = models.TextField(blank=True, null=True, verbose_name='Ghi chú')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Phiếu nhập hàng'
        verbose_name_plural = 'Danh sách phiếu nhập hàng'
        ordering = ['-receipt_date']
    
    def __str__(self):
        return f"PN-{self.id} ({self.receipt_date})"
    
    @property
    def total_amount(self):
        return sum(item.total_price for item in self.items.all())


class GoodsReceiptItem(models.Model):
    """
    Chi tiết phiếu nhập hàng
    """
    receipt = models.ForeignKey(
        GoodsReceipt,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Phiếu nhập'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='receipt_items',
        verbose_name='Sản phẩm'
    )
    quantity = models.IntegerField(verbose_name='Số lượng')
    unit_price = models.DecimalField(
        max_digits=15, 
        decimal_places=0,
        verbose_name='Đơn giá nhập'
    )
    
    class Meta:
        verbose_name = 'Chi tiết phiếu nhập'
        verbose_name_plural = 'Chi tiết phiếu nhập'
    
    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
    
    @property
    def total_price(self):
        return self.quantity * self.unit_price
