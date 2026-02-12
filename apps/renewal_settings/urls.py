from django.urls import path
from .views import (
    RenewalSettingsView, 
    RenewalSettingsDetailView, 
    QuickMessageSettingsView,
    TestCallIntegrationView,
    TestSmsIntegrationView,
    TestWhatsAppIntegrationView,
    PolicySettingsView,
    AutoRefreshSettingsView, 
    CallIntegrationGlobalView,
    IntegrationSettingsView
)
from .quick_views import QuickMessageSendView

urlpatterns = [
    path('', RenewalSettingsView.as_view(), name='renewal-settings-list'),
    
    path('auto-refresh/', AutoRefreshSettingsView.as_view(), name='auto-refresh-settings'),
    
    path('policy-processing/', PolicySettingsView.as_view(), name='policy-settings'),
    
    path('call-integration/', CallIntegrationGlobalView.as_view(), name='call-integration-global'),
    path('call-integration/<int:provider_id>/', RenewalSettingsDetailView.as_view(), name='call-integration-detail'),
    
    path('integration-settings/', IntegrationSettingsView.as_view(), name='integration-settings'),

    path('<int:provider_id>/', RenewalSettingsDetailView.as_view(), name='renewal-settings-detail'),

    path('quick-message-settings/', QuickMessageSettingsView.as_view(), name='quick-message-settings'),
    path('quick-messages/send/', QuickMessageSendView.as_view(), name='send-quick-message'),

    path('test-integration/call/', TestCallIntegrationView.as_view(), name='test-call-integration'),
    path('test-integration/sms/', TestSmsIntegrationView.as_view(), name='test-sms-integration'),
    path('test-integration/whatsapp/', TestWhatsAppIntegrationView.as_view(), name='test-whatsapp-integration'),
]