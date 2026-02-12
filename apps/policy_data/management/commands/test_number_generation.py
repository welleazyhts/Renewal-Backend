from django.core.management.base import BaseCommand
from apps.policy_data.utils import generate_policy_number, generate_case_number
from apps.policies.models import Policy
from apps.renewals.models import RenewalCase
class Command(BaseCommand):
    help = 'Test policy and case number generation'

    def handle(self, *args, **options):
        self.stdout.write("🧪 Testing Number Generation")
        self.stdout.write("=" * 50)
        
        self.stdout.write("\n📋 Testing Policy Number Generation...")
        
        existing_policies = Policy.objects.filter(
            policy_number__startswith='POL-'
        ).values_list('policy_number', flat=True).order_by('policy_number')
        
        self.stdout.write(f"   Existing policies: {list(existing_policies)}")
        
        next_policy = generate_policy_number()
        self.stdout.write(f"   Next policy number: {next_policy}")
        
        self.stdout.write("\n📋 Testing Case Number Generation...")
        
        existing_cases = RenewalCase.objects.filter(
            case_number__startswith='CASE-'
        ).values_list('case_number', flat=True).order_by('case_number')
        
        self.stdout.write(f"   Existing cases: {list(existing_cases)}")
        
        next_case = generate_case_number()
        self.stdout.write(f"   Next case number: {next_case}")
        
        self.stdout.write(self.style.SUCCESS("\n🎉 Number generation testing completed!"))
