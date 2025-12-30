from rest_framework import viewsets
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Report
from .serializers import ReportSerializer

class ReportViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing Report instances.
    
    Provides CRUD operations for reports:
    - list: Get all reports for the authenticated user
    - create: Create a new report
    - retrieve: Get a specific report by ID
    - update: Update a report (full update)
    - partial_update: Partially update a report
    - destroy: Delete a report
    """
    serializer_class = ReportSerializer
    
    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Report.objects.filter(created_by=self.request.user)
        # Return empty queryset for unauthenticated users (e.g., during schema generation)
        return Report.objects.none()
    
    @swagger_auto_schema(
        operation_description="List all reports created by the authenticated user.",
        security=[{'Token': []}],
        responses={
            200: ReportSerializer(many=True),
            401: openapi.Response(description="Unauthorized - Authentication required")
        },
        tags=['Reports']
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Create a new report with service and billing details.",
        security=[{'Token': []}],
        request_body=ReportSerializer,
        responses={
            201: ReportSerializer,
            400: openapi.Response(description="Validation error"),
            401: openapi.Response(description="Unauthorized - Authentication required")
        },
        tags=['Reports']
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Retrieve a specific report by ID.",
        security=[{'Token': []}],
        responses={
            200: ReportSerializer,
            404: openapi.Response(description="Report not found"),
            401: openapi.Response(description="Unauthorized - Authentication required")
        },
        tags=['Reports']
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Update a report (full update). All fields must be provided.",
        security=[{'Token': []}],
        request_body=ReportSerializer,
        responses={
            200: ReportSerializer,
            400: openapi.Response(description="Validation error"),
            404: openapi.Response(description="Report not found"),
            401: openapi.Response(description="Unauthorized - Authentication required")
        },
        tags=['Reports']
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Partially update a report. Only provided fields will be updated.",
        security=[{'Token': []}],
        request_body=ReportSerializer,
        responses={
            200: ReportSerializer,
            400: openapi.Response(description="Validation error"),
            404: openapi.Response(description="Report not found"),
            401: openapi.Response(description="Unauthorized - Authentication required")
        },
        tags=['Reports']
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Delete a report by ID.",
        security=[{'Token': []}],
        responses={
            204: openapi.Response(description="Report deleted successfully"),
            404: openapi.Response(description="Report not found"),
            401: openapi.Response(description="Unauthorized - Authentication required")
        },
        tags=['Reports']
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
