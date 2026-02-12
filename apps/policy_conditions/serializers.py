from rest_framework import serializers
from .models import PolicyCondition
from apps.policies.models import Policy


class FlexibleDescriptionField(serializers.Field):
    def to_internal_value(self, data):
        if isinstance(data, list):
            if not data:
                raise serializers.ValidationError("Description cannot be empty.")

            cleaned_items = [item.strip() for item in data if isinstance(item, str) and item.strip()]

            if not cleaned_items:
                raise serializers.ValidationError("Description cannot be empty.")

            return '\n'.join(cleaned_items)

        elif isinstance(data, str):
            if not data or not data.strip():
                raise serializers.ValidationError("Description cannot be empty.")
            return data.strip()

        else:
            raise serializers.ValidationError("Description must be a string or array of strings.")

    def to_representation(self, value):
        return value

class PolicyConditionSerializer(serializers.ModelSerializer):
    policy_id = serializers.IntegerField(write_only=True)
    policy_number = serializers.CharField(source='policy.policy_number', read_only=True)
    customer_name = serializers.CharField(source='policy.customer.full_name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    updated_by_name = serializers.CharField(source='updated_by.get_full_name', read_only=True)

    description = FlexibleDescriptionField()

    class Meta:
        model = PolicyCondition
        fields = [
            'id', 'policy_id', 'policy_number', 'customer_name', 'description',
            'created_by', 'created_by_name', 'updated_by', 'updated_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'updated_by']
    
    def validate_policy_id(self, value):
        if not Policy.objects.filter(id=value, is_deleted=False).exists():
            raise serializers.ValidationError("Policy does not exist or has been deleted.")
        return value

    def create(self, validated_data):
        policy_id = validated_data.pop('policy_id')
        validated_data['policy_id'] = policy_id
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'policy_id' in validated_data:
            policy_id = validated_data.pop('policy_id')
            validated_data['policy_id'] = policy_id
        return super().update(instance, validated_data)

class PolicyConditionListSerializer(serializers.ModelSerializer):
    policy_number = serializers.CharField(source='policy.policy_number', read_only=True)
    customer_name = serializers.CharField(source='policy.customer.full_name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)

    class Meta:
        model = PolicyCondition
        fields = [
            'id', 'policy_number', 'customer_name', 'description',
            'created_by_name', 'created_at'
        ]
