from rest_framework import serializers
from .models import ExportOrder, ExportOrderItem
from agencies.serializers import AgencySerializer

# ============================================================
# ORDER SERIALIZERS
# ============================================================


class ExportOrderItemSerializer(serializers.ModelSerializer):
    """
    Chi tiết phiếu xuất
    """
    product_name = serializers.CharField(source='product.name', read_only=True)
    unit_name = serializers.CharField(source='product.unit.name', read_only=True)
    total_price = serializers.DecimalField(max_digits=15, decimal_places=0, read_only=True)
    
    class Meta:
        model = ExportOrderItem
        fields = ['id', 'product', 'product_name', 'unit_name', 
                  'quantity', 'unit_price', 'total_price']


class ExportOrderSerializer(serializers.ModelSerializer):
    """
    Phiếu xuất hàng
    """
    items = ExportOrderItemSerializer(many=True, read_only=True)
    agency_name = serializers.CharField(source='agency.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    total_amount = serializers.DecimalField(max_digits=15, decimal_places=0, read_only=True)
    total_quantity = serializers.IntegerField(read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = ExportOrder
        fields = [
            'id', 'agency', 'agency_name', 'order_date', 
            'status', 'status_display', 'created_by', 'created_by_name',
            'note', 'items', 'total_amount', 'total_quantity',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']


class ExportOrderCreateSerializer(serializers.ModelSerializer):
    """
    Tạo phiếu xuất hàng với chi tiết
    """
    items = ExportOrderItemSerializer(many=True)
    
    class Meta:
        model = ExportOrder
        fields = ['agency', 'order_date', 'note', 'items']
    
    def validate_items(self, value):
        """Kiểm tra phải có ít nhất 1 item và số lượng >= tồn kho"""
        if not value:
            raise serializers.ValidationError('Phiếu xuất phải có ít nhất 1 sản phẩm')
        
        for item in value:
            if item.get('quantity', 0) <= 0:
                raise serializers.ValidationError('Số lượng sản phẩm phải lớn hơn 0')
            
            # Kiểm tra tồn kho đủ không
            product = item.get('product')
            quantity = item.get('quantity', 0)
            if product and quantity > product.stock_quantity:
                raise serializers.ValidationError(
                    f'Sản phẩm "{product.name}" chỉ còn {product.stock_quantity} cái, không đủ {quantity} cái'
                )
        
        return value
    
    def validate(self, attrs):
        agency = attrs['agency']
        
        # Kiểm tra đại lý có hoạt động không
        if not agency.is_active:
            raise serializers.ValidationError({
                'agency': f'Đại lý {agency.name} đã bị vô hiệu hóa'
            })
        
        # Kiểm tra đại lý có thể đặt hàng không
        if not agency.can_order:
            raise serializers.ValidationError({
                'agency': f'Đại lý {agency.name} đã vượt quá hạn mức công nợ ({agency.current_debt:,.0f}/{agency.agency_type.max_debt:,.0f})'
            })
        
        return attrs
    
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = ExportOrder.objects.create(**validated_data)
        
        total_amount = 0
        for item_data in items_data:
            item = ExportOrderItem.objects.create(order=order, **item_data)
            total_amount += item.total_price
            
            # Trừ tồn kho
            product = item_data['product']
            product.stock_quantity -= item_data['quantity']
            product.save()
        
        # Cập nhật công nợ đại lý
        agency = order.agency
        agency.current_debt += total_amount
        agency.save()
        
        return order
