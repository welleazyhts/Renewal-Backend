from rest_framework import serializers
from django.db import transaction
from .models import (
    WhatsAppFlow, 
    FlowBlock, 
    WhatsAppMessageTemplate, 
    FlowTemplate,
    FlowAnalytics,
    AITemplate
)

class FlowBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = FlowBlock
        fields = ['id', 'block_id', 'block_type', 'configuration', 'connections']
class WhatsAppFlowSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    recipients = serializers.SerializerMethodField()
    delivery_rate = serializers.SerializerMethodField()
    last_run = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    
    class Meta:
        model = WhatsAppFlow
        fields = [
            'id', 'name', 'status', 'status_display', 
            'entry_point', 'recipients', 'delivery_rate', 
            'last_run', 'tags', 'created_at'
        ]

    def get_recipients(self, obj):
        if hasattr(obj, 'analytics'):
            return obj.analytics.total_runs
        return 0

    def get_delivery_rate(self, obj):
        if hasattr(obj, 'analytics') and obj.analytics.total_runs > 0:
            rate = (obj.analytics.completed_runs / obj.analytics.total_runs) * 100
            return f"{rate:.1f}%"
        return "0.0%"

    def get_last_run(self, obj):
        return obj.updated_at.strftime("%b %d, %Y, %I:%M %p")

    def get_tags(self, obj):
        tags = []
        
        if obj.entry_point == 'INBOUND':
            tags.append("Onboarding")
        elif obj.entry_point == 'SCHEDULED':
            tags.append("Renewal")
        elif obj.entry_point == 'POST_CAMPAIGN':
            tags.append("Marketing")
        else:
            tags.append("General")
            
        tags.append("All Customers")
        return tags


class WhatsAppFlowDetailSerializer(WhatsAppFlowSerializer):
    blocks = FlowBlockSerializer(many=True, required=False)
    
    class Meta:
        model = WhatsAppFlow
        fields = WhatsAppFlowSerializer.Meta.fields + ['blocks', 'canvas_layout']

    @transaction.atomic
    def create(self, validated_data):
        blocks_data = validated_data.pop('blocks', [])
        user = self.context['request'].user if self.context.get('request') else None
        
        flow = WhatsAppFlow.objects.create(**validated_data, created_by=user)
        
        block_objects = [FlowBlock(flow=flow, **data) for data in blocks_data]
        FlowBlock.objects.bulk_create(block_objects)
        
        return flow

    @transaction.atomic
    def update(self, instance, validated_data):
        blocks_data = validated_data.pop('blocks', None)
        
        instance = super().update(instance, validated_data)

        if blocks_data is not None:
            existing_blocks = {block.block_id: block for block in instance.blocks.all()}
            incoming_block_ids = set()
            new_blocks = []

            for block_data in blocks_data:
                block_id = block_data.get('block_id')
                incoming_block_ids.add(block_id)

                if block_id in existing_blocks:
                    block = existing_blocks[block_id]
                    for attr, value in block_data.items():
                        setattr(block, attr, value)
                    block.save()
                else:
                    new_blocks.append(FlowBlock(flow=instance, **block_data))

            if new_blocks:
                FlowBlock.objects.bulk_create(new_blocks)

            ids_to_delete = existing_blocks.keys() - incoming_block_ids
            if ids_to_delete:
                FlowBlock.objects.filter(flow=instance, block_id__in=ids_to_delete).delete()

        return instance
class WhatsAppMessageTemplateSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = WhatsAppMessageTemplate
        fields = ['id', 'name', 'status', 'status_display', 'content_json', 'created_at']
        read_only_fields = ['id', 'status_display', 'created_at']

class FlowTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = FlowTemplate
        fields = ['id', 'name', 'description', 'template_flow_json', 'category']
        read_only_fields = ['id']
class AITemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AITemplate
        fields = ['id', 'name', 'description', 'category', 'prompt_used', 'generated_content', 'status', 'created_at']
        read_only_fields = ['id', 'created_at']
