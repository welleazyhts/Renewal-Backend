from django.core.management.base import BaseCommand
from apps.policies.models import Policy, PolicyType
from datetime import date, timedelta
import json


class Command(BaseCommand):
    help = 'Test renewal reminder functionality through API simulation'

    def handle(self, *args, **options):
        self.stdout.write("🧪 Testing Renewal Reminder API Functionality")
        self.stdout.write("=" * 60)
        
        total_policies = Policy.objects.count()
        if total_policies == 0:
            self.stdout.write(self.style.WARNING("⚠️ No policies found. Please add some policies first."))
            return
        
        self.stdout.write(f"📊 Found {total_policies} policies in database")
        
        self.test_renewal_dashboard()
        
        self.test_renewal_urgency()
        
        self.test_reminder_scenarios()
        
        self.show_api_examples()
        
        self.stdout.write(self.style.SUCCESS("\n✅ Renewal reminder API testing completed!"))

    def test_renewal_dashboard(self):
        """Test the renewal dashboard functionality"""
        self.stdout.write("\n📊 Testing Renewal Dashboard:")
        self.stdout.write("-" * 40)
        
        today = date.today()
        
        total_policies = Policy.objects.count()
        active_policies = Policy.objects.filter(status='active').count()
        expired_policies = Policy.objects.filter(status='expired').count()
        
        overdue_count = 0
        due_today_count = 0
        due_this_week_count = 0
        due_this_month_count = 0
        
        for policy in Policy.objects.filter(renewal_date__isnull=False):
            if policy.renewal_date < today:
                overdue_count += 1
            elif policy.renewal_date == today:
                due_today_count += 1
            elif policy.renewal_date <= today + timedelta(days=7):
                due_this_week_count += 1
            elif policy.renewal_date <= today + timedelta(days=30):
                due_this_month_count += 1
        
        dashboard_data = {
            'total_policies': total_policies,
            'active_policies': active_policies,
            'expired_policies': expired_policies,
            'renewal_urgency': {
                'overdue': overdue_count,
                'due_today': due_today_count,
                'due_this_week': due_this_week_count,
                'due_this_month': due_this_month_count,
            }
        }
        
        self.stdout.write(json.dumps(dashboard_data, indent=2))

    def test_renewal_urgency(self):
        self.stdout.write("\n🚨 Testing Renewal Urgency Categories:")
        self.stdout.write("-" * 45)
        
        today = date.today()
        policies = Policy.objects.filter(renewal_date__isnull=False)[:5]
        
        for policy in policies:
            urgency = self.get_urgency_category(policy.renewal_date, today)
            days_diff = (policy.renewal_date - today).days
            
            self.stdout.write(
                f"📋 {policy.policy_number}: "
                f"Renewal: {policy.renewal_date} | "
                f"Days: {days_diff:+d} | "
                f"Urgency: {urgency}"
            )

    def get_urgency_category(self, renewal_date, today):
        """Get urgency category for a renewal date"""
        if renewal_date < today:
            return "🔴 OVERDUE"
        elif renewal_date == today:
            return "🟠 DUE TODAY"
        elif renewal_date <= today + timedelta(days=7):
            return "🟡 DUE THIS WEEK"
        elif renewal_date <= today + timedelta(days=30):
            return "🟢 DUE THIS MONTH"
        else:
            return "⚪ FUTURE"

    def test_reminder_scenarios(self):
        self.stdout.write("\n🎯 Testing Reminder Scenarios:")
        self.stdout.write("-" * 35)
        
        sample_policy = Policy.objects.filter(end_date__isnull=False).first()
        if not sample_policy:
            self.stdout.write("⚠️ No policies with end dates found")
            return
        
        self.stdout.write(f"📋 Sample Policy: {sample_policy.policy_number}")
        self.stdout.write(f"📅 End Date: {sample_policy.end_date}")
        self.stdout.write()
        
        reminder_options = [15, 30, 45, 60]
        today = date.today()
        
        for days in reminder_options:
            renewal_date = sample_policy.end_date - timedelta(days=days)
            days_until_renewal = (renewal_date - today).days
            urgency = self.get_urgency_category(renewal_date, today)
            
            self.stdout.write(
                f"🔧 {days:2d}-day reminder: "
                f"Renewal: {renewal_date} | "
                f"Days until: {days_until_renewal:+3d} | "
                f"{urgency}"
            )

    def show_api_examples(self):
        self.stdout.write("\n🚀 API Endpoint Examples:")
        self.stdout.write("-" * 30)
        
        sample_policies = Policy.objects.all()[:3]
        policy_ids = [p.id for p in sample_policies]
        
        examples = [
            {
                'title': '1. Get Renewal Dashboard',
                'method': 'GET',
                'url': '/api/policies/renewal_dashboard/',
                'description': 'Get comprehensive renewal statistics'
            },
            {
                'title': '2. Configure All Motor Policies to 15-day Reminders',
                'method': 'POST',
                'url': '/api/policies/configure_renewal_reminders/',
                'body': {
                    'reminder_days': 15,
                    'category': 'Motor'
                },
                'description': 'Set all Motor category policies to 15-day reminders'
            },
            {
                'title': '3. Configure Specific Policies to 30-day Reminders',
                'method': 'POST',
                'url': '/api/policies/configure_renewal_reminders/',
                'body': {
                    'reminder_days': 30,
                    'policy_ids': policy_ids
                },
                'description': f'Set specific policies {policy_ids} to 30-day reminders'
            },
            {
                'title': '4. Get Overdue Renewals',
                'method': 'GET',
                'url': '/api/policies/renewal_urgency_list/?urgency=overdue',
                'description': 'Get all policies with overdue renewals'
            },
            {
                'title': '5. Update Single Policy Reminder',
                'method': 'POST',
                'url': f'/api/policies/{policy_ids[0] if policy_ids else 1}/update_renewal_reminder/',
                'body': {
                    'reminder_days': 45
                },
                'description': 'Update a specific policy to 45-day reminders'
            }
        ]
        
        for example in examples:
            self.stdout.write(f"\n{example['title']}:")
            self.stdout.write(f"   {example['method']} {example['url']}")
            if 'body' in example:
                self.stdout.write(f"   Body: {json.dumps(example['body'], indent=8)}")
            self.stdout.write(f"   📝 {example['description']}")
        
        self.stdout.write("\n💡 Postman Collection:")
        self.stdout.write("   Import these endpoints into Postman for testing")
        self.stdout.write("   Base URL: http://localhost:8000")
        self.stdout.write("   Add Authorization header with your token")
        
        self.stdout.write("\n🛠️ Management Commands:")
        self.stdout.write("   python manage.py configure_renewal_reminders --reminder-days 30")
        self.stdout.write("   python manage.py configure_renewal_reminders --reminder-days 15 --category Motor")
        self.stdout.write("   python manage.py test_renewal_logic")
