from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Q, Count, Sum
from .models import CustomerFile
from .serializers import (
    CustomerFileSerializer,
    CustomerFileListSerializer
)
from apps.core.pagination import StandardResultsSetPagination

class CustomerFileViewSet(viewsets.ModelViewSet):
    queryset = CustomerFile.objects.select_related(
        'uploaded_by', 'updated_by', 'customer'
    ).filter(is_active=True)

    serializer_class = CustomerFileSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    filterset_fields = [
        'customer', 'file_type', 'uploaded_by', 'is_active'
    ]

    search_fields = [
        'file_name', 'file_type'
    ]
    
    ordering_fields = [
        'uploaded_at', 'updated_at', 'file_name', 'file_size'
    ]
    ordering = ['-uploaded_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return CustomerFileListSerializer
        return CustomerFileSerializer
    
    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)
    
    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.updated_by = self.request.user
        instance.save()
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        return Response({
            'success': True,
            'message': 'Customer file uploaded successfully',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response({
                'success': True,
                'message': 'Customer files retrieved successfully',
                'data': serializer.data
            })
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'message': 'Customer files retrieved successfully',
            'data': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def by_customer(self, request):
        customer_id = request.query_params.get('customer_id')

        if not customer_id:
            return Response({
                'success': False,
                'message': 'Customer ID is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        files = self.get_queryset().filter(customer=customer_id)
        serializer = CustomerFileListSerializer(files, many=True)

        stats = files.aggregate(
            total_files=Count('id'),
            total_size=Sum('file_size')
        )

        return Response({
            'success': True,
            'message': 'Customer files retrieved successfully',
            'data': serializer.data,
            'statistics': stats
        })

    @action(detail=True, methods=['patch'])
    def deactivate(self, request, pk=None):
        file_instance = self.get_object()
        file_instance.is_active = False
        file_instance.updated_by = request.user
        file_instance.save()
        
        return Response({
            'success': True,
            'message': 'Customer file deactivated successfully'
        })
    
    @action(detail=True, methods=['patch'])
    def activate(self, request, pk=None):
        file_instance = self.get_object()
        file_instance.is_active = True
        file_instance.updated_by = request.user
        file_instance.save()
        
        return Response({
            'success': True,
            'message': 'Customer file activated successfully'
        })
