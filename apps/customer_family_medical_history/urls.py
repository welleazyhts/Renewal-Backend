
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'customer_family_medical_history'

router = DefaultRouter()
router.register(r'', views.CustomerFamilyMedicalHistoryViewSet, basename='customer-family-medical-history')

urlpatterns = [
    path('', include(router.urls)),
]
