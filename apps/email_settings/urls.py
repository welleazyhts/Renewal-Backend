from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (EmailAccountViewSet, ClassificationRuleViewSet, EmailModuleSettingsAPIView,TestConnectionAPIView,ProviderDefaultsAPIView,
    GlobalTestConnectionAPIView,ManualSyncAPIView)

router = DefaultRouter()
router.register(r'email-accounts', EmailAccountViewSet, basename='emailaccount')
router.register(r'classification-rules', ClassificationRuleViewSet, basename='classificationrule')

urlpatterns = [
    path('', include(router.urls)),
    
    path('general/', EmailModuleSettingsAPIView.as_view(), name='general-settings'),
    path('email-accounts/<int:pk>/test-connection/', TestConnectionAPIView.as_view(), name='email-account-test-connection'),
    path('email-accounts/<int:pk>/sync-now/', ManualSyncAPIView.as_view(), name='manual-sync'),
    path('providers/defaults/', ProviderDefaultsAPIView.as_view(), name='provider-defaults'),
    path('test-global-connection/', GlobalTestConnectionAPIView.as_view(), name='global-test-connection'),
]

