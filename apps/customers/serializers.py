# serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Customer
from apps.channels.serializers import ChannelSerializer

User = get_user_model()
class AgentSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    role_name = serializers.CharField(source='role.name', read_only=True)
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'full_name', 'role_name', 'department', 'status']


class CustomerSerializer(serializers.ModelSerializer):
    assigned_agent_details = AgentSerializer(source='assigned_agent', read_only=True)
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    channels = ChannelSerializer(many=True, read_only=True)

    class Meta:
        model = Customer
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)

        data['full_name'] = instance.full_name

        if instance.assigned_agent:
            data['agent_summary'] = {
                'id': instance.assigned_agent.id,
                'name': instance.assigned_agent.get_full_name(),
                'email': instance.assigned_agent.email,
                'role': instance.assigned_agent.role.name if instance.assigned_agent.role else None
            }
        else:
            data['agent_summary'] = None

        return data


class CustomerListSerializer(serializers.ModelSerializer):
    assigned_agent_name = serializers.CharField(source='assigned_agent.get_full_name', read_only=True)
    full_name = serializers.CharField(source='get_full_name', read_only=True)

    class Meta:
        model = Customer
        fields = [
            'id', 'customer_code', 'full_name', 'email', 'phone',
            'status', 'priority', 'profile', 'total_policies',
            'city', 'state', 'assigned_agent', 'assigned_agent_name',
            'created_at', 'updated_at'
        ]

class AgentAssignmentSerializer(serializers.Serializer):
    agent_id = serializers.IntegerField()

    def validate_agent_id(self, value):
        try:
            agent = User.objects.get(id=value, status='active', is_active=True)
            return value
        except User.DoesNotExist:
            raise serializers.ValidationError("Agent not found or inactive")


class BulkAgentAssignmentSerializer(serializers.Serializer):
    assignments = serializers.ListField(
        child=serializers.DictField(
            child=serializers.IntegerField()
        ),
        min_length=1
    )

    def validate_assignments(self, value):
        for assignment in value:
            if 'customer_id' not in assignment or 'agent_id' not in assignment:
                raise serializers.ValidationError(
                    "Each assignment must contain 'customer_id' and 'agent_id'"
                )
        return value