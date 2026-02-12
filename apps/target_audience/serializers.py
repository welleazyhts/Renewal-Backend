from rest_framework import serializers
from .models import TargetAudience


class TargetAudienceSerializer(serializers.ModelSerializer):    
    class Meta:
        model = TargetAudience
        fields = [
            'id',
            'key', 
            'name',
            'description',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TargetAudienceListSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = TargetAudience
        fields = [
            'id',
            'name',
            'description'
        ]


class TargetAudienceCreateSerializer(serializers.ModelSerializer):    
    class Meta:
        model = TargetAudience
        fields = [
            'key',
            'name', 
            'description'
        ]
    
    def validate_key(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Key cannot be empty.")
        
        if TargetAudience.objects.filter(key=value.strip()).exists():
            raise serializers.ValidationError("A target audience with this key already exists.")
        
        return value.strip()
    
    def validate_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Name cannot be empty.")
        return value.strip()
