from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from .models import CustomerData,LoanData
from .tasks import import_customer_data,import_loan_data
from rest_framework.response import Response
from rest_framework.decorators import api_view
import math
import uuid
from django.utils import timezone
from datetime import date

# Create your views here.
def index(request):
    import_loan_data.apply_async()
    import_customer_data.apply_async()
    return HttpResponse("WORKING")


@api_view(['POST'])
def register(request):
    first_name = request.data.get('first_name')
    last_name = request.data.get('last_name')
    age = request.data.get('age')
    monthly_income = request.data.get('monthly_income')
    phone_number = request.data.get('phone_number')
    
    approved_limit = 36 * monthly_income
    approved_limit = round(approved_limit, -5)  # Round to the nearest lakh (100,000)

    interest_rate = 0.01
    months = 12  # Example: compound interest over 1 year
    compounded_limit = approved_limit * ((1 + interest_rate) ** months)

    customer = CustomerData.objects.create(
        first_name=first_name,
        last_name=last_name,
        age=age,
        monthly_income=monthly_income,
        phone_number=phone_number,
        approved_limit=round(compounded_limit)
    )

    # response data
    response_data = {
        "customer_id": customer.id,
        "name": f"{customer.first_name} {customer.last_name}",
        "age": customer.age,
        "monthly_income": customer.monthly_income,
        "approved_limit": customer.approved_limit,
        "phone_number": customer.phone_number,
    }
    
    return Response(response_data)

@api_view(['POST'])
def check_eligibility(request):
    customer_id = request.data.get('customer_id')
    loan_amount = request.data.get('loan_amount')
    requested_interest_rate = request.data.get('interest_rate')
    tenure = request.data.get('tenure')

    customer = get_object_or_404(CustomerData, id=customer_id)
    monthly_income = customer.monthly_income
    approved_limit = customer.approved_limit

    credit_score = calculate_credit_score(customer_id, approved_limit)
    
    approval = False
    corrected_interest_rate = requested_interest_rate
    
    if credit_score > 50:
        approval = True
        corrected_interest_rate = requested_interest_rate
    elif 30 < credit_score <= 50:
        approval = True
        corrected_interest_rate = max(requested_interest_rate, 12)
    elif 10 < credit_score <= 30:
        approval = True
        corrected_interest_rate = max(requested_interest_rate, 16)
    elif credit_score <= 10:
        approval = False
    
    total_current_emis = sum(loan.emi for loan in LoanData.objects.filter(customer_id=customer_id))
    monthly_installment = calculate_monthly_installment(loan_amount, corrected_interest_rate, tenure)
    
    if total_current_emis + monthly_installment > 0.5 * monthly_income:
        approval = False
    
    response_data = {
        "customer_id": customer_id,
        "approval": approval,
        "interest_rate": requested_interest_rate,
        "corrected_interest_rate": corrected_interest_rate if requested_interest_rate != corrected_interest_rate else requested_interest_rate,
        "tenure": tenure,
        "monthly_installment": monthly_installment
    }

    return Response(response_data)

