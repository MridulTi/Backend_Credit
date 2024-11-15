from django.db import models

# Create your models here.
class CustomerData(models.Model):
    customer_id = models.CharField(max_length=20, unique=True)  # Unique customer ID
    first_name = models.CharField(max_length=100)  # Customer's first name
    last_name = models.CharField(max_length=100)  # Customer's last name
    phone_number = models.CharField(max_length=15,null=True,)  # Customer's phone number
    monthly_salary = models.DecimalField(max_digits=12, decimal_places=2)  # Monthly salary of the customer
    approved_limit = models.DecimalField(max_digits=12, decimal_places=2)  # Approved loan limit
    age = models.IntegerField()  # Customer's age

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.customer_id})"

class LoanData(models.Model):
    customer = models.ForeignKey('api.CustomerData', on_delete=models.CASCADE, related_name='loans')  # Foreign key to CustomerData
    loan_id = models.CharField(max_length=20, unique=True)  # Unique loan ID
    loan_amount = models.DecimalField(max_digits=12, decimal_places=2)  # Loan amount
    tenure = models.IntegerField()  # Loan tenure in months
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)  # Interest rate in percentage
    monthly_repayment = models.DecimalField(max_digits=12, decimal_places=2)  # EMI amount
    emis_paid_on_time = models.IntegerField()  # Number of EMIs paid on time
    start_date = models.DateField()  # Loan start date
    end_date = models.DateField()  # Loan end date

    def __str__(self):
        return f"Loan ID: {self.loan_id} for Customer ID: {self.customer.customer_id}"