from rest_framework import serializers
from .models import Report

class ReportSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    created_by_email = serializers.EmailField(source='created_by.email', read_only=True)
    
    class Meta:
        model = Report
        fields = [
            'id',
            'service_details',
            'account_number',
            'service_location',
            'foundation_year',
            'usage_details',
            'user_biometric',
            'credit_limit',
            'monthly_bill_report',
            'annual_bill_report',
            'notifications_comments',
            'service_recipient_at_branch',
            'monthly_service_reports',
            'annual_service_reports',
            'created_by',
            'created_by_name',
            'created_by_email',
            'created_at',
            'updated_at',
            'is_active'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)

