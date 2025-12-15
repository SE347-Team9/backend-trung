from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'regulations', views.RegulationViewSet, basename='regulation')
router.register(r'revenue', views.RevenueReportViewSet, basename='revenue-report')
router.register(r'debt', views.DebtReportViewSet, basename='debt-report')
router.register(r'dashboard', views.DashboardViewSet, basename='dashboard')

urlpatterns = [
    path('', include(router.urls)),
]
