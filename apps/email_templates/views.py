from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Count, F
from django.utils import timezone
from datetime import timedelta

from .models import EmailTemplate, EmailTemplateTag, EmailTemplateVersion
from .serializers import (
    EmailTemplateSerializer, EmailTemplateCreateSerializer, EmailTemplateUpdateSerializer,
    EmailTemplateTagSerializer, EmailTemplateVersionSerializer,
    EmailTemplateRenderSerializer, EmailTemplateStatsSerializer
)

class EmailTemplateTagViewSet(viewsets.ModelViewSet):    
    queryset = EmailTemplateTag.objects.filter(is_deleted=False)
    serializer_class = EmailTemplateTagSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset.order_by('name')
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)
    
    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.deleted_at = timezone.now()
        instance.deleted_by = self.request.user
        instance.save(update_fields=['is_deleted', 'deleted_at', 'deleted_by'])
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        tag = self.get_object()
        tag.is_active = True
        tag.updated_by = request.user
        tag.save(update_fields=['is_active', 'updated_by'])
        
        return Response({'message': 'Tag activated successfully'})
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        tag = self.get_object()
        tag.is_active = False
        tag.updated_by = request.user
        tag.save(update_fields=['is_active', 'updated_by'])
        
        return Response({'message': 'Tag deactivated successfully'})


