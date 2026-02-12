from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PolicyFeatureViewSet

router = DefaultRouter()
router.register(r'', PolicyFeatureViewSet, basename='policy-features')

urlpatterns = [
    path('', include(router.urls)),
]
