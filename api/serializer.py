from rest_framework import serializers
from .models import CustomerData, LoanData

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerData
        fields = ['customer_id', 'first_name', 'last_name', 'phone_number', 'monthly_salary', 'approved_limit', 'age']


class LoanSerializer(serializers.ModelSerializer):
    # Nested serializer to include customer details in loan data
    customer_id = serializers.CharField(source='customer.customer_id', read_only=True)  # Include customer ID in loan data

    class Meta:
        model = LoanData
        fields = [
            'loan_id', 'loan_amount', 'tenure', 'interest_rate', 'monthly_repayment',
            'emis_paid_on_time', 'start_date', 'end_date', 'customer_id'
        ]