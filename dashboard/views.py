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
    operation_description="Get comprehensive dashboard metrics organized into report and account groups.",
    security=[{'Token': []}],
    responses={
        200: openapi.Response(
            description="Dashboard metrics",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'report': openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        description='Report-related metrics',
                        properties={
                            'total': openapi.Schema(type=openapi.TYPE_INTEGER, description='Total number of reports'),
                            'change': openapi.Schema(type=openapi.TYPE_NUMBER, description='Percentage change in reports'),
                            'monthly_growth': openapi.Schema(type=openapi.TYPE_NUMBER, description='Monthly growth percentage'),
                            'system_activity': openapi.Schema(type=openapi.TYPE_NUMBER, description='System activity percentage'),
                            'today': openapi.Schema(type=openapi.TYPE_INTEGER, description='Number of reports created today'),
                            'this_week': openapi.Schema(type=openapi.TYPE_INTEGER, description='Number of reports created this week'),
                            'this_year': openapi.Schema(type=openapi.TYPE_INTEGER, description='Number of reports created this year'),
                            'active': openapi.Schema(type=openapi.TYPE_INTEGER, description='Number of active reports'),
                            'with_account': openapi.Schema(type=openapi.TYPE_INTEGER, description='Number of reports with account numbers'),
                            'without_account': openapi.Schema(type=openapi.TYPE_INTEGER, description='Number of reports without account numbers'),
                            'with_foundation_year': openapi.Schema(type=openapi.TYPE_INTEGER, description='Number of reports with foundation year data'),
                            'unique_service_locations': openapi.Schema(type=openapi.TYPE_INTEGER, description='Number of unique service locations'),
                            'latest_date': openapi.Schema(type=openapi.TYPE_STRING, description='ISO format date of the most recent report'),
                            'oldest_date': openapi.Schema(type=openapi.TYPE_STRING, description='ISO format date of the oldest report'),
                            'avg_per_month': openapi.Schema(type=openapi.TYPE_NUMBER, description='Average number of reports per month this year'),
                        }
                    ),
                    'account': openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        description='Account-related metrics',
                        properties={
                            'unique_count': openapi.Schema(type=openapi.TYPE_INTEGER, description='Total number of unique account numbers'),
                            'with_account': openapi.Schema(type=openapi.TYPE_INTEGER, description='Number of reports with account numbers'),
                            'without_account': openapi.Schema(type=openapi.TYPE_INTEGER, description='Number of reports without account numbers'),
                            'today': openapi.Schema(type=openapi.TYPE_INTEGER, description='Number of unique accounts created today'),
                            'this_week': openapi.Schema(type=openapi.TYPE_INTEGER, description='Number of unique accounts created this week'),
                            'this_year': openapi.Schema(type=openapi.TYPE_INTEGER, description='Number of unique accounts created this year'),
                            'growth': openapi.Schema(type=openapi.TYPE_NUMBER, description='Account growth percentage (this month vs last month)'),
                            'updated_recently': openapi.Schema(type=openapi.TYPE_INTEGER, description='Number of accounts updated in the last 7 days'),
                            'completeness': openapi.Schema(type=openapi.TYPE_NUMBER, description='Percentage of accounts with complete data (account number, service location, credit limit)'),
                            'with_credit_limit': openapi.Schema(type=openapi.TYPE_INTEGER, description='Number of unique accounts with credit limit data'),
                            'with_biometric': openapi.Schema(type=openapi.TYPE_INTEGER, description='Number of unique accounts with biometric data'),
                            'with_monthly_bill': openapi.Schema(type=openapi.TYPE_INTEGER, description='Number of unique accounts with monthly bill reports'),
                            'with_annual_bill': openapi.Schema(type=openapi.TYPE_INTEGER, description='Number of unique accounts with annual bill reports'),
                            'with_service_recipient': openapi.Schema(type=openapi.TYPE_INTEGER, description='Number of unique accounts with service recipient data'),
                            'with_monthly_service': openapi.Schema(type=openapi.TYPE_INTEGER, description='Number of unique accounts with monthly service reports'),
                            'with_annual_service': openapi.Schema(type=openapi.TYPE_INTEGER, description='Number of unique accounts with annual service reports'),
                            'with_foundation_year': openapi.Schema(type=openapi.TYPE_INTEGER, description='Number of unique accounts with foundation year data'),
                            'with_complete_data': openapi.Schema(type=openapi.TYPE_INTEGER, description='Number of unique accounts with complete data (account, location, credit limit)'),
                        }
                    ),
                    'users': openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        description='User-related metrics',
                        properties={
                            'active': openapi.Schema(type=openapi.TYPE_INTEGER, description='Number of active users (always 1 for the current user)'),
                            'change': openapi.Schema(type=openapi.TYPE_NUMBER, description='Percentage change in user activity (based on reports created)'),
                            'growth': openapi.Schema(type=openapi.TYPE_NUMBER, description='User growth percentage (based on account creation activity)'),
                        }
                    ),
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
    
    # User activity growth (based on reports created)
    current_month_user_activity = Report.objects.filter(
        created_by=user,
        created_at__year=timezone.now().year,
        created_at__month=timezone.now().month
    ).count()
    
    last_month_user_activity = Report.objects.filter(
        created_by=user,
        created_at__year=(timezone.now() - timedelta(days=30)).year,
        created_at__month=(timezone.now() - timedelta(days=30)).month
    ).count()
    
    users_change = ((current_month_user_activity - last_month_user_activity) / last_month_user_activity * 100) if last_month_user_activity > 0 else 0
    
    # User growth (based on account creation activity)
    current_month_user_accounts = Report.objects.filter(
        created_by=user,
        account_number__isnull=False,
        created_at__year=timezone.now().year,
        created_at__month=timezone.now().month
    ).exclude(account_number='').values('account_number').distinct().count()
    
    last_month_user_accounts = Report.objects.filter(
        created_by=user,
        account_number__isnull=False,
        created_at__year=(timezone.now() - timedelta(days=30)).year,
        created_at__month=(timezone.now() - timedelta(days=30)).month
    ).exclude(account_number='').values('account_number').distinct().count()
    
    user_growth = ((current_month_user_accounts - last_month_user_accounts) / last_month_user_accounts * 100) if last_month_user_accounts > 0 else 0
    
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
    
    # Account-related detailed metrics
    user_reports = Report.objects.filter(created_by=user)
    
    # Accounts created today
    accounts_today = user_reports.filter(
        account_number__isnull=False
    ).exclude(account_number='').filter(
        created_at__date=timezone.now().date()
    ).values('account_number').distinct().count()
    
    # Accounts created this week
    accounts_this_week = user_reports.filter(
        account_number__isnull=False
    ).exclude(account_number='').filter(
        created_at__gte=week_start
    ).values('account_number').distinct().count()
    
    # Accounts created this year
    accounts_this_year = user_reports.filter(
        account_number__isnull=False
    ).exclude(account_number='').filter(
        created_at__year=timezone.now().year
    ).values('account_number').distinct().count()
    
    # Accounts with credit limits
    accounts_with_credit_limit = user_reports.filter(
        account_number__isnull=False,
        credit_limit__isnull=False
    ).exclude(account_number='', credit_limit='').values('account_number').distinct().count()
    
    # Accounts with biometric data
    accounts_with_biometric = user_reports.filter(
        account_number__isnull=False,
        user_biometric__isnull=False
    ).exclude(account_number='', user_biometric='').values('account_number').distinct().count()
    
    # Accounts with monthly bill reports
    accounts_with_monthly_bill = user_reports.filter(
        account_number__isnull=False,
        monthly_bill_report__isnull=False
    ).exclude(account_number='', monthly_bill_report='').values('account_number').distinct().count()
    
    # Accounts with annual bill reports
    accounts_with_annual_bill = user_reports.filter(
        account_number__isnull=False,
        annual_bill_report__isnull=False
    ).exclude(account_number='', annual_bill_report='').values('account_number').distinct().count()
    
    # Accounts with service recipients
    accounts_with_service_recipient = user_reports.filter(
        account_number__isnull=False,
        service_recipient_at_branch__isnull=False
    ).exclude(account_number='', service_recipient_at_branch='').values('account_number').distinct().count()
    
    # Accounts with monthly service reports
    accounts_with_monthly_service = user_reports.filter(
        account_number__isnull=False,
        monthly_service_reports__isnull=False
    ).exclude(account_number='', monthly_service_reports='').values('account_number').distinct().count()
    
    # Accounts with annual service reports
    accounts_with_annual_service = user_reports.filter(
        account_number__isnull=False,
        annual_service_reports__isnull=False
    ).exclude(account_number='', annual_service_reports='').values('account_number').distinct().count()
    
    # Accounts with foundation year
    accounts_with_foundation_year = user_reports.filter(
        account_number__isnull=False,
        foundation_year__isnull=False
    ).exclude(account_number='').values('account_number').distinct().count()
    
    # Account growth (new accounts this month vs last month)
    current_month_accounts = user_reports.filter(
        account_number__isnull=False,
        created_at__year=timezone.now().year,
        created_at__month=timezone.now().month
    ).exclude(account_number='').values('account_number').distinct().count()
    
    last_month_accounts = user_reports.filter(
        account_number__isnull=False,
        created_at__year=(timezone.now() - timedelta(days=30)).year,
        created_at__month=(timezone.now() - timedelta(days=30)).month
    ).exclude(account_number='').values('account_number').distinct().count()
    
    account_growth = ((current_month_accounts - last_month_accounts) / last_month_accounts * 100) if last_month_accounts > 0 else 0
    
    # Accounts updated recently (last 7 days)
    accounts_updated_recently = user_reports.filter(
        account_number__isnull=False,
        updated_at__gte=timezone.now() - timedelta(days=7)
    ).exclude(account_number='').values('account_number').distinct().count()
    
    # Percentage of accounts with complete data
    accounts_with_complete_data = user_reports.filter(
        account_number__isnull=False,
        service_location__isnull=False,
        credit_limit__isnull=False
    ).exclude(
        account_number='',
        service_location='',
        credit_limit=''
    ).values('account_number').distinct().count()
    
    account_completeness = (accounts_with_complete_data / unique_account_numbers * 100) if unique_account_numbers > 0 else 0
    
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
        'report': {
            'total': total_reports,
            'change': round(reports_change, 1),
            'monthly_growth': round(monthly_growth, 1),
            'system_activity': round(system_activity, 1),
            'today': reports_today,
            'this_week': reports_this_week,
            'this_year': reports_this_year,
            'active': active_reports,
            'with_account': reports_with_account,
            'without_account': reports_without_account,
            'with_foundation_year': reports_with_foundation_year,
            'unique_service_locations': unique_service_locations,
            'latest_date': latest_report_date,
            'oldest_date': oldest_report_date,
            'avg_per_month': avg_reports_per_month,
        },
        'account': {
            'unique_count': unique_account_numbers,
            'with_account': reports_with_account,
            'without_account': reports_without_account,
            'today': accounts_today,
            'this_week': accounts_this_week,
            'this_year': accounts_this_year,
            'growth': round(account_growth, 1),
            'updated_recently': accounts_updated_recently,
            'completeness': round(account_completeness, 1),
            'with_credit_limit': accounts_with_credit_limit,
            'with_biometric': accounts_with_biometric,
            'with_monthly_bill': accounts_with_monthly_bill,
            'with_annual_bill': accounts_with_annual_bill,
            'with_service_recipient': accounts_with_service_recipient,
            'with_monthly_service': accounts_with_monthly_service,
            'with_annual_service': accounts_with_annual_service,
            'with_foundation_year': accounts_with_foundation_year,
            'with_complete_data': accounts_with_complete_data,
        },
        'users': {
            'active': active_users,
            'change': round(users_change, 1),
            'growth': round(user_growth, 1),
        },
    })
