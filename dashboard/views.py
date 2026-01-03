from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from reports.models import Report
from django.contrib.auth import get_user_model

User = get_user_model()

@swagger_auto_schema(
    method='get',
    operation_description="Get comprehensive dashboard metrics including reports statistics, growth metrics, account numbers, service locations, and time-based analytics.",
    security=[{'Token': []}],
    responses={
        200: openapi.Response(
            description="Dashboard metrics",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'total_reports': openapi.Schema(type=openapi.TYPE_INTEGER, description='Total number of reports'),
                    'reports_change': openapi.Schema(type=openapi.TYPE_NUMBER, description='Percentage change in reports'),
                    'active_users': openapi.Schema(type=openapi.TYPE_INTEGER, description='Number of active users (always 1 for the current user)'),
                    'users_change': openapi.Schema(type=openapi.TYPE_NUMBER, description='Percentage change in users (always 0 for user-specific data)'),
                    'monthly_growth': openapi.Schema(type=openapi.TYPE_NUMBER, description='Monthly growth percentage'),
                    'system_activity': openapi.Schema(type=openapi.TYPE_NUMBER, description='System activity percentage'),
                    'unique_account_numbers': openapi.Schema(type=openapi.TYPE_INTEGER, description='Number of unique account numbers'),
                    'reports_today': openapi.Schema(type=openapi.TYPE_INTEGER, description='Number of reports created today'),
                    'reports_this_week': openapi.Schema(type=openapi.TYPE_INTEGER, description='Number of reports created this week'),
                    'reports_this_year': openapi.Schema(type=openapi.TYPE_INTEGER, description='Number of reports created this year'),
                    'active_reports': openapi.Schema(type=openapi.TYPE_INTEGER, description='Number of active reports'),
                    'unique_service_locations': openapi.Schema(type=openapi.TYPE_INTEGER, description='Number of unique service locations'),
                    'reports_with_account': openapi.Schema(type=openapi.TYPE_INTEGER, description='Number of reports with account numbers'),
                    'reports_without_account': openapi.Schema(type=openapi.TYPE_INTEGER, description='Number of reports without account numbers'),
                    'latest_report_date': openapi.Schema(type=openapi.TYPE_STRING, description='ISO format date of the most recent report'),
                    'oldest_report_date': openapi.Schema(type=openapi.TYPE_STRING, description='ISO format date of the oldest report'),
                    'avg_reports_per_month': openapi.Schema(type=openapi.TYPE_NUMBER, description='Average number of reports per month this year'),
                    'reports_with_foundation_year': openapi.Schema(type=openapi.TYPE_INTEGER, description='Number of reports with foundation year data')
                }
            )
        ),
        401: openapi.Response(description="Unauthorized - Authentication required")
    },
    tags=['Dashboard']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_metrics(request):
    """Get dashboard metrics"""
    user = request.user
    
    # Total Reports
    total_reports = Report.objects.filter(created_by=user).count()
    last_month_reports = Report.objects.filter(
        created_by=user,
        created_at__gte=timezone.now() - timedelta(days=30)
    ).count()
    reports_change = ((total_reports - last_month_reports) / last_month_reports * 100) if last_month_reports > 0 else 0
    
    # Active Users (always 1 for the current user)
    active_users = 1
    users_change = 0
    
    # Monthly Growth (based on reports)
    current_month_reports = Report.objects.filter(
        created_by=user,
        created_at__year=timezone.now().year,
        created_at__month=timezone.now().month
    ).count()
    last_month_reports_count = Report.objects.filter(
        created_by=user,
        created_at__year=(timezone.now() - timedelta(days=30)).year,
        created_at__month=(timezone.now() - timedelta(days=30)).month
    ).count()
    monthly_growth = ((current_month_reports - last_month_reports_count) / last_month_reports_count * 100) if last_month_reports_count > 0 else 0
    
    # System Activity (based on recent report activity)
    recent_activity = Report.objects.filter(
        created_by=user,
        updated_at__gte=timezone.now() - timedelta(days=7)
    ).count()
    total_activity = Report.objects.filter(created_by=user).count()
    system_activity = (recent_activity / total_activity * 100) if total_activity > 0 else 0
    
    # Unique Account Numbers
    unique_account_numbers = Report.objects.filter(
        created_by=user,
        account_number__isnull=False
    ).exclude(account_number='').values('account_number').distinct().count()
    
    # Reports created today
    reports_today = Report.objects.filter(
        created_by=user,
        created_at__date=timezone.now().date()
    ).count()
    
    # Reports created this week
    week_start = timezone.now() - timedelta(days=timezone.now().weekday())
    reports_this_week = Report.objects.filter(
        created_by=user,
        created_at__gte=week_start
    ).count()
    
    # Reports created this year
    reports_this_year = Report.objects.filter(
        created_by=user,
        created_at__year=timezone.now().year
    ).count()
    
    # Active reports count
    active_reports = Report.objects.filter(
        created_by=user,
        is_active=True
    ).count()
    
    # Unique service locations
    unique_service_locations = Report.objects.filter(
        created_by=user,
        service_location__isnull=False
    ).exclude(service_location='').values('service_location').distinct().count()
    
    # Reports with account numbers vs without
    reports_with_account = Report.objects.filter(
        created_by=user,
        account_number__isnull=False
    ).exclude(account_number='').count()
    reports_without_account = total_reports - reports_with_account
    
    # Most recent and oldest report dates
    latest_report = Report.objects.filter(created_by=user).order_by('-created_at').first()
    oldest_report = Report.objects.filter(created_by=user).order_by('created_at').first()
    
    latest_report_date = latest_report.created_at.isoformat() if latest_report else None
    oldest_report_date = oldest_report.created_at.isoformat() if oldest_report else None
    
    # Average reports per month (this year)
    months_elapsed = timezone.now().month
    avg_reports_per_month = round(reports_this_year / months_elapsed, 1) if months_elapsed > 0 else 0
    
    # Reports with foundation year data
    reports_with_foundation_year = Report.objects.filter(
        created_by=user,
        foundation_year__isnull=False
    ).count()
    
    return Response({
        'total_reports': total_reports,
        'reports_change': round(reports_change, 1),
        'active_users': active_users,
        'users_change': round(users_change, 1),
        'monthly_growth': round(monthly_growth, 1),
        'system_activity': round(system_activity, 1),
        'unique_account_numbers': unique_account_numbers,
        'reports_today': reports_today,
        'reports_this_week': reports_this_week,
        'reports_this_year': reports_this_year,
        'active_reports': active_reports,
        'unique_service_locations': unique_service_locations,
        'reports_with_account': reports_with_account,
        'reports_without_account': reports_without_account,
        'latest_report_date': latest_report_date,
        'oldest_report_date': oldest_report_date,
        'avg_reports_per_month': avg_reports_per_month,
        'reports_with_foundation_year': reports_with_foundation_year,
    })
