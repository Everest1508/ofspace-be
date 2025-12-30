from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .serializers import UserSerializer, LoginSerializer, ChangePasswordSerializer

User = get_user_model()

@swagger_auto_schema(
    method='post',
    operation_description="Authenticate user with email and password. Returns authentication token and user information.",
    request_body=LoginSerializer,
    responses={
        200: openapi.Response(
            description="Successful login",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'token': openapi.Schema(type=openapi.TYPE_STRING, description='Authentication token'),
                    'user': openapi.Schema(type=openapi.TYPE_OBJECT, description='User information')
                }
            )
        ),
        400: openapi.Response(description="Invalid credentials or validation error")
    },
    tags=['Authentication']
)
@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """Login endpoint"""
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        user_serializer = UserSerializer(user)
        return Response({
            'token': token.key,
            'user': user_serializer.data
        }, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='post',
    operation_description="Logout user and invalidate authentication token.",
    security=[{'Token': []}],
    responses={
        200: openapi.Response(
            description="Successfully logged out",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING, example='Successfully logged out')
                }
            )
        ),
        401: openapi.Response(description="Unauthorized - Authentication required")
    },
    tags=['Authentication']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """Logout endpoint"""
    try:
        request.user.auth_token.delete()
    except:
        pass
    return Response({'message': 'Successfully logged out'}, status=status.HTTP_200_OK)

@swagger_auto_schema(
    method='get',
    operation_description="Get current authenticated user information.",
    security=[{'Token': []}],
    responses={
        200: UserSerializer,
        401: openapi.Response(description="Unauthorized - Authentication required")
    },
    tags=['Authentication']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    """Get current user"""
    serializer = UserSerializer(request.user)
    return Response(serializer.data)

@swagger_auto_schema(
    method='put',
    operation_description="Update user profile information. Use PUT for full update or PATCH for partial update.",
    security=[{'Token': []}],
    request_body=UserSerializer,
    responses={
        200: UserSerializer,
        400: openapi.Response(description="Validation error"),
        401: openapi.Response(description="Unauthorized - Authentication required")
    },
    tags=['Authentication']
)
@swagger_auto_schema(
    method='patch',
    operation_description="Partially update user profile information.",
    security=[{'Token': []}],
    request_body=UserSerializer,
    responses={
        200: UserSerializer,
        400: openapi.Response(description="Validation error"),
        401: openapi.Response(description="Unauthorized - Authentication required")
    },
    tags=['Authentication']
)
@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    """Update user profile"""
    serializer = UserSerializer(request.user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='post',
    operation_description="Change user password. Requires old password and new password.",
    security=[{'Token': []}],
    request_body=ChangePasswordSerializer,
    responses={
        200: openapi.Response(
            description="Password updated successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING, example='Password updated successfully')
                }
            )
        ),
        400: openapi.Response(description="Invalid old password or validation error"),
        401: openapi.Response(description="Unauthorized - Authentication required")
    },
    tags=['Authentication']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """Change password"""
    serializer = ChangePasswordSerializer(data=request.data)
    if serializer.is_valid():
        user = request.user
        if not user.check_password(serializer.validated_data['old_password']):
            return Response({'old_password': 'Wrong password.'}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({'message': 'Password updated successfully'}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
