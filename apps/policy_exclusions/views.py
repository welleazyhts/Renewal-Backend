from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from .models import PolicyExclusion
from .serializers import (
    PolicyExclusionSerializer,
    PolicyExclusionCreateSerializer,
    PolicyExclusionUpdateSerializer,
    PolicyExclusionDetailSerializer
)

class PolicyExclusionViewSet(viewsets.ModelViewSet):    
    queryset = PolicyExclusion.objects.select_related(
        'policy', 'policy__policy_type', 'created_by', 'updated_by'
    ).filter(is_deleted=False)
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['policy', 'exclusion_type', 'policy__policy_type']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return PolicyExclusionCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return PolicyExclusionUpdateSerializer
        return PolicyExclusionSerializer
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)
    
    def perform_destroy(self, instance):
        instance.delete(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def by_policy(self, request):
        policy_id = request.query_params.get('policy_id')
        policy_number = request.query_params.get('policy_number')
        
        if not policy_id and not policy_number:
            return Response(
                {'error': 'Either policy_id or policy_number is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset()
        
        if policy_id:
            queryset = queryset.filter(policy_id=policy_id)
        elif policy_number:
            queryset = queryset.filter(policy__policy_number__iexact=policy_number)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        search_term = request.query_params.get('search', '').strip()

        if not search_term:
            return Response(
                {'error': 'Search term is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        queryset = self.get_queryset().filter(
            Q(description__icontains=search_term) |
            Q(exclusion_type__icontains=search_term) |
            Q(policy__policy_number__icontains=search_term)
        )

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def detailed_view(self, request):
        policy_id = request.query_params.get('policy_id')
        policy_number = request.query_params.get('policy_number')

        queryset = self.get_queryset()

        if policy_id:
            queryset = queryset.filter(policy_id=policy_id)
        elif policy_number:
            queryset = queryset.filter(policy__policy_number__iexact=policy_number)

        exclusions_by_type = {}
        for exclusion in queryset:
            exclusion_type = exclusion.get_exclusion_type_display()
            if exclusion_type not in exclusions_by_type:
                exclusions_by_type[exclusion_type] = {
                    'type': exclusion_type,
                    'category': exclusion.exclusion_type,
                    'items': [],
                    'color_class': self._get_color_class(exclusion.exclusion_type)
                }

            if exclusion.description:
                lines = exclusion.description.split('\n')
                for line in lines:
                    line = line.strip()
                    if line:
                        cleaned_line = line.lstrip('•-*').strip()
                        if cleaned_line and cleaned_line not in exclusions_by_type[exclusion_type]['items']:
                            exclusions_by_type[exclusion_type]['items'].append(cleaned_line)

        return Response({
            'policy_id': policy_id,
            'policy_number': policy_number,
            'exclusions': list(exclusions_by_type.values()),
            'total_categories': len(exclusions_by_type)
        })

    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        exclusions_data = request.data.get('exclusions', [])

        if not exclusions_data:
            return Response(
                {'error': 'exclusions data is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        created_exclusions = []
        errors = []

        for idx, exclusion_data in enumerate(exclusions_data):
            serializer = PolicyExclusionCreateSerializer(data=exclusion_data)
            if serializer.is_valid():
                exclusion = serializer.save(created_by=request.user)
                created_exclusions.append(PolicyExclusionSerializer(exclusion).data)
            else:
                errors.append({
                    'index': idx,
                    'data': exclusion_data,
                    'errors': serializer.errors
                })

        return Response({
            'created': created_exclusions,
            'errors': errors,
            'total_created': len(created_exclusions),
            'total_errors': len(errors)
        })

    def _get_color_class(self, exclusion_type):
        color_mapping = {
            'not_covered': 'danger', 
            'conditions_apply': 'warning', 
            'partial_coverage': 'info',  
            'waiting_period': 'secondary',  
            'geographical_limit': 'primary', 
            'age_limit': 'dark', 
            'pre_existing_condition': 'danger', 
            'activity_exclusion': 'warning', 
            'other': 'secondary' 
        }
        return color_mapping.get(exclusion_type, 'secondary')
