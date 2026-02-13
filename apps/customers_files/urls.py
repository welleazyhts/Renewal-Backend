from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CustomerFileViewSet

router = DefaultRouter()
router.register(r'customer-files', CustomerFileViewSet, basename='customer-files')

urlpatterns = [
    path('', include(router.urls)),
]
