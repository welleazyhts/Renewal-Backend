from rest_framework import serializers
from .models import PolicyExclusion
from apps.policies.models import Policy
class PolicyExclusionSerializer(serializers.ModelSerializer):
    policy_number = serializers.CharField(source='policy.policy_number', read_only=True)
    policy_type_name = serializers.CharField(source='policy.policy_type.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    updated_by_name = serializers.CharField(source='updated_by.get_full_name', read_only=True)

    class Meta:
        model = PolicyExclusion
        fields = [
            'id', 'policy', 'policy_number', 'policy_type_name',
            'exclusion_type', 'description',
            'created_by', 'created_by_name', 'updated_by', 'updated_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class PolicyExclusionCreateSerializer(serializers.ModelSerializer):

    policy_id = serializers.IntegerField(write_only=True)

    description = serializers.CharField(required=True)

    policy_number = serializers.CharField(source='policy.policy_number', read_only=True)
    policy_type_name = serializers.CharField(source='policy.policy_type.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    exclusion_type_display = serializers.CharField(source='get_exclusion_type_display', read_only=True)

    class Meta:
        model = PolicyExclusion
        fields = [
            'id', 'policy_id', 'policy_number', 'policy_type_name',
            'exclusion_type', 'exclusion_type_display', 'description',
            'created_by', 'created_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def to_internal_value(self, data):
        data = data.copy() if hasattr(data, 'copy') else dict(data)

        if 'description' in data:
            description = data['description']
            if isinstance(description, list):
                data['description'] = '\n'.join([f"• {item}" for item in description])
            elif not isinstance(description, str):
                data['description'] = str(description)

        return super().to_internal_value(data)

    def validate_policy_id(self, value):
        if not Policy.objects.filter(id=value, is_deleted=False).exists():
            raise serializers.ValidationError("Policy does not exist or is deleted.")
        return value

    def create(self, validated_data):
        policy_id = validated_data.pop('policy_id')

        policy = Policy.objects.get(id=policy_id)
        validated_data['policy'] = policy

        return super().create(validated_data)


class PolicyExclusionUpdateSerializer(serializers.ModelSerializer):

    description = serializers.CharField(required=False)

    class Meta:
        model = PolicyExclusion
        fields = [
            'exclusion_type', 'description'
        ]

    def to_internal_value(self, data):
        data = data.copy() if hasattr(data, 'copy') else dict(data)

        if 'description' in data:
            description = data['description']
            if isinstance(description, list):
                data['description'] = '\n'.join([f"• {item}" for item in description])
            elif not isinstance(description, str):
                data['description'] = str(description)

        return super().to_internal_value(data)

class PolicyExclusionDetailSerializer(serializers.ModelSerializer):

    policy_number = serializers.CharField(source='policy.policy_number', read_only=True)
    policy_type_name = serializers.CharField(source='policy.policy_type.name', read_only=True)
    exclusion_type_display = serializers.CharField(source='get_exclusion_type_display', read_only=True)

    class Meta:
        model = PolicyExclusion
        fields = [
            'id', 'policy_number', 'policy_type_name',
            'exclusion_type', 'exclusion_type_display', 'description',
            'created_at', 'updated_at'
        ]
