from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import UserSettings
from .serializers import UserSettingsSerializer

@swagger_auto_schema(
    method='get',
    operation_description="Get user settings. Creates default settings if they don't exist.",
    security=[{'Token': []}],
    responses={
        200: UserSettingsSerializer,
        401: openapi.Response(description="Unauthorized - Authentication required")
    },
    tags=['Settings']
)
@swagger_auto_schema(
    method='put',
    operation_description="Update user settings (full update). All fields must be provided.",
    security=[{'Token': []}],
    request_body=UserSettingsSerializer,
    responses={
        200: UserSettingsSerializer,
        400: openapi.Response(description="Validation error"),
        401: openapi.Response(description="Unauthorized - Authentication required")
    },
    tags=['Settings']
)
@swagger_auto_schema(
    method='patch',
    operation_description="Partially update user settings. Only provided fields will be updated.",
    security=[{'Token': []}],
    request_body=UserSettingsSerializer,
    responses={
        200: UserSettingsSerializer,
        400: openapi.Response(description="Validation error"),
        401: openapi.Response(description="Unauthorized - Authentication required")
    },
    tags=['Settings']
)
@api_view(['GET', 'PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def user_settings(request):
    """Get or update user settings"""
    try:
        settings = UserSettings.objects.get(user=request.user)
    except UserSettings.DoesNotExist:
        settings = UserSettings.objects.create(user=request.user)
    
    if request.method == 'GET':
        serializer = UserSettingsSerializer(settings)
        return Response(serializer.data)
    
    elif request.method in ['PUT', 'PATCH']:
        serializer = UserSettingsSerializer(settings, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
