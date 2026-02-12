from django.db import models
from django.contrib.auth import get_user_model
from apps.core.models import BaseModel
from apps.policies.models import Policy

User = get_user_model()
class PolicyCondition(BaseModel):    
    policy = models.ForeignKey(
        Policy,
        on_delete=models.CASCADE,
        related_name='policy_conditions',
        help_text="Links condition to a specific policy"
    )
    
    description = models.TextField(
        help_text="The actual condition details"
    )
    
    class Meta:
        db_table = 'policy_conditions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['policy']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Condition for {self.policy.policy_number}"
    
    @property
    def policy_number(self):
        return self.policy.policy_number if self.policy else None
    
    @property
    def customer_name(self):
        return self.policy.customer.full_name if self.policy and self.policy.customer else None
