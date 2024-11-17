from django.db import models
from datetime import date

# Create your models here.
class CustomerData(models.Model):
    customer_id = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15,null=True,)
    monthly_salary = models.DecimalField(max_digits=12, decimal_places=2)
    approved_limit = models.DecimalField(max_digits=12, decimal_places=2)
    age = models.IntegerField()

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.customer_id})"

class LoanData(models.Model):
    customer = models.ForeignKey('api.CustomerData', on_delete=models.CASCADE, related_name='loans')
    loan_id = models.CharField(max_length=20, unique=True)
    loan_amount = models.DecimalField(max_digits=12, decimal_places=2)
    tenure = models.IntegerField()
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    monthly_repayment = models.DecimalField(max_digits=12, decimal_places=2)
    emis_paid_on_time = models.IntegerField()
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return f"Loan ID: {self.loan_id} for Customer ID: {self.customer.customer_id}"
    
    def calculate_credit_score(customer_id):
        customer_loans = LoanData.objects.filter(customer_id=customer_id)
        customer = CustomerData.objects.get(customer_id=customer_id)

        if not customer_loans.exists():
            return 0 
       
        total_current_loans = sum(loan.loan_amount for loan in customer_loans)
        if total_current_loans > customer.approved_limit:
            return 0

        
        score = 0

        total_emis = sum(loan.tenure for loan in customer_loans)
        total_emis_paid_on_time = sum(loan.emis_paid_on_time for loan in customer_loans)
        on_time_percentage = (total_emis_paid_on_time / total_emis) * 100 if total_emis > 0 else 0
        score += (on_time_percentage / 100) * 40

        num_loans = customer_loans.count()
        score += min(num_loans * 5, 10)

        current_year = date.today().year
        active_loans_this_year = sum(
            1 for loan in customer_loans 
            if loan.start_date.year == current_year or loan.end_date.year == current_year
        )

        score += min(active_loans_this_year * 5, 20)

        total_loan_volume = sum(loan.loan_amount for loan in customer_loans)
        score += min(float(total_loan_volume) / float(customer.approved_limit) * 30, 30)

        return round(min(score, 100), 2)