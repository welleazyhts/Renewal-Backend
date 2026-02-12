from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import ClosedCaseChatbot, ClosedCaseChatbotMessage, ClosedCaseChatbotAnalytics
from .services import ClosedCaseChatbotAnalyticsService

@shared_task
def cleanup_old_chatbot_sessions():
    cutoff_date = timezone.now() - timedelta(days=90)
    
    old_sessions = ClosedCaseChatbot.objects.filter(
        is_active=False,
        last_interaction__lt=cutoff_date
    )
    
    count = old_sessions.count()
    old_sessions.delete()
    
    return f"Cleaned up {count} old chatbot sessions"

@shared_task
def generate_daily_analytics():
    analytics_service = ClosedCaseChatbotAnalyticsService()
    today = timezone.now().date()
    
    active_sessions = ClosedCaseChatbot.objects.filter(is_active=True)
    
    analytics_created = 0
    
    for session in active_sessions:
        daily_interactions = session.messages.filter(
            timestamp__date=today
        ).count()
        
        if daily_interactions > 0:
            analytics_service.record_metric(
                session, 
                'daily_interactions', 
                daily_interactions, 
                today
            )
            analytics_created += 1
        
        total_interactions = session.messages.count()
        analytics_service.record_metric(
            session, 
            'total_interactions', 
            total_interactions, 
            today
        )
        analytics_created += 1
    
    return f"Generated {analytics_created} analytics records for {active_sessions.count()} sessions"


@shared_task
def send_chatbot_reminders():
    cutoff_date = timezone.now() - timedelta(days=7)
    
    inactive_sessions = ClosedCaseChatbot.objects.filter(
        is_active=True,
        last_interaction__lt=cutoff_date
    )
    
    reminders_sent = 0
    
    for session in inactive_sessions:
        print(f"Sending reminder to {session.customer_name} ({session.mobile_number})")
        reminders_sent += 1
    
    return f"Sent {reminders_sent} chatbot reminders"


@shared_task
def update_chatbot_interaction_counts():
    sessions = ClosedCaseChatbot.objects.all()
    updated_count = 0
    
    for session in sessions:
        message_count = session.messages.count()
        if session.interaction_count != message_count:
            session.interaction_count = message_count
            session.save()
            updated_count += 1
    
    return f"Updated interaction counts for {updated_count} sessions"


@shared_task
def generate_weekly_report():
    analytics_service = ClosedCaseChatbotAnalyticsService()
    
    category_stats = analytics_service.get_category_wise_stats()
    profile_stats = analytics_service.get_profile_type_stats()
    language_stats = analytics_service.get_language_wise_stats()
    
    daily_stats = analytics_service.get_daily_interaction_stats(days=7)
    
    report_data = {
        'category_stats': list(category_stats),
        'profile_stats': list(profile_stats),
        'language_stats': list(language_stats),
        'daily_stats': daily_stats,
        'generated_at': timezone.now().isoformat()
    }
    
    return report_data


@shared_task
def archive_old_messages():
    cutoff_date = timezone.now() - timedelta(days=365)
    
    old_messages = ClosedCaseChatbotMessage.objects.filter(
        timestamp__lt=cutoff_date
    )
    
    count = old_messages.count()
    old_messages.delete()
    
    return f"Archived {count} old messages"
