from rest_framework import serializers
from .models import District, AgencyType, Agency

# ============================================================
# AGENCY SERIALIZERS
# ============================================================


class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = ['id', 'name']


class AgencyTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgencyType
        fields = ['id', 'name', 'max_debt']


class AgencySerializer(serializers.ModelSerializer):
    """
    Serializer hiển thị thông tin đại lý
    """
    agency_type_name = serializers.CharField(source='agency_type.name', read_only=True)
    district_name = serializers.CharField(source='district.name', read_only=True)
    remaining_debt_limit = serializers.DecimalField(max_digits=15, decimal_places=0, read_only=True)
    can_order = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Agency
        fields = [
            'id', 'name', 'agency_type', 'agency_type_name',
            'district', 'district_name', 'phone', 'email', 'address',
            'current_debt', 'remaining_debt_limit', 'can_order',
            'reception_date', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'current_debt', 'created_at', 'updated_at']


class AgencyCreateSerializer(serializers.ModelSerializer):
    """
    Serializer tạo đại lý mới
    """
    class Meta:
        model = Agency
        fields = [
            'name', 'agency_type', 'district', 
            'phone', 'email', 'address', 'reception_date'
        ]
