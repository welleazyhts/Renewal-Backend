from django.urls import path
from .views import (
    SystemSettingsView,
    AIBasicConfigView,
    AIFeaturesView,
    RateLimitingView,
    AdvancedConfigView,
    KnowledgeBaseView,
    KnowledgeBaseUpdateView,
    SystemPerformanceView,
    OllamaConfigView,
    TestAIConnectionView,
    OllamaModelsView,
    AIProvidersView,
)

urlpatterns = [
    path("settings/", SystemSettingsView.as_view(), name="system-settings"),
    
    path("ai-providers/", AIProvidersView.as_view(), name="ai-providers"),
    
    path("ai-config/", AIBasicConfigView.as_view(), name="ai-basic-config"),
    
    path("ai-features/", AIFeaturesView.as_view(), name="ai-features"),
    
    path("rate-limiting/", RateLimitingView.as_view(), name="rate-limiting"),
    
    path("advanced-config/", AdvancedConfigView.as_view(), name="advanced-config"),
    
    path("knowledge-base/", KnowledgeBaseView.as_view(), name="knowledge-base"),
    path("knowledge-base", KnowledgeBaseView.as_view(), name="knowledge-base-no-slash"),
    path("knowledge-base/update/", KnowledgeBaseUpdateView.as_view(), name="knowledge-base-update"),
    
    path("performance/", SystemPerformanceView.as_view(), name="system-performance"),
    
    path("ollama-config/", OllamaConfigView.as_view(), name="ollama-config"),
    path("ollama-models/", OllamaModelsView.as_view(), name="ollama-models"),
    
    path("test-connection/", TestAIConnectionView.as_view(), name="test-ai-connection"),
]
