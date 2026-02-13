import imaplib
import smtplib
from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .utils import PROVIDER_DEFAULTS
from .utils import test_account_connection
from django.utils import timezone 
from .models import EmailAccount, EmailModuleSettings, ClassificationRule
from .serializers import EmailAccountSerializer, EmailModuleSettingsSerializer, ClassificationRuleSerializer
from .services import EmailSyncService
from rest_framework.decorators import action

class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if isinstance(obj, EmailModuleSettings):
            return obj.user_id == request.user.id
        return obj.user == request.user

class EmailAccountViewSet(viewsets.ModelViewSet):
    serializer_class = EmailAccountSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    @action(detail=True, methods=['post'], url_path='set-sync')
    def set_sync_status(self, request, pk=None):
        account = self.get_object()
        enable_sync = request.data.get('enabled')
        
        if enable_sync is None:
            return Response(
                {"error": "Missing 'enabled' field. Send { 'enabled': true } or { 'enabled': false }"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        account.auto_sync_enabled = bool(enable_sync)
        account.updated_by = request.user
        account.save()
        
        state_text = "activated" if account.auto_sync_enabled else "deactivated"
        return Response({
            "success": True, 
            "message": f"Auto-sync {state_text} for {account.account_name}",
            "auto_sync_enabled": account.auto_sync_enabled
        })

    def get_queryset(self):
        return EmailAccount.objects.filter(user=self.request.user, is_deleted=False).order_by('account_name')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def perform_destroy(self, instance):
        instance.soft_delete(self.request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)

class ClassificationRuleViewSet(viewsets.ModelViewSet):
    serializer_class = ClassificationRuleSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        return ClassificationRule.objects.filter(user=self.request.user, is_deleted=False).order_by('priority', 'keyword')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)
        
    def perform_destroy(self, instance):
        instance.soft_delete(self.request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)
        
class EmailModuleSettingsAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        settings, created = EmailModuleSettings.objects.get_or_create(
            user=request.user,
            defaults={'created_by': request.user, 'updated_by': request.user}
        )
        serializer = EmailModuleSettingsSerializer(settings)
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        settings = get_object_or_404(EmailModuleSettings, user=request.user)
        serializer = EmailModuleSettingsSerializer(settings, data=request.data)
        if serializer.is_valid():
            serializer.save(updated_by=request.user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, *args, **kwargs):
        settings = get_object_or_404(EmailModuleSettings, user=request.user)
        serializer = EmailModuleSettingsSerializer(settings, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(updated_by=request.user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TestConnectionAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        account = get_object_or_404(EmailAccount, pk=pk, user=request.user, is_deleted=False)
        test_results = test_account_connection(account)
        account.connection_status = test_results['success']
        account.last_sync_at = timezone.now()
        if not test_results['success']:
            error_log = f"IMAP: {test_results.get('imap_status')} | SMTP: {test_results.get('smtp_status')}"
            account.last_sync_log = error_log
        else:
            account.last_sync_log = "Connection successful."
        account.updated_by = request.user
        account.save()
        return Response(test_results, status=status.HTTP_200_OK)
    
class ProviderDefaultsAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(PROVIDER_DEFAULTS)

class GlobalTestConnectionAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        account = EmailAccount.objects.filter(user=request.user, is_deleted=False).first()
        
        if not account:
            return Response(
                {"success": False, "error": "No saved email accounts found to test."}, 
                status=status.HTTP_404_NOT_FOUND
            )

        test_results = test_account_connection(account)

        settings, _ = EmailModuleSettings.objects.get_or_create(user=request.user)
        settings.imap_connection_status = test_results['success']
        settings.save()

        account.connection_status = test_results['success']
        account.last_sync_at = timezone.now()
        account.save()

        return Response(test_results)
class ManualSyncAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        account = get_object_or_404(EmailAccount, pk=pk, user=request.user)
        
        service = EmailSyncService()
        result = service.sync_account(account.id)
        
        return Response(result)