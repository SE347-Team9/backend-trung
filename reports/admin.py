from django.contrib import admin
from .models import Regulation, RevenueReport, DebtReport


@admin.register(Regulation)
class RegulationAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'value', 'is_active', 'updated_at']
    list_filter = ['is_active']
    search_fields = ['code', 'name']


@admin.register(RevenueReport)
class RevenueReportAdmin(admin.ModelAdmin):
    list_display = ['agency', 'month', 'year', 'order_count', 'total_revenue', 'ratio']
    list_filter = ['year', 'month']
    search_fields = ['agency__name']


@admin.register(DebtReport)
class DebtReportAdmin(admin.ModelAdmin):
    list_display = ['agency', 'month', 'year', 'opening_debt', 'incurred', 'paid', 'closing_debt']
    list_filter = ['year', 'month']
    search_fields = ['agency__name']
