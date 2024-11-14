from django.db import models

# Create your models here.
class CustomerData(models.Model):
    customer_id=models.CharField(max_length=20,unique=True)
    first_name=models.CharField(max_length=50)
    last_name=models.CharField(max_length=50)
    phone_number=models.CharField(max_length=15,blank=True,null=True)
    monthly_salary=models.DecimalField(max_digits=10,decimal_places=2)
    approved_limit=models.DecimalField(max_digits=10,decimal_places=2)
    current_debt=models.DecimalField(max_digits=10,decimal_places=2)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.customer_id})"
    
class LoanData(models.Model):
    customer = models.ForeignKey(CustomerData, on_delete=models.CASCADE, related_name='loans')
    loan_id = models.CharField(max_length=20, unique=True)
    loan_amount = models.DecimalField(max_digits=15, decimal_places=2)
    tenure = models.IntegerField(help_text="Loan tenure in months")
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    monthly_repayment = models.DecimalField(max_digits=10, decimal_places=2)
    emis_paid_on_time = models.IntegerField()
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return f"Loan {self.loan_id} for {self.customer}"