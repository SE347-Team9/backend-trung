from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'districts', views.DistrictViewSet, basename='district')
router.register(r'types', views.AgencyTypeViewSet, basename='agency-type')
router.register(r'', views.AgencyViewSet, basename='agency')

urlpatterns = [
    path('', include(router.urls)),
]
