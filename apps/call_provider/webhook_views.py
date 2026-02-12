import logging

from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import CallProviderConfig
from .services import CallProviderService

logger = logging.getLogger(__name__)


class TwilioStatusCallbackView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, provider_id: int, *args, **kwargs):
        provider = get_object_or_404(
            CallProviderConfig,
            id=provider_id,
            is_deleted=False,
        )

        call_sid = request.data.get("CallSid")
        call_status = request.data.get("CallStatus")     
        duration = request.data.get("CallDuration")

        terminal_statuses = {"completed", "failed", "busy", "no-answer", "canceled"}
        if call_status in terminal_statuses:
            success = call_status == "completed"

            try:
                CallProviderService.log_usage_for_provider(
                    provider=provider,
                    status=call_status,
                    success=success,
                    duration=float(duration) if duration else None,
                    extra={
                        "provider_type": "twilio",
                        "call_sid": call_sid,
                        "raw_payload": dict(request.data),
                    },
                )
            except Exception as exc:
                logger.exception(
                    "Failed to log Twilio callback for provider %s: %s",
                    provider.id, exc
                )

        return Response("OK")


class ExotelStatusCallbackView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, provider_id: int, *args, **kwargs):
        provider = get_object_or_404(
            CallProviderConfig,
            id=provider_id,
            is_deleted=False,
        )

        status_str = (
            request.data.get("Status")
            or request.data.get("status")
            or request.data.get("CallStatus")
            or "unknown"
        )
        status_str = str(status_str).lower()

        duration = (
            request.data.get("CallDuration")
            or request.data.get("duration")
            or request.data.get("call_duration")
        )

        success = status_str in {"completed", "answered", "success"}

        try:
            CallProviderService.log_usage_for_provider(
                provider=provider,
                status=status_str,
                success=success,
                duration=float(duration) if duration else None,
                extra={
                    "provider_type": "exotel",
                    "raw_payload": dict(request.data),
                },
            )
        except Exception as exc:
            logger.exception(
                "Failed to log Exotel callback for provider %s: %s",
                provider.id, exc
            )

        return Response("OK")


class UbonaStatusCallbackView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, provider_id: int, *args, **kwargs):
        provider = get_object_or_404(
            CallProviderConfig,
            id=provider_id,
            is_deleted=False,
        )

        status_str = (
            request.data.get("status")
            or request.data.get("Status")
            or "unknown"
        )
        status_str = str(status_str).lower()

        duration = (
            request.data.get("duration")
            or request.data.get("CallDuration")
            or request.data.get("call_duration")
        )

        success = status_str in {"completed", "answered", "success"}

        try:
            CallProviderService.log_usage_for_provider(
                provider=provider,
                status=status_str,
                success=success,
                duration=float(duration) if duration else None,
                extra={
                    "provider_type": "ubona",
                    "raw_payload": dict(request.data),
                },
            )
        except Exception as exc:
            logger.exception(
                "Failed to log Ubona callback for provider %s: %s",
                provider.id, exc
            )

        return Response("OK")
