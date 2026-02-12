from django.db import models
from django.conf import settings

class BaseHierarchyNode(models.Model):
    unit_name = models.CharField(max_length=255, verbose_name="Unit Name")
    description = models.TextField(blank=True, null=True)
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        db_column='manager_id',
        related_name='%(class)s_managed' 
    )
    
    budget = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    target_cases = models.IntegerField(default=0)
    status = models.CharField(max_length=20, default='Active')

    class Meta:
        abstract = True

class Region(BaseHierarchyNode):
    class Meta:
        db_table = 'hierarchy_region'

class State(BaseHierarchyNode):
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='states', db_column='region_id')
    class Meta:
        db_table = 'hierarchy_state'
class Branch(BaseHierarchyNode):
    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name='branches', db_column='state_id')
    class Meta:
        db_table = 'hierarchy_branch'

class Department(BaseHierarchyNode):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='departments', db_column='branch_id')
    class Meta:
        db_table = 'hierarchy_department'
class Team(BaseHierarchyNode):
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='teams', db_column='department_id')
    class Meta:
        db_table = 'hierarchy_team'