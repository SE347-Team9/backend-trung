from django.contrib import admin
from .models import Unit, Product, GoodsReceipt, GoodsReceiptItem


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'unit', 'price', 'stock_quantity', 'is_active']
    list_filter = ['unit', 'is_active']
    search_fields = ['name']


class GoodsReceiptItemInline(admin.TabularInline):
    model = GoodsReceiptItem
    extra = 1


@admin.register(GoodsReceipt)
class GoodsReceiptAdmin(admin.ModelAdmin):
    list_display = ['id', 'receipt_date', 'created_by', 'total_amount']
    list_filter = ['receipt_date']
    inlines = [GoodsReceiptItemInline]
