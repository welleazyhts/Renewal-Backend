from rest_framework.routers import DefaultRouter
from .views import (
    KnowledgeDocumentViewSet,
    KnowledgeWebsiteViewSet,
    DocumentModuleViewSet,
)

router = DefaultRouter()

router.register(
    r"documents",
    KnowledgeDocumentViewSet,
    basename="knowledge-documents",
)

router.register(
    r"websites",
    KnowledgeWebsiteViewSet,
    basename="knowledge-websites",
)

router.register(
    r"document-modules",
    DocumentModuleViewSet,
    basename="document-modules",
)

urlpatterns = router.urls
