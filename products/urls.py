from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'units', views.UnitViewSet, basename='unit')
router.register(r'receipts', views.GoodsReceiptViewSet, basename='goods-receipt')
router.register(r'', views.ProductViewSet, basename='product')

urlpatterns = [
    path('', include(router.urls)),
]
