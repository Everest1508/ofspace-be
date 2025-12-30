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
    operation_description="Get dashboard metrics including total reports, active users, monthly growth, and system activity.",
    security=[{'Token': []}],
    responses={
        200: openapi.Response(
            description="Dashboard metrics",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'total_reports': openapi.Schema(type=openapi.TYPE_INTEGER, description='Total number of reports'),
                    'reports_change': openapi.Schema(type=openapi.TYPE_NUMBER, description='Percentage change in reports'),
                    'active_users': openapi.Schema(type=openapi.TYPE_INTEGER, description='Number of active users'),
                    'users_change': openapi.Schema(type=openapi.TYPE_NUMBER, description='Percentage change in users'),
                    'monthly_growth': openapi.Schema(type=openapi.TYPE_NUMBER, description='Monthly growth percentage'),
                    'system_activity': openapi.Schema(type=openapi.TYPE_NUMBER, description='System activity percentage')
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
    
    # Active Users (for admin, otherwise just current user)
    if user.is_staff:
        active_users = User.objects.filter(is_active=True).count()
        last_month_users = User.objects.filter(
            is_active=True,
            date_joined__gte=timezone.now() - timedelta(days=30)
        ).count()
        users_change = ((active_users - last_month_users) / last_month_users * 100) if last_month_users > 0 else 0
    else:
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
    
    return Response({
        'total_reports': total_reports,
        'reports_change': round(reports_change, 1),
        'active_users': active_users,
        'users_change': round(users_change, 1),
        'monthly_growth': round(monthly_growth, 1),
        'system_activity': round(system_activity, 1),
    })
