from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.http import HttpResponse
from django.utils import timezone
from .models import SmsProvider, SmsMessage
from apps.billing.models import CommunicationLog
from .serializers import (
    SmsProviderSerializer,
    SmsProviderCreateUpdateSerializer,
    SmsMessageSerializer
)
from .services import SmsService


class SmsProviderViewSet(viewsets.ModelViewSet):
    queryset = SmsProvider.objects.filter(is_deleted=False)
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return SmsProviderCreateUpdateSerializer
        return SmsProviderSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.is_active = False
        instance.save()

    @action(detail=True, methods=['post'], url_path='health-check')
    def health_check(self, request, pk=None):
        provider = self.get_object()
        try:
            service = SmsService().get_service_instance(provider.id)
            if hasattr(service, 'health_check'):
                result = service.health_check()
            else:
                result = {'status': 'unknown', 'error': 'Health check not implemented for this provider'}

            provider.status = result.get('status', 'disconnected')
            provider.last_sent_at = timezone.now()
            provider.save(update_fields=['status', 'last_sent_at'])
            
            return Response(result)
        except Exception as e:
            return Response({'status': 'disconnected', 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['patch'], url_path='set-default')
    def set_default(self, request, pk=None):
        provider = self.get_object()
        
        desired_state = request.data.get('is_default')

        if desired_state is None:
             desired_state = True

        if desired_state and not provider.is_active:
            return Response(
                {"error": "Cannot set an inactive provider as default."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        provider.is_default = desired_state
        provider.save()
        return Response(SmsProviderSerializer(provider).data)

    @action(detail=True, methods=['post'], url_path='toggle-active')
    def toggle_active(self, request, pk=None):
        provider = self.get_object()
        provider.is_active = not provider.is_active
        provider.save()
        return Response(SmsProviderSerializer(provider).data)


class SmsMessageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SmsMessage.objects.all()
    serializer_class = SmsMessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['provider', 'status', 'to_phone_number']
    search_fields = ['content', 'to_phone_number', 'message_sid']


class SmsWebhookView(APIView):
    permission_classes = [AllowAny] 
    authentication_classes = []

    def post(self, request, provider_type=None):
        if provider_type == 'twilio':
            message_sid = request.POST.get('MessageSid')
            message_status = request.POST.get('MessageStatus') 
            error_code = request.POST.get('ErrorCode')
            
            print(f"📩 TWILIO WEBHOOK: {message_sid} -> {message_status}")

            if message_sid and message_status:
                try:
                    sms_obj = SmsMessage.objects.get(message_sid=message_sid)
                    
                    sms_obj.status = message_status
                    
                    if error_code:
                        sms_obj.error_code = error_code
                        sms_obj.error_message = "Twilio Error Code: " + str(error_code)
                    
                    if message_status == 'sent':
                        sms_obj.sent_at = timezone.now()
                    elif message_status == 'delivered':
                        sms_obj.delivered_at = timezone.now()
                    
                    sms_obj.save()
                    billing_status = message_status
                    if message_status in ['undelivered', 'failed']:
                        billing_status = 'failed'
                    
                    CommunicationLog.objects.filter(provider_message_id=message_sid).update(status=billing_status)
                    
                except SmsMessage.DoesNotExist:
                    print(f"⚠️ Message SID {message_sid} not found in local DB.")
            
            return HttpResponse("<Response></Response>", content_type="text/xml")
            
        return Response(status=status.HTTP_400_BAD_REQUEST)
