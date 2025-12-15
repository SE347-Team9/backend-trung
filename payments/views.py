from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from accounts.views import IsAdmin, IsStaff
from .models import Payment
from .serializers import PaymentSerializer, PaymentCreateSerializer

# ============================================================
# PAYMENT VIEWS
# ============================================================


class PaymentViewSet(viewsets.ModelViewSet):
    """
    API Quản lý phiếu thu tiền
    - Admin/Staff: Full quyền
    - Agency: Chỉ xem phiếu thu của mình
    """
    queryset = Payment.objects.all().select_related('agency', 'received_by')
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return PaymentCreateSerializer
        return PaymentSerializer
    
    def get_queryset(self):
        user = self.request.user
        queryset = self.queryset
        
        # Agency chỉ xem được phiếu thu của mình
        if user.role == 'agency':
            return queryset.filter(agency__user=user)
        
        # Filter theo đại lý
        agency = self.request.query_params.get('agency')
        if agency:
            queryset = queryset.filter(agency_id=agency)
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(received_by=self.request.user)