@api_view(['POST'])
def create_loan(request):
    customer_id=request.data.get('customer_id')
    loan_amount=request.data.get('loan_amount')
    requested_interest_rate=request.data.get('interest_rate')
    tenure=request.data.get('tenure')

    # Retrieve customer
    customer = get_object_or_404(CustomerData, id=customer_id)

    # Check eligibility
    approved, corrected_interest_rate, message = check_eligibility(customer, loan_amount, requested_interest_rate, tenure)
    
    if not approved:
        return Response({
            "loan_id": None,
            "customer_id": customer_id,
            "loan_approved": False,
            "message": message,
            "monthly_installment": None
        })

    # Calculate monthly installment
    monthly_installment = calculate_monthly_installment(loan_amount, corrected_interest_rate, tenure)

    # Generate a unique loan ID
    loan_id = str(uuid.uuid4())[:20]

    # Determine loan start and end dates
    start_date = timezone.now().date()
    end_date = start_date.replace(year=start_date.year + tenure // 12, month=start_date.month + tenure % 12)

    # Create and save the loan
    loan = LoanData.objects.create(
        customer=customer,
        loan_id=loan_id,
        loan_amount=loan_amount,
        tenure=tenure,
        interest_rate=corrected_interest_rate,
        monthly_repayment=monthly_installment,
        emis_paid_on_time=0,  # Assuming no payments made initially
        start_date=start_date,
        end_date=end_date
    )
    response_data={
        "loan_id": loan.loan_id,
        "customer_id": customer.id,
        "loan_approved": True,
        "message": "Loan approved.",
        "monthly_installment": monthly_installment
    }
    # Return response
    return Response(response_data)

@api_view(['GET'])
def view_loan_byCustomerId(request,customer_id):
    customer = get_object_or_404(CustomerData, customer_id=customer_id)
    loans = customer.loans.all()

    # Prepare the response data for each loan
    loans_data = []
    for loan in loans:
        # Calculate the remaining EMIs based on end date
        months_left = ((loan.end_date.year - date.today().year) * 12 +
                       loan.end_date.month - date.today().month)
        repayments_left = max(0, months_left)  # Ensure it doesn't go negative
        
        loans_data.append({
            "loan_id": loan.loan_id,
            "loan_amount": float(loan.loan_amount),
            "interest_rate": float(loan.interest_rate),
            "monthly_installment": float(loan.monthly_repayment),
            "repayments_left": repayments_left,
        })

    return Response(loans_data)
    

@api_view(['GET'])
def view_loan_byLoanId(request,loan_id):
    loan = get_object_or_404(LoanData, loan_id=loan_id)
    customer = loan.customer

    # Prepare the response data
    response_data = {
        "loan_id": loan.loan_id,
        "customer": {
            "id": customer.id,
            "first_name": customer.first_name,
            "last_name": customer.last_name,
            "phone_number": customer.phone_number,
            "age": customer.age,
        },
        "loan_amount": float(loan.loan_amount),
        "interest_rate": float(loan.interest_rate),
        "monthly_installment": float(loan.monthly_repayment),
        "tenure": loan.tenure,
    }
    
    return Response(response_data)


# ELIGIBILITY CHECK FUNCTIONS
def calculate_credit_score(customer_id, approved_limit):
    # Fetch loan data for the customer from the database
    loan_data = LoanData.objects.filter(customer_id=customer_id)
    
    if not loan_data.exists():
        return 0  # If no loan history, default score can be set here as required

    past_loans_on_time = loan_data.filter(on_time_payment=True).count()
    total_loans = loan_data.count()
    current_year_loans = loan_data.filter(year=2024).count()  # Assuming 2024 is the current year
    loan_volume = sum(loan.loan_volume for loan in loan_data)

    # Calculate credit score based on criteria
    credit_score = (past_loans_on_time / total_loans) * 40  # 40% weight for on-time payments
    credit_score += min(total_loans, 10) * 10  # 10% for number of loans (capped at 10)
    credit_score += min(current_year_loans, 5) * 10  # 10% for current year activity (capped at 5)
    credit_score += min(loan_volume / approved_limit, 1) * 40  # 40% weight for loan volume ratio

    if loan_volume > approved_limit:
        credit_score = 0

    return credit_score

def calculate_monthly_installment(loan_amount, interest_rate, tenure):
    monthly_interest_rate = interest_rate / 12 / 100
    monthly_installment = loan_amount * (monthly_interest_rate * (1 + monthly_interest_rate) ** tenure) / ((1 + monthly_interest_rate) ** tenure - 1)
    return monthly_installment


def check_eligibility(customer, loan_amount, interest_rate, tenure):
    # Assume a function that checks the credit score based on customer data (from database or logic)
    credit_score = calculate_credit_score(customer.id, customer.approved_limit)
    approved_limit = customer.approved_limit
    
    # Eligibility rules based on credit score
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
        return approved, corrected_interest_rate, "Loan not approved due to low credit score."

    # Check if sum of all current EMIs exceeds 50% of monthly income
    total_current_emis = sum(loan.monthly_repayment for loan in customer.loans.all())
    monthly_installment = calculate_monthly_installment(loan_amount, corrected_interest_rate, tenure)

    if total_current_emis + monthly_installment > 0.5 * customer.monthly_income:
        return False, corrected_interest_rate, "Loan not approved: EMIs exceed 50% of monthly income."

    return approved, corrected_interest_rate, ""