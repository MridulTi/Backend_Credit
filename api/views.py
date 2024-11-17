from rest_framework import generics, status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404,HttpResponse
from django.utils import timezone
from datetime import date
import uuid
from .models import CustomerData, LoanData
from .serializer import CustomerSerializer, LoanSerializer
from .tasks import import_customer_data,import_loan_data
import random

def index(request):
    import_customer_data()
    import_loan_data()
    print("WORKIMG?")
    return HttpResponse("WORKING")

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = CustomerData.objects.all()
    serializer_class = CustomerSerializer

    @action(detail=False, methods=['post'])
    def register(self, request, *args, **kwargs):
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        age = request.data.get('age')
        monthly_income = request.data.get('monthly_income')
        phone_number = request.data.get('phone_number')
        
        approved_limit = 36 * monthly_income
        approved_limit = round(approved_limit, -5)  # Round to nearest lakh (100,000)
        
        interest_rate = 0.01
        months = 12  # Example: compound interest over 1 year
        compounded_limit = approved_limit * ((1 + interest_rate) ** months)
        
        while True:
            customer_id = str(random.randint(10, 9999)) 
            if not CustomerData.objects.filter(customer_id=customer_id).exists():
                break

        customer = CustomerData.objects.create(
            customer_id=customer_id,
            first_name=first_name,
            last_name=last_name,
            age=age,
            monthly_salary=monthly_income,
            phone_number=phone_number,
            approved_limit=round(compounded_limit)
        )
        
        response_data = {
            "customer_id": customer.customer_id,
            "name": f"{customer.first_name} {customer.last_name}",
            "age": customer.age,
            "monthly_income": customer.monthly_salary,
            "approved_limit": customer.approved_limit,
            "phone_number": customer.phone_number,
        }
        return Response(response_data, status=status.HTTP_201_CREATED)


