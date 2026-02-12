from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from .models import OtherInsurancePolicy
from .serializers import (
    OtherInsurancePolicySerializer,
    OtherInsurancePolicyCreateSerializer,
    OtherInsurancePolicyListSerializer,
)

class OtherInsurancePolicyViewSet(viewsets.ModelViewSet):
    queryset = OtherInsurancePolicy.objects.filter(is_deleted=False)

    def get_serializer_class(self):
        if self.action == 'store':
            return OtherInsurancePolicyCreateSerializer
        elif self.action == 'list':
            return OtherInsurancePolicyListSerializer
        return OtherInsurancePolicySerializer

    def get_queryset(self):
        queryset = OtherInsurancePolicy.objects.filter(is_deleted=False)

        if self.action == 'list':
            customer_id = self.request.query_params.get('customer_id')
            if customer_id:
                queryset = queryset.filter(customer_id=customer_id)

            policy_type_id = self.request.query_params.get('policy_type_id')
            if policy_type_id:
                queryset = queryset.filter(policy_type_id=policy_type_id)

            insurance_company = self.request.query_params.get('insurance_company')
            if insurance_company:
                queryset = queryset.filter(insurance_company__icontains=insurance_company)

            policy_status = self.request.query_params.get('policy_status')
            if policy_status:
                queryset = queryset.filter(policy_status=policy_status)

            switching_potential = self.request.query_params.get('switching_potential')
            if switching_potential:
                queryset = queryset.filter(switching_potential=switching_potential)

            search = self.request.query_params.get('search')
            if search:
                queryset = queryset.filter(
                    Q(policy_number__icontains=search) |
                    Q(insurance_company__icontains=search) |
                    Q(agent_name__icontains=search) |
                    Q(customer__first_name__icontains=search) |
                    Q(customer__last_name__icontains=search) |
                    Q(customer__customer_code__icontains=search) |
                    Q(policy_type__name__icontains=search)
                )

        return queryset.select_related('customer', 'policy_type').order_by('-created_at')

    @action(detail=False, methods=['post'])
    def store(self, request):
        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                policy = serializer.save(created_by=request.user)

                response_serializer = OtherInsurancePolicySerializer(policy)
                return Response({
                    'success': True,
                    'message': 'Other insurance policy stored successfully',
                    'data': response_serializer.data
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'success': False,
                    'message': 'Validation failed',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                'success': False,
                'message': f'Error storing other insurance policy: {str(e)}',
                'errors': {}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()

            serializer = self.get_serializer(queryset, many=True)

            return Response({
                'success': True,
                'message': 'Other insurance policies retrieved successfully',
                'count': queryset.count(),
                'data': serializer.data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'success': False,
                'message': f'Error retrieving other insurance policies: {str(e)}',
                'data': []
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)