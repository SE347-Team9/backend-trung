from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from accounts.views import IsAdmin, IsStaff
from .models import District, AgencyType, Agency
from .serializers import (
    DistrictSerializer, AgencyTypeSerializer, 
    AgencySerializer, AgencyCreateSerializer
)

# ============================================================
# AGENCY VIEWS
# ============================================================


class DistrictViewSet(viewsets.ModelViewSet):
    """API Quản lý quận"""
    queryset = District.objects.all()
    serializer_class = DistrictSerializer
    permission_classes = [IsAuthenticated]


class AgencyTypeViewSet(viewsets.ModelViewSet):
    """API Quản lý loại đại lý"""
    queryset = AgencyType.objects.all()
    serializer_class = AgencyTypeSerializer
    permission_classes = [IsAuthenticated]


class AgencyViewSet(viewsets.ModelViewSet):
    """
    API Quản lý đại lý
    - Admin: Full quyền
    - Staff: Xem, tạo, sửa
    - Agency: Chỉ xem đại lý của mình
    """
    queryset = Agency.objects.all().select_related('agency_type', 'district', 'user')
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return AgencyCreateSerializer
        return AgencySerializer
    
    def get_queryset(self):
        user = self.request.user
        queryset = self.queryset
        
        # Agency chỉ xem được thông tin của mình
        if user.role == 'agency':
            return queryset.filter(user=user)
        
        # Admin và Staff xem được tất cả
        # Filter theo trạng thái
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        # Filter theo loại đại lý
        agency_type = self.request.query_params.get('agency_type')
        if agency_type:
            queryset = queryset.filter(agency_type_id=agency_type)
        
        # Filter theo quận
        district = self.request.query_params.get('district')
        if district:
            queryset = queryset.filter(district_id=district)
        
        # Search theo tên
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(name__icontains=search)
        
        # Filter theo công nợ
        debt_status = self.request.query_params.get('debt_status')
        if debt_status == 'overdue':
            queryset = queryset.exclude(can_order=True)  # Công nợ vượt hạn
        elif debt_status == 'safe':
            queryset = queryset.filter(can_order=True)  # Công nợ an toàn
        
        return queryset
    
    def perform_create(self, serializer):
        # Kiểm tra số đại lý tối đa/quận (lấy từ Regulation)
        from reports.models import Regulation
        max_agencies_per_district = int(Regulation.get_value('MAX_AGENCIES_PER_DISTRICT', '999'))
        
        # Kiểm tra số đại lý trong quận
        district_id = self.request.data.get('district')
        if district_id:
            agency_count = Agency.objects.filter(district_id=district_id).count()
            if agency_count >= max_agencies_per_district:
                from rest_framework.exceptions import ValidationError
                raise ValidationError(f'Quận này đã đủ số lượng đại lý ({max_agencies_per_district})')
        
        serializer.save()
    
    @action(detail=True, methods=['get'])
    def debt_info(self, request, pk=None):
        """Xem thông tin công nợ của đại lý"""
        agency = self.get_object()
        return Response({
            'agency_id': agency.id,
            'agency_name': agency.name,
            'agency_type': agency.agency_type.name,
            'max_debt': agency.agency_type.max_debt,
            'current_debt': agency.current_debt,
            'remaining_limit': agency.remaining_debt_limit,
            'can_order': agency.can_order,
        })
    
    @action(detail=True, methods=['get'])
    def debt_history(self, request, pk=None):
        """Lịch sử phát sinh và thanh toán công nợ của đại lý"""
        from orders.models import ExportOrder
        from payments.models import Payment
        from orders.serializers import ExportOrderSerializer
        from payments.serializers import PaymentSerializer
        
        agency = self.get_object()
        
        # Lấy danh sách phát sinh (phiếu xuất hàng đã xác nhận)
        orders = ExportOrder.objects.filter(
            agency=agency,
            status__in=['confirmed', 'shipping', 'completed']
        ).order_by('-order_date')
        
        # Lấy danh sách thanh toán
        payments = Payment.objects.filter(agency=agency).order_by('-payment_date')
        
        return Response({
            'agency_id': agency.id,
            'agency_name': agency.name,
            'current_debt': agency.current_debt,
            'orders': ExportOrderSerializer(orders, many=True).data,
            'payments': PaymentSerializer(payments, many=True).data,
        })
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Thống kê đại lý"""
        total = Agency.objects.count()
        active = Agency.objects.filter(is_active=True).count()
        by_type = {}
        
        for agency_type in AgencyType.objects.all():
            by_type[agency_type.name] = Agency.objects.filter(agency_type=agency_type).count()
        
        return Response({
            'total': total,
            'active': active,
            'inactive': total - active,
            'by_type': by_type,
        })
