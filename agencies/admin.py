from django.contrib import admin
from .models import District, AgencyType, Agency


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']


@admin.register(AgencyType)
class AgencyTypeAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'max_debt']
    search_fields = ['name']


@admin.register(Agency)
class AgencyAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'agency_type', 'district', 'phone', 'current_debt', 'is_active', 'reception_date']
    list_filter = ['agency_type', 'district', 'is_active']
    search_fields = ['name', 'phone', 'email']
    date_hierarchy = 'reception_date'
