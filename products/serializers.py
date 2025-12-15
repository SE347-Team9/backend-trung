from rest_framework import serializers
from .models import Unit, Product, GoodsReceipt, GoodsReceiptItem

# ============================================================
# PRODUCT SERIALIZERS
# ============================================================


class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = ['id', 'name']


class ProductSerializer(serializers.ModelSerializer):
    """
    Serializer sản phẩm
    """
    unit_name = serializers.CharField(source='unit.name', read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'unit', 'unit_name', 
            'price', 'stock_quantity', 'description', 
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_name(self, value):
        """Kiểm tra tên sản phẩm không trống"""
        if not value or not value.strip():
            raise serializers.ValidationError('Tên sản phẩm không được để trống')
        return value.strip()
    
    def validate_price(self, value):
        """Kiểm tra giá > 0"""
        if value <= 0:
            raise serializers.ValidationError('Giá sản phẩm phải lớn hơn 0')
        return value
    
    def validate_stock_quantity(self, value):
        """Kiểm tra tồn kho >= 0"""
        if value < 0:
            raise serializers.ValidationError('Số lượng tồn kho không được âm')
        return value

class GoodsReceiptItemSerializer(serializers.ModelSerializer):
    """
    Chi tiết phiếu nhập
    """
    product_name = serializers.CharField(source='product.name', read_only=True)
    total_price = serializers.DecimalField(max_digits=15, decimal_places=0, read_only=True)
    
    class Meta:
        model = GoodsReceiptItem
        fields = ['id', 'product', 'product_name', 'quantity', 'unit_price', 'total_price']


class GoodsReceiptSerializer(serializers.ModelSerializer):
    """
    Phiếu nhập hàng
    """
    items = GoodsReceiptItemSerializer(many=True, read_only=True)
    total_amount = serializers.DecimalField(max_digits=15, decimal_places=0, read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = GoodsReceipt
        fields = ['id', 'receipt_date', 'created_by', 'created_by_name', 
                  'note', 'items', 'total_amount', 'created_at']
        read_only_fields = ['id', 'created_by', 'created_at']


class GoodsReceiptCreateSerializer(serializers.ModelSerializer):
    """
    Tạo phiếu nhập hàng với chi tiết
    """
    items = GoodsReceiptItemSerializer(many=True)
    
    class Meta:
        model = GoodsReceipt
        fields = ['receipt_date', 'note', 'items']
    
    def validate_items(self, value):
        """Kiểm tra phải có ít nhất 1 item"""
        if not value:
            raise serializers.ValidationError('Phiếu nhập phải có ít nhất 1 sản phẩm')
        
        # Kiểm tra từng item
        for item in value:
            if item.get('quantity', 0) <= 0:
                raise serializers.ValidationError('Số lượng sản phẩm phải lớn hơn 0')
            if item.get('unit_price', 0) <= 0:
                raise serializers.ValidationError('Giá sản phẩm phải lớn hơn 0')
        
        return value
    
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        receipt = GoodsReceipt.objects.create(**validated_data)
        
        for item_data in items_data:
            GoodsReceiptItem.objects.create(receipt=receipt, **item_data)
            # Cập nhật tồn kho
            product = item_data['product']
            product.stock_quantity += item_data['quantity']
            product.save()
        
        return receipt