class LoanViewSet(viewsets.ModelViewSet):
    queryset = LoanData.objects.all()
    serializer_class = LoanSerializer

    @action(detail=False, methods=['post'])
    def check_eligibility(self, request, *args, **kwargs):
        customer_id = request.data.get('customer_id')
        loan_amount = request.data.get('loan_amount')
        requested_interest_rate = request.data.get('interest_rate')
        tenure = request.data.get('tenure')

        customer = get_object_or_404(CustomerData, id=customer_id)
        monthly_income = customer.monthly_salary
        approved_limit = customer.approved_limit

        credit_score = LoanData.calculate_credit_score(customer_id)
        approval = False
        corrected_interest_rate = requested_interest_rate
        
        if credit_score > 50:
            approval = True
        elif 30 < credit_score <= 50:
            approval = True
            corrected_interest_rate = max(requested_interest_rate, 12)
        elif 10 < credit_score <= 30:
            approval = True
            corrected_interest_rate = max(requested_interest_rate, 16)
        elif credit_score <= 10:
            approval = False
        
        total_current_emis = sum(loan.emis_paid_on_time for loan in LoanData.objects.filter(customer_id=customer_id))
        monthly_installment = calculate_monthly_installment(loan_amount, corrected_interest_rate, tenure)
        
        if total_current_emis + monthly_installment > 0.5 * float(monthly_income):
            approval = False
        
        response_data = {
            "customer_id": customer_id,
            "approval": approval,
            "interest_rate": requested_interest_rate,
            "corrected_interest_rate": corrected_interest_rate,
            "tenure": tenure,
            "monthly_installment": monthly_installment
        }
        return Response(response_data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def create_loan(self, request, *args, **kwargs):
        customer_id = request.data.get('customer_id')
        loan_amount = request.data.get('loan_amount')
        requested_interest_rate = request.data.get('interest_rate')
        tenure = request.data.get('tenure')

        customer = get_object_or_404(CustomerData, id=customer_id)
        approved, corrected_interest_rate, message = check_eligibility_logic(customer, loan_amount, requested_interest_rate, tenure)
        
        if not approved:
            return Response({
                "loan_id": None,
                "customer_id": customer_id,
                "loan_approved": False,
                "message": message,
                "monthly_installment": None
            }, status=status.HTTP_400_BAD_REQUEST)

        monthly_installment = calculate_monthly_installment(loan_amount, corrected_interest_rate, tenure)
        while True:
            loan_id = str(random.randint(10, 9999)) 
            if not LoanData.objects.filter(loan_id=customer_id).exists():
                break
        start_date = timezone.now().date()
        new_year = start_date.year + (start_date.month + tenure - 1) // 12
        new_month = (start_date.month + tenure - 1) % 12 + 1
        end_date = start_date.replace(year=new_year, month=new_month)
        
        loan = LoanData.objects.create(
            customer=customer,
            loan_id=loan_id,
            loan_amount=loan_amount,
            tenure=tenure,
            interest_rate=corrected_interest_rate,
            monthly_repayment=monthly_installment,
            emis_paid_on_time=0,
            start_date=start_date,
            end_date=end_date
        )
        
        response_data = {
            "loan_id": loan.loan_id,
            "customer_id": customer.id,
            "loan_approved": True,
            "message": "Loan approved.",
            "monthly_installment": monthly_installment
        }
        return Response(response_data, status=status.HTTP_201_CREATED)
    
    @action(detail=False,methods=['get'])
    def view_loan_by_customer_id(self,request):
        """View loans by customer ID."""
        customer_id = request.query_params.get('customer_id')
        customer = get_object_or_404(CustomerData, id=customer_id)
        loans = LoanData.objects.filter(customer=customer)

        loans_data = [
            {
                "loan_id": loan.loan_id,
                "loan_amount": loan.loan_amount,
                "interest_rate": loan.interest_rate,
                "monthly_installment": loan.monthly_repayment,
                "repayments_left": max(0, ((loan.end_date.year - date.today().year) * 12 + loan.end_date.month - date.today().month))
            } for loan in loans
        ]
        return Response(loans_data, status=status.HTTP_200_OK)


    @action(detail=False,methods=['get'])
    def view_loan_by_loan_id(self,request):
        """View loan by loan ID."""
        loan_id = request.query_params.get('loan_id')
        loan = get_object_or_404(LoanData, loan_id=loan_id)
        response_data = {
            "loan_id": loan.loan_id,
            "customer": {
                "id": loan.customer.id,
                "name": f"{loan.customer.first_name} {loan.customer.last_name}"
            },
            "loan_amount": loan.loan_amount,
            "interest_rate": loan.interest_rate,
            "monthly_installment": loan.monthly_repayment,
            "tenure": loan.tenure
        }
        return Response(response_data, status=status.HTTP_200_OK)




def calculate_monthly_installment(loan_amount, interest_rate, tenure):
    monthly_interest_rate = interest_rate / 12 / 100
    monthly_installment = loan_amount * (monthly_interest_rate * (1 + monthly_interest_rate) ** tenure) / ((1 + monthly_interest_rate) ** tenure - 1)
    return round(monthly_installment,2)

def check_eligibility_logic(customer, loan_amount, interest_rate, tenure):
    credit_score = LoanData.calculate_credit_score(customer.id)
    approved_limit = customer.approved_limit
    
    if credit_score > 50:
        approved = True
        corrected_interest_rate = interest_rate
    elif 30 < credit_score <= 50:
        approved = True
        corrected_interest_rate = max(interest_rate, 12)
    elif 10 < credit_score <= 30:
        approved = True
        corrected_interest_rate = max(interest_rate, 16)
    else:
        approved = False
        return approved, None, "Loan not approved due to low credit score."
    
    total_current_emis = sum(loan.monthly_repayment for loan in customer.loans.all())
    monthly_installment = calculate_monthly_installment(loan_amount, corrected_interest_rate, tenure)
    
    if float(total_current_emis) + monthly_installment > 0.5 * float(customer.monthly_salary):
        return False, corrected_interest_rate, "Loan not approved: EMIs exceed 50% of monthly income."
    
    return approved, corrected_interest_rate, ""