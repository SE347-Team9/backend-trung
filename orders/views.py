from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum

from accounts.views import IsAdmin, IsStaff
from .models import ExportOrder, ExportOrderItem
from .serializers import ExportOrderSerializer, ExportOrderCreateSerializer

# ============================================================
# ORDER VIEWS
# ============================================================


class ExportOrderViewSet(viewsets.ModelViewSet):
    """
    API Quản lý phiếu xuất hàng
    - Admin/Staff: Full quyền
    - Agency: Chỉ xem đơn hàng của mình
    """
    queryset = ExportOrder.objects.all().select_related(
        'agency', 'created_by'
    ).prefetch_related('items__product')
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ExportOrderCreateSerializer
        return ExportOrderSerializer
    
    def get_queryset(self):
        from django.db.models import Q
        from datetime import datetime, timedelta
        
        user = self.request.user
        queryset = self.queryset
        
        # Agency chỉ xem được đơn của mình
        if user.role == 'agency':
            return queryset.filter(agency__user=user)
        
        # Filter theo trạng thái
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter theo đại lý
        agency = self.request.query_params.get('agency')
        if agency:
            queryset = queryset.filter(agency_id=agency)
        
        # Filter theo khoảng ngày
        from_date = self.request.query_params.get('from_date')
        if from_date:
            queryset = queryset.filter(order_date__gte=from_date)
        
        to_date = self.request.query_params.get('to_date')
        if to_date:
            queryset = queryset.filter(order_date__lte=to_date)
        
        # Filter theo người tạo
        created_by = self.request.query_params.get('created_by')
        if created_by:
            queryset = queryset.filter(created_by_id=created_by)
        
        # Search theo ghi chú
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(Q(note__icontains=search) | Q(agency__name__icontains=search))
        
        # Sort
        sort_by = self.request.query_params.get('sort_by', '-order_date')
        if sort_by in ['order_date', '-order_date', 'created_at', '-created_at']:
            queryset = queryset.order_by(sort_by)
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """Xác nhận đơn hàng"""
        order = self.get_object()
        if order.status != 'pending':
            return Response(
                {'error': 'Chỉ có thể xác nhận đơn hàng đang chờ xử lý'},
                status=status.HTTP_400_BAD_REQUEST
            )
        order.status = 'confirmed'
        order.save()
        return Response({'message': 'Đã xác nhận đơn hàng'})
    
    @action(detail=True, methods=['post'])
    def ship(self, request, pk=None):
        """Chuyển sang đang giao"""
        order = self.get_object()
        if order.status != 'confirmed':
            return Response(
                {'error': 'Chỉ có thể giao đơn hàng đã xác nhận'},
                status=status.HTTP_400_BAD_REQUEST
            )
        order.status = 'shipping'
        order.save()
        return Response({'message': 'Đơn hàng đang được giao'})
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Hoàn thành đơn hàng"""
        order = self.get_object()
        if order.status not in ['confirmed', 'shipping']:
            return Response(
                {'error': 'Không thể hoàn thành đơn hàng này'},
                status=status.HTTP_400_BAD_REQUEST
            )
        order.status = 'completed'
        order.save()
        return Response({'message': 'Đơn hàng đã hoàn thành'})
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Hủy đơn hàng"""
        order = self.get_object()
        if order.status not in ['pending', 'confirmed']:
            return Response(
                {'error': 'Không thể hủy đơn hàng này'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Hoàn lại tồn kho và công nợ
        for item in order.items.all():
            item.product.stock_quantity += item.quantity
            item.product.save()
        
        order.agency.current_debt -= order.total_amount
        order.agency.save()
        
        order.status = 'cancelled'
        order.save()
        return Response({'message': 'Đã hủy đơn hàng'})
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Thống kê đơn hàng"""
        total = ExportOrder.objects.count()
        pending = ExportOrder.objects.filter(status='pending').count()
        completed = ExportOrder.objects.filter(status='completed').count()
        cancelled = ExportOrder.objects.filter(status='cancelled').count()
        
        total_revenue = ExportOrder.objects.filter(
            status='completed'
        ).aggregate(total=Sum('items__quantity') * Sum('items__unit_price'))
        
        return Response({
            'total': total,
            'pending': pending,
            'completed': completed,
            'cancelled': cancelled,
        })