class EmailTemplateViewSet(viewsets.ModelViewSet):
    
    queryset = EmailTemplate.objects.filter(is_deleted=False)
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return EmailTemplateCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return EmailTemplateUpdateSerializer
        return EmailTemplateSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        tag_names = self.request.query_params.getlist('tags')
        if tag_names:
            queryset = queryset.filter(tags__name__in=tag_names).distinct()
        
        template_type = self.request.query_params.get('template_type')
        if template_type:
            queryset = queryset.filter(template_type=template_type)
        
        is_public = self.request.query_params.get('is_public')
        if is_public is not None:
            queryset = queryset.filter(is_public=is_public.lower() == 'true')
        
        created_by = self.request.query_params.get('created_by')
        if created_by:
            queryset = queryset.filter(created_by_id=created_by)
        
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(subject__icontains=search)
            )
        
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)
    
    def perform_destroy(self, instance):
        instance.soft_delete()
        instance.deleted_by = self.request.user
        instance.save(update_fields=['deleted_by'])
    
    @action(detail=True, methods=['post'])
    def render(self, request, pk=None):
        template = self.get_object()
        serializer = EmailTemplateRenderSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        context = serializer.validated_data.get('context', {})
        rendered_content = template.render_content(context)
        
        return Response(rendered_content)
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        template = self.get_object()
        template.status = 'active'
        template.updated_by = request.user
        template.save(update_fields=['status', 'updated_by'])
        
        return Response({'message': 'Template activated successfully'})
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        template = self.get_object()
        template.status = 'inactive'
        template.updated_by = request.user
        template.save(update_fields=['status', 'updated_by'])
        
        return Response({'message': 'Template deactivated successfully'})
    
    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        template = self.get_object()
        template.status = 'archived'
        template.updated_by = request.user
        template.save(update_fields=['status', 'updated_by'])
        
        return Response({'message': 'Template archived successfully'})
    
    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        original_template = self.get_object()
        
        new_template = EmailTemplate.objects.create(
            name=f"{original_template.name} (Copy)",
            subject=original_template.subject,
            description=original_template.description,
            html_content=original_template.html_content,
            text_content=original_template.text_content,
            template_type=original_template.template_type,
            variables=original_template.variables,
            status='draft',
            is_public=original_template.is_public,
            created_by=request.user
        )
        
        new_template.tags.set(original_template.tags.all())
        
        EmailTemplateVersion.objects.create(
            template=new_template,
            name=new_template.name,
            subject=new_template.subject,
            html_content=new_template.html_content,
            text_content=new_template.text_content,
            template_type=new_template.template_type,
            variables=new_template.variables,
            change_summary="Duplicated from original template",
            is_current=True,
            created_by=request.user
        )
        
        serializer = self.get_serializer(new_template)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def increment_usage(self, request, pk=None):
        template = self.get_object()
        template.increment_usage()
        
        return Response({
            'message': 'Usage count incremented',
            'usage_count': template.usage_count,
            'last_used': template.last_used
        })
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        queryset = self.get_queryset()
        
        total_templates = queryset.count()
        active_templates = queryset.filter(status='active').count()
        draft_templates = queryset.filter(status='draft').count()
        archived_templates = queryset.filter(status='archived').count()
        
        most_used = queryset.order_by('-usage_count')[:5]
        
        recent_templates = queryset.order_by('-created_at')[:5]
        
        type_stats = queryset.values('template_type').annotate(
            count=Count('id')
        ).order_by('-count')
        
        return Response({
            'total_templates': total_templates,
            'active_templates': active_templates,
            'draft_templates': draft_templates,
            'archived_templates': archived_templates,
            'most_used_templates': EmailTemplateSerializer(most_used, many=True).data,
            'recent_templates': EmailTemplateSerializer(recent_templates, many=True).data,
            'category_distribution': [],
            'type_distribution': list(type_stats)
        })
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        queryset = self.get_queryset()
        
        query = request.query_params.get('q', '')
        tag_names = request.query_params.getlist('tags')
        template_type = request.query_params.get('template_type')
        status_filter = request.query_params.get('status')
        created_after = request.query_params.get('created_after')
        created_before = request.query_params.get('created_before')
        
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) |
                Q(subject__icontains=query) |
                Q(description__icontains=query) |
                Q(html_content__icontains=query) |
                Q(text_content__icontains=query)
            )
        
        if tag_names:
            queryset = queryset.filter(tags__name__in=tag_names).distinct()
        
        if template_type:
            queryset = queryset.filter(template_type=template_type)
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        if created_after:
            queryset = queryset.filter(created_at__gte=created_after)
        
        if created_before:
            queryset = queryset.filter(created_at__lte=created_before)
        
        order_by = request.query_params.get('order_by', '-created_at')
        queryset = queryset.order_by(order_by)
        
        page_size = int(request.query_params.get('page_size', 20))
        page = int(request.query_params.get('page', 1))
        start = (page - 1) * page_size
        end = start + page_size
        
        templates = queryset[start:end]
        total_count = queryset.count()
        
        serializer = self.get_serializer(templates, many=True)
        
        return Response({
            'results': serializer.data,
            'total_count': total_count,
            'page': page,
            'page_size': page_size,
            'total_pages': (total_count + page_size - 1) // page_size
        })


class EmailTemplateVersionViewSet(viewsets.ReadOnlyModelViewSet):    
    queryset = EmailTemplateVersion.objects.all()
    serializer_class = EmailTemplateVersionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        template_id = self.request.query_params.get('template_id')
        if template_id:
            queryset = queryset.filter(template_id=template_id)
        
        is_current = self.request.query_params.get('is_current')
        if is_current is not None:
            queryset = queryset.filter(is_current=is_current.lower() == 'true')
        
        return queryset.order_by('-version_number')
    
    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        version = self.get_object()
        template = version.template
        template.name = version.name
        template.subject = version.subject
        template.html_content = version.html_content
        template.text_content = version.text_content
        template.template_type = version.template_type
        template.variables = version.variables
        template.updated_by = request.user
        template.save()
        
        EmailTemplateVersion.objects.create(
            template=template,
            name=template.name,
            subject=template.subject,
            html_content=template.html_content,
            text_content=template.text_content,
            template_type=template.template_type,
            variables=template.variables,
            change_summary=f"Restored to version {version.version_number}",
            is_current=True,
            created_by=request.user
        )
        
        return Response({'message': f'Template restored to version {version.version_number}'})
