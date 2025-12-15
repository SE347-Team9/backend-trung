from rest_framework import serializers
from .models import Payment
from datetime import date

# ============================================================
# PAYMENT SERIALIZERS
# ============================================================


class PaymentSerializer(serializers.ModelSerializer):
    """
    Phiếu thu tiền
    """
    agency_name = serializers.CharField(source='agency.name', read_only=True)
    received_by_name = serializers.CharField(source='received_by.username', read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'agency', 'agency_name', 'payment_date', 
            'amount', 'received_by', 'received_by_name', 
            'note', 'created_at'
        ]
        read_only_fields = ['id', 'received_by', 'created_at']


class PaymentCreateSerializer(serializers.ModelSerializer):
    """
    Tạo phiếu thu tiền
    """
    class Meta:
        model = Payment
        fields = ['agency', 'payment_date', 'amount', 'note']
    
    def validate_amount(self, value):
        """Kiểm tra số tiền phải > 0"""
        if value <= 0:
            raise serializers.ValidationError('Số tiền thu phải lớn hơn 0')
        return value
    
    def validate_payment_date(self, value):
        """Kiểm tra ngày không được trong tương lai"""
        if value > date.today():
            raise serializers.ValidationError('Ngày thu không được trong tương lai')
        return value
    
    def validate(self, attrs):
        agency = attrs['agency']
        amount = attrs['amount']
        
        # Kiểm tra đại lý có hoạt động không
        if not agency.is_active:
            raise serializers.ValidationError({
                'agency': f'Đại lý {agency.name} đã bị vô hiệu hóa'
            })
        
        # Kiểm tra số tiền thu không được lớn hơn công nợ
        if amount > agency.current_debt:
            raise serializers.ValidationError({
                'amount': f'Số tiền thu ({amount:,.0f}) vượt quá công nợ hiện tại ({agency.current_debt:,.0f})'
            })
        
        return attrs

