from rest_framework import serializers
from .models import CommonRenewalTimelineSettings
from typing import Any 

class CommonRenewalTimelineSettingsSerializer(serializers.ModelSerializer):    
    class Meta:
        model = CommonRenewalTimelineSettings
        fields = [
            'id',
            'renewal_pattern',
            'reminder_days',
            'reminder_schedule',
            'auto_renewal_enabled',
            'is_active',
            'description',
            'created_at',
            'updated_at',
            'created_by',
            'updated_by',
        ]
        read_only_fields = ['created_at', 'updated_at', 'created_by', 'updated_by']


class CommonRenewalTimelineSettingsCreateSerializer(serializers.ModelSerializer):    
    class Meta:
        model = CommonRenewalTimelineSettings
        fields = [
            'renewal_pattern',
            'reminder_days',
            'reminder_schedule',
            'auto_renewal_enabled',
            'is_active',
            'description',
        ]


