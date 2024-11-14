from celery import shared_task
import pandas as pd
from .models import CustomerData,LoanData

@shared_task
def import_customer_data():
    customer_data = pd.read_excel('path/to/customer_data.xlsx')
    print(customer_data)
    # for _, row in customer_data.iterrows():
    #     CustomerData.objects.update_or_create(
    #         customer_id=row['customer_id'],
    #         defaults={
    #             'first_name': row['first_name'],
    #             'last_name': row['last_name'],
    #             'phone_number': row.get('phone_number'),
    #             'monthly_salary': row['monthly_salary'],
    #             'approved_limit': row['approved_limit'],
    #         }
    #     )
@shared_task
def import_loan_data():
    loan_data = pd.read_excel('path/to/loan_data.xlsx')
    print(loan_data)
    # for _, row in loan_data.iterrows():
    #     customer = CustomerData.objects.get(customer_id=row['customer id'])
    #     LoanData.objects.update_or_create(
    #         loan_id=row['loan id'],
    #         defaults={
    #             'customer': customer,
    #             'loan_amount': row['loan amount'],
    #             'tenure': row['tenure'],
    #             'interest_rate': row['interest rate'],
    #             'monthly_repayment': row['monthly repayment (emi)'],
    #             'emis_paid_on_time': row['EMIs paid on time'],
    #             'start_date': row['start date'],
    #             'end_date': row['end date'],
    #         }
    #     )
