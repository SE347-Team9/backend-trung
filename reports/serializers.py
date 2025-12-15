from rest_framework import serializers
from .models import Regulation, RevenueReport, DebtReport

# ============================================================
# REPORT SERIALIZERS
# ============================================================


class RegulationSerializer(serializers.ModelSerializer):
    """
    Quy định hệ thống
    """
    updated_by_name = serializers.CharField(source='updated_by.username', read_only=True)
    
    class Meta:
        model = Regulation
        fields = ['id', 'code', 'name', 'value', 'description', 
                  'is_active', 'updated_at', 'updated_by', 'updated_by_name']
        read_only_fields = ['id', 'code', 'updated_at', 'updated_by']


class RevenueReportSerializer(serializers.ModelSerializer):
    """
    Báo cáo doanh số
    """
    agency_name = serializers.CharField(source='agency.name', read_only=True)
    
    class Meta:
        model = RevenueReport
        fields = ['id', 'agency', 'agency_name', 'month', 'year', 
                  'order_count', 'total_revenue', 'ratio', 'created_at']


class DebtReportSerializer(serializers.ModelSerializer):
    """
    Báo cáo công nợ
    """
    agency_name = serializers.CharField(source='agency.name', read_only=True)
    
    class Meta:
        model = DebtReport
        fields = ['id', 'agency', 'agency_name', 'month', 'year',
                  'opening_debt', 'incurred', 'paid', 'closing_debt', 'created_at']
