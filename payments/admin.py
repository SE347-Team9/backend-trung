from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'agency', 'payment_date', 'amount', 'received_by']
    list_filter = ['payment_date', 'agency']
    search_fields = ['agency__name']
    date_hierarchy = 'payment_date'
