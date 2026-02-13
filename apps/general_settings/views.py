import qrcode
import base64
from io import BytesIO
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import UserSettings
from .serializers import UserSettingsSerializer
from django_otp.plugins.otp_totp.models import TOTPDevice

class GeneralSettingsViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSettingsSerializer

    def get_object(self):
        obj, created = UserSettings.objects.get_or_create(user=self.request.user)
        return obj

    @action(detail=False, methods=['get', 'patch'])
    def my_settings(self, request):
        settings_obj = self.get_object()

        if request.method == 'GET':
            serializer = self.get_serializer(settings_obj)
            return Response(serializer.data)

        elif request.method == 'PATCH':
            serializer = self.get_serializer(settings_obj, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "status": "success", 
                    "message": "Settings updated successfully", 
                    "data": serializer.data
                })
            return Response(serializer.errors, status=400)


class MFAViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def generate_qr(self, request):
        user = request.user
        
        device, created = TOTPDevice.objects.get_or_create(user=user, confirmed=False, defaults={'name': 'default'})

        otp_uri = device.config_url

        qr = qrcode.make(otp_uri)
        buffer = BytesIO()
        qr.save(buffer, format="PNG")
        qr_base64 = base64.b64encode(buffer.getvalue()).decode()

        return Response({
            "status": "pending",
            "message": "Scan this QR code with Google Authenticator",
            "qr_code_base64": f"data:image/png;base64,{qr_base64}",
            "manual_entry_key": base64.b32encode(device.bin_key).decode('utf-8') 
        })

    @action(detail=False, methods=['post'])
    def verify_and_enable(self, request):
        user = request.user
        otp_code = request.data.get('otp')

        if not otp_code:
            return Response({"error": "OTP code is required"}, status=400)

        device = TOTPDevice.objects.filter(user=user, confirmed=False).first()
        
        if not device:
            return Response({"error": "No setup pending. Please generate QR first."}, status=400)

        if device.verify_token(otp_code):
            device.confirmed = True
            device.save()
            
            settings, _ = UserSettings.objects.get_or_create(user=user)
            settings.mfa_enabled = True
            settings.save()

            return Response({"status": "success", "message": "MFA Enabled Successfully"})
        
        return Response({"error": "Invalid OTP Code"}, status=400)

    @action(detail=False, methods=['post'])
    def disable(self, request):
        user = request.user
        
        TOTPDevice.objects.filter(user=user).delete()
        
        settings, _ = UserSettings.objects.get_or_create(user=user)
        settings.mfa_enabled = False
        settings.save()
        
        return Response({"status": "success", "message": "MFA Disabled"})