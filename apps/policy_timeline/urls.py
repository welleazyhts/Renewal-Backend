from django.urls import path
from . import views

app_name = 'policy_timeline'

urlpatterns = [
    path('', views.PolicyTimelineListCreateView.as_view(), name='timeline-list-create'),
    path('<int:id>/', views.PolicyTimelineDetailView.as_view(), name='timeline-detail'),
    
    path('policy/<int:policy_id>/', views.policy_timeline_by_policy, name='timeline-by-policy'),
    
    path('customer/<int:customer_id>/', views.customer_policy_timeline, name='customer-timeline'),
    
    path('dashboard/<int:customer_id>/', views.policy_timeline_dashboard, name='timeline-dashboard'),
    path('complete-view/<int:customer_id>/', views.policy_timeline_complete_view, name='timeline-complete-view'),
    path('complete-api/<int:customer_id>/', views.policy_timeline_complete_api, name='timeline-complete-api'),
    
    path('search/', views.search_timeline_events, name='search-timeline-events'),
    path('statistics/', views.timeline_statistics, name='timeline-statistics'),
    
    path('bulk-create/', views.create_timeline_event_bulk, name='bulk-create-events'),
    
    path('event-types/', views.timeline_event_types, name='event-types'),
    path('create-event/', views.create_timeline_event, name='create-event'),
    
    path('data-check/<str:policy_type_slug>/<int:customer_id>/', views.policy_data_check_generic, name='data-check-generic'),
]
