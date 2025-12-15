from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from accounts.views import IsAdmin, IsStaff
from .models import Unit, Product, GoodsReceipt, GoodsReceiptItem
from .serializers import (
    UnitSerializer, ProductSerializer,
    GoodsReceiptSerializer, GoodsReceiptCreateSerializer
)

# ============================================================
# PRODUCT VIEWS
# ============================================================


class UnitViewSet(viewsets.ModelViewSet):
    """API Quản lý đơn vị tính"""
    queryset = Unit.objects.all()
    serializer_class = UnitSerializer
    permission_classes = [IsAuthenticated]


class ProductViewSet(viewsets.ModelViewSet):
    """API Quản lý sản phẩm"""
    queryset = Product.objects.all().select_related('unit')
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = self.queryset
        
        # Filter theo tình trạng
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        # Filter theo đơn vị
        unit = self.request.query_params.get('unit')
        if unit:
            queryset = queryset.filter(unit_id=unit)
        
        # Search theo tên sản phẩm
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(name__icontains=search)
        
        # Filter theo khoảng giá
        min_price = self.request.query_params.get('min_price')
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        
        max_price = self.request.query_params.get('max_price')
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        
        # Sort
        sort_by = self.request.query_params.get('sort_by', 'name')
        if sort_by in ['name', 'price', '-price', 'stock_quantity', '-stock_quantity']:
            queryset = queryset.order_by(sort_by)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        """Danh sách sản phẩm sắp hết hàng (tồn < 10)"""
        products = Product.objects.filter(stock_quantity__lt=10, is_active=True)
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Thống kê sản phẩm"""
        total = Product.objects.count()
        active = Product.objects.filter(is_active=True).count()
        out_of_stock = Product.objects.filter(stock_quantity=0).count()
        low_stock = Product.objects.filter(stock_quantity__lt=10, stock_quantity__gt=0).count()
        
        return Response({
            'total': total,
            'active': active,
            'inactive': total - active,
            'out_of_stock': out_of_stock,
            'low_stock': low_stock,
        })


class GoodsReceiptViewSet(viewsets.ModelViewSet):
    """API Quản lý phiếu nhập hàng"""
    queryset = GoodsReceipt.objects.all().prefetch_related('items__product')
    permission_classes = [IsStaff]  # Chỉ Staff và Admin
    
    def get_serializer_class(self):
        if self.action == 'create':
            return GoodsReceiptCreateSerializer
        return GoodsReceiptSerializer
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
