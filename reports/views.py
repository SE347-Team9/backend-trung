from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, F
from django.db import models
from datetime import datetime

from accounts.views import IsAdmin, IsStaff
from agencies.models import Agency
from orders.models import ExportOrder
from payments.models import Payment
from .models import Regulation, RevenueReport, DebtReport
from .serializers import (
    RegulationSerializer, RevenueReportSerializer, DebtReportSerializer
)

# ============================================================
# REGULATION & REPORT VIEWS
# ============================================================


class RegulationViewSet(viewsets.ModelViewSet):
    """
    API Quản lý quy định
    - Admin: Full quyền
    - Staff/Agency: Chỉ xem
    """
    queryset = Regulation.objects.all()
    serializer_class = RegulationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdmin()]
        return [IsAuthenticated()]
    
    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


class RevenueReportViewSet(viewsets.ReadOnlyModelViewSet):
    """API Báo cáo doanh số (chỉ xem)"""
    queryset = RevenueReport.objects.all().select_related('agency')
    serializer_class = RevenueReportSerializer
    permission_classes = [IsStaff]
    
    def get_queryset(self):
        queryset = self.queryset
        
        # Filter theo tháng/năm
        month = self.request.query_params.get('month')
        year = self.request.query_params.get('year')
        
        if month:
            queryset = queryset.filter(month=month)
        if year:
            queryset = queryset.filter(year=year)
        
        return queryset
    
    @action(detail=False, methods=['post'])
    def generate(self, request):
        """Tạo báo cáo doanh số và công nợ cho tháng/năm"""
        from payments.models import Payment
        
        month = request.data.get('month', datetime.now().month)
        year = request.data.get('year', datetime.now().year)
        
        # Xóa báo cáo cũ (nếu có)
        RevenueReport.objects.filter(month=month, year=year).delete()
        DebtReport.objects.filter(month=month, year=year).delete()
        
        # ========== BÁIO CÁO DOANH SỐ ==========
        # Tính tổng doanh thu tháng từ các đơn hoàn thành
        total_revenue_data = ExportOrder.objects.filter(
            order_date__month=month,
            order_date__year=year,
            status='completed'
        ).aggregate(
            total=Sum(F('items__quantity') * F('items__unit_price'), output_field=models.DecimalField())
        )
        total_revenue = total_revenue_data['total'] or 0
        
        # Tạo báo cáo doanh số cho từng đại lý
        for agency in Agency.objects.filter(is_active=True):
            orders = ExportOrder.objects.filter(
                agency=agency,
                order_date__month=month,
                order_date__year=year,
                status='completed'
            )
            
            order_count = orders.count()
            
            # Tính tổng doanh thu công ty
            agency_revenue_data = orders.aggregate(
                total=Sum(F('items__quantity') * F('items__unit_price'), output_field=models.DecimalField())
            )
            agency_revenue = agency_revenue_data['total'] or 0
            
            ratio = (float(agency_revenue) / float(total_revenue) * 100) if total_revenue > 0 else 0
            
            RevenueReport.objects.create(
                agency=agency,
                month=month,
                year=year,
                order_count=order_count,
                total_revenue=agency_revenue,
                ratio=ratio
            )
        
        # ========== BÁIO CÁO CÔNG NỢ ==========
        for agency in Agency.objects.filter(is_active=True):
            # Nợ đầu kỳ: lấy nợ cuối của tháng trước
            prev_month = month - 1 if month > 1 else 12
            prev_year = year if month > 1 else year - 1
            prev_report = DebtReport.objects.filter(
                agency=agency, month=prev_month, year=prev_year
            ).first()
            opening_debt = prev_report.closing_debt if prev_report else 0
            
            # Phát sinh: tổng tiền đặt hàng trong tháng
            orders = ExportOrder.objects.filter(
                agency=agency,
                order_date__month=month,
                order_date__year=year,
                status='completed'
            )
            incurred_data = orders.aggregate(
                total=Sum(F('items__quantity') * F('items__unit_price'), output_field=models.DecimalField())
            )
            incurred = incurred_data['total'] or 0
            
            # Đã thanh toán: tổng phiếu thu trong tháng
            payments = Payment.objects.filter(
                agency=agency,
                payment_date__month=month,
                payment_date__year=year
            )
            paid = payments.aggregate(total=Sum('amount'))['total'] or 0
            
            # Nợ cuối kỳ = Nợ đầu + Phát sinh - Đã thanh toán
            closing_debt = opening_debt + incurred - paid
            
            DebtReport.objects.create(
                agency=agency,
                month=month,
                year=year,
                opening_debt=opening_debt,
                incurred=incurred,
                paid=paid,
                closing_debt=closing_debt
            )
        
        return Response({
            'message': f'Đã tạo báo cáo doanh số và công nợ tháng {month}/{year}',
            'total_revenue': float(total_revenue)
        })


class DebtReportViewSet(viewsets.ReadOnlyModelViewSet):
    """API Báo cáo công nợ (chỉ xem)"""
    queryset = DebtReport.objects.all().select_related('agency')
    serializer_class = DebtReportSerializer
    permission_classes = [IsStaff]
    
    def get_queryset(self):
        queryset = self.queryset
        
        month = self.request.query_params.get('month')
        year = self.request.query_params.get('year')
        
        if month:
            queryset = queryset.filter(month=month)
        if year:
            queryset = queryset.filter(year=year)
        
        return queryset


