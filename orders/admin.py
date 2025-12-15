from django.contrib import admin
from .models import ExportOrder, ExportOrderItem


class ExportOrderItemInline(admin.TabularInline):
    model = ExportOrderItem
    extra = 1


@admin.register(ExportOrder)
class ExportOrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'agency', 'order_date', 'status', 'total_amount', 'created_by']
    list_filter = ['status', 'order_date', 'agency']
    search_fields = ['agency__name']
    date_hierarchy = 'order_date'
    inlines = [ExportOrderItemInline]
