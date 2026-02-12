from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Region, State, Branch, Department, Team

try:
    from apps.users.models import Role
except ImportError:
    from users.models import Role

User = get_user_model()

class NodeSerializer(serializers.ModelSerializer):
    manager_id = serializers.CharField(write_only=True)
    
    manager_name = serializers.CharField(source='manager.first_name', read_only=True)

    def validate_manager_id(self, value):
        try:
            user = User.objects.get(pk=value)
        except User.DoesNotExist:
            raise serializers.ValidationError(f"User with Database ID '{value}' not found.")

        if not user.role:
             raise serializers.ValidationError(f"User '{user.first_name}' has no role assigned.")
        
        role_name = user.role.name.lower()
        if 'manager' not in role_name and 'admin' not in role_name:
            raise serializers.ValidationError(
                f"User '{user.first_name}' is a '{user.role.name}'. This role is not allowed."
            )

        return user

    def create(self, validated_data):
        if 'manager_id' in validated_data:
            validated_data['manager'] = validated_data.pop('manager_id')
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'manager_id' in validated_data:
            validated_data['manager'] = validated_data.pop('manager_id')
        return super().update(instance, validated_data)

class RegionSerializer(NodeSerializer):
    level = serializers.SerializerMethodField()
    def get_level(self, obj): return "Region"
    class Meta:
        model = Region
        fields = ['id', 'unit_name', 'description', 'manager_id', 'manager_name', 'budget', 'target_cases', 'status', 'level']

class StateSerializer(NodeSerializer):
    parent_id = serializers.PrimaryKeyRelatedField(queryset=Region.objects.all(), source='region', write_only=True)
    
    level = serializers.SerializerMethodField()
    def get_level(self, obj): return "State"
    class Meta:
        model = State
        fields = ['id', 'unit_name', 'parent_id', 'description', 'manager_id', 'manager_name', 'budget', 'target_cases', 'status', 'level']

class BranchSerializer(NodeSerializer):
    parent_id = serializers.PrimaryKeyRelatedField(queryset=State.objects.all(), source='state', write_only=True)
    
    level = serializers.SerializerMethodField()
    def get_level(self, obj): return "Branch"
    class Meta:
        model = Branch
        fields = ['id', 'unit_name', 'parent_id', 'description', 'manager_id', 'manager_name', 'budget', 'target_cases', 'status', 'level']

class DepartmentSerializer(NodeSerializer):
    parent_id = serializers.PrimaryKeyRelatedField(queryset=Branch.objects.all(), source='branch', write_only=True)
    
    level = serializers.SerializerMethodField()
    def get_level(self, obj): return "Department"
    class Meta:
        model = Department
        fields = ['id', 'unit_name', 'parent_id', 'description', 'manager_id', 'manager_name', 'budget', 'target_cases', 'status', 'level']

class TeamSerializer(NodeSerializer):
    parent_id = serializers.PrimaryKeyRelatedField(queryset=Department.objects.all(), source='department', write_only=True)
    
    level = serializers.SerializerMethodField()
    def get_level(self, obj): return "Team"
    class Meta:
        model = Team
        fields = ['id', 'unit_name', 'parent_id', 'description', 'manager_id', 'manager_name', 'budget', 'target_cases', 'status', 'level']