class DashboardViewSet(viewsets.ViewSet):
    """
    API Dashboard - Thống kê tổng quan hệ thống
    Chỉ Admin/Staff được xem
    """
    permission_classes = [IsStaff]
    
    @action(detail=False, methods=['get'])
    def overview(self, request):
        """Tổng quan hệ thống"""
        from agencies.models import Agency, AgencyType, District
        from products.models import Product, GoodsReceipt
        from orders.models import ExportOrder
        from payments.models import Payment
        
        # ===== AGENCIES =====
        total_agencies = Agency.objects.count()
        active_agencies = Agency.objects.filter(is_active=True).count()
        total_debt = Agency.objects.aggregate(total=Sum('current_debt'))['total'] or 0
        
        # ===== PRODUCTS =====
        total_products = Product.objects.count()
        out_of_stock = Product.objects.filter(stock_quantity=0).count()
        low_stock = Product.objects.filter(stock_quantity__lt=10, stock_quantity__gt=0).count()
        
        # ===== ORDERS =====
        pending_orders = ExportOrder.objects.filter(status='pending').count()
        confirmed_orders = ExportOrder.objects.filter(status='confirmed').count()
        shipping_orders = ExportOrder.objects.filter(status='shipping').count()
        completed_orders = ExportOrder.objects.filter(status='completed').count()
        total_orders = ExportOrder.objects.count()
        
        # ===== REVENUE (THÁNG NÀY) =====
        current_month = datetime.now().month
        current_year = datetime.now().year
        month_revenue = ExportOrder.objects.filter(
            order_date__month=current_month,
            order_date__year=current_year,
            status='completed'
        ).aggregate(
            total=Sum(F('items__quantity') * F('items__unit_price'), output_field=models.DecimalField())
        )['total'] or 0
        
        return Response({
            'agencies': {
                'total': total_agencies,
                'active': active_agencies,
                'inactive': total_agencies - active_agencies,
                'total_debt': float(total_debt),
            },
            'products': {
                'total': total_products,
                'active': Product.objects.filter(is_active=True).count(),
                'out_of_stock': out_of_stock,
                'low_stock': low_stock,
            },
            'orders': {
                'total': total_orders,
                'pending': pending_orders,
                'confirmed': confirmed_orders,
                'shipping': shipping_orders,
                'completed': completed_orders,
            },
            'revenue': {
                'month': current_month,
                'year': current_year,
                'total': float(month_revenue),
            }
        })
    
    @action(detail=False, methods=['get'])
    def revenue_by_agency(self, request):
        """Doanh số theo đại lý (tháng hiện tại)"""
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        reports = RevenueReport.objects.filter(
            month=current_month,
            year=current_year
        ).select_related('agency').order_by('-total_revenue')
        
        data = []
        for report in reports:
            data.append({
                'agency_id': report.agency.id,
                'agency_name': report.agency.name,
                'total_revenue': float(report.total_revenue),
                'order_count': report.order_count,
                'ratio': float(report.ratio),
            })
        
        return Response({
            'month': current_month,
            'year': current_year,
            'data': data
        })
    
    @action(detail=False, methods=['get'])
    def debt_by_agency(self, request):
        """Công nợ theo đại lý (sắp xếp theo nợ cao nhất)"""
        agencies = Agency.objects.filter(is_active=True).order_by('-current_debt')[:10]
        
        data = []
        for agency in agencies:
            data.append({
                'agency_id': agency.id,
                'agency_name': agency.name,
                'current_debt': float(agency.current_debt),
                'max_debt': float(agency.agency_type.max_debt),
                'remaining_limit': float(agency.remaining_debt_limit),
                'status': 'OK' if agency.can_order else 'VƯỢT HẠN',
            })
        
        return Response(data)
    
    @action(detail=False, methods=['get'])
    def order_status_summary(self, request):
        """Tóm tắt trạng thái đơn hàng"""
        from django.db.models import Count
        
        summary = ExportOrder.objects.values('status').annotate(count=Count('id')).order_by('status')
        
        data = {}
        status_display = {
            'pending': 'Chờ xử lý',
            'confirmed': 'Đã xác nhận',
            'shipping': 'Đang giao',
            'completed': 'Hoàn thành',
            'cancelled': 'Đã hủy',
        }
        
        for item in summary:
            status = item['status']
            data[status] = {
                'count': item['count'],
                'display': status_display.get(status, status),
            }
        
        return Response(data)
    
    @action(detail=False, methods=['post'])
    def generate(self, request):
        """Tạo báo cáo công nợ cho tháng/năm"""
        month = request.data.get('month', datetime.now().month)
        year = request.data.get('year', datetime.now().year)
        
        # Xóa báo cáo cũ (nếu có)
        DebtReport.objects.filter(month=month, year=year).delete()
        
        for agency in Agency.objects.filter(is_active=True):
            # Tính nợ đầu kỳ (từ báo cáo tháng trước hoặc 0)
            prev_month = month - 1 if month > 1 else 12
            prev_year = year if month > 1 else year - 1
            
            try:
                prev_report = DebtReport.objects.get(
                    agency=agency, month=prev_month, year=prev_year
                )
                opening_debt = prev_report.closing_debt
            except DebtReport.DoesNotExist:
                opening_debt = 0
            
            # Tính phát sinh (tổng đơn hàng trong tháng)
            orders = ExportOrder.objects.filter(
                agency=agency,
                order_date__month=month,
                order_date__year=year,
                status='completed'
            )
            incurred = sum(order.total_amount for order in orders)
            
            # Tính đã thu
            payments = Payment.objects.filter(
                agency=agency,
                payment_date__month=month,
                payment_date__year=year
            )
            paid = sum(p.amount for p in payments)
            
            # Nợ cuối kỳ
            closing_debt = opening_debt + incurred - paid
            
            DebtReport.objects.create(
                agency=agency,
                month=month,
                year=year,
                opening_debt=opening_debt,
                incurred=incurred,
                paid=paid,
                closing_debt=closing_debt
            )
        
        return Response({
            'message': f'Đã tạo báo cáo công nợ tháng {month}/{year}'
        })
