from rest_framework import serializers
from .models import PolicyCoverage
from apps.policies.models import PolicyType

class PolicyCoverageSerializer(serializers.ModelSerializer):

    policy_type_id = serializers.IntegerField(write_only=True)
    policy_type_name = serializers.CharField(source='policy_type.name', read_only=True)
    policy_type_code = serializers.CharField(source='policy_type.code', read_only=True)
    policy_type_category = serializers.CharField(source='policy_type.category', read_only=True)

    class Meta:
        model = PolicyCoverage
        fields = [
            'id', 'policy_type_id', 'policy_type_name', 'policy_type_code', 'policy_type_category',
            'coverage_type', 'coverage_category', 'coverage_name', 'coverage_description',
            'coverage_amount', 'deductible_amount', 'coverage_percentage',
            'is_included', 'is_optional', 'premium_impact', 'display_order',
            'terms_conditions', 'exclusions', 'additional_info', 'support_coverage',
            'created_at', 'updated_at', 'created_by', 'updated_by'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_policy_type_id(self, value):
        if not PolicyType.objects.filter(id=value, is_deleted=False).exists():
            raise serializers.ValidationError("Policy type does not exist or has been deleted.")
        return value

    def create(self, validated_data):
        policy_type_id = validated_data.pop('policy_type_id')
        validated_data['policy_type_id'] = policy_type_id
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'policy_type_id' in validated_data:
            policy_type_id = validated_data.pop('policy_type_id')
            validated_data['policy_type_id'] = policy_type_id
        return super().update(instance, validated_data)
    
    def validate_coverage_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Coverage name cannot be empty.")
        return value.strip()
    
    def validate_coverage_description(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Coverage description cannot be empty.")
        return value.strip()
    
    def validate_coverage_amount(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("Coverage amount cannot be negative.")
        return value
    
    def validate_deductible_amount(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("Deductible amount cannot be negative.")
        return value
    
    def validate_coverage_percentage(self, value):
        if value is not None and (value < 0 or value > 100):
            raise serializers.ValidationError("Coverage percentage must be between 0 and 100.")
        return value
    
    def validate_premium_impact(self, value):
        if value < 0:
            raise serializers.ValidationError("Premium impact cannot be negative.")
        return value


class PolicyCoverageListSerializer(serializers.ModelSerializer):

    policy_type_name = serializers.CharField(source='policy_type.name', read_only=True)
    policy_type_category = serializers.CharField(source='policy_type.category', read_only=True)

    class Meta:
        model = PolicyCoverage
        fields = [
            'id', 'policy_type_name', 'policy_type_category', 'coverage_type',
            'coverage_category', 'coverage_name', 'coverage_description',
            'coverage_amount', 'deductible_amount', 'coverage_percentage',
            'is_included', 'is_optional', 'premium_impact', 'support_coverage', 'created_at'
        ]

class PolicyCoverageSummarySerializer(serializers.ModelSerializer):    
    class Meta:
        model = PolicyCoverage
        fields = [
            'id', 'coverage_type', 'coverage_name', 'coverage_amount',
            'deductible_amount', 'coverage_percentage', 'is_included', 'support_coverage'
        ]
