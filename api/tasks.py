import pandas as pd
from .models import CustomerData,LoanData  # Replace with the correct model import
from background_task import background

@background(schedule=10)
def import_customer_data():
    print("INSIDE CUSTOMER DATA")

    # Load customer data from the Excel file
    customer_data = pd.read_excel('path/to/customer_data.xlsx')

    # Iterate over each row in the DataFrame
    for _, row in customer_data.iterrows():
        # Accessing data from row (which is a pandas Series)
        CustomerData.objects.update_or_create(
            customer_id=row['Customer ID'],  # Match exact column name
            defaults={
                'first_name': row['First Name'],          # Match exact column name
                'last_name': row['Last Name'], 
                'age':row['Age'],        # Match exact column name
                'phone_number': row.get('Phone Number'),  # Match exact column name
                'monthly_salary': row['Monthly Salary'],  # Match exact column name
                'approved_limit': row['Approved Limit'],  # Match exact column name
            }
        )

    print("CUSTOMER DATA IMPORTED IN DB")

@background(schedule=20)
def import_loan_data():
    print("INSIDE LOAN DATA")
    loan_data = pd.read_excel('path/to/loan_data.xlsx')
    for _, row in loan_data.iterrows():
        customer = CustomerData.objects.get(customer_id=row['Customer ID'])
        LoanData.objects.update_or_create(
            loan_id=row['Loan ID'],
            defaults={
                'customer': customer,
                'loan_amount': row['Loan Amount'],
                'tenure': row['Tenure'],
                'interest_rate': row['Interest Rate'],
                'monthly_repayment': row['Monthly payment'],
                'emis_paid_on_time': row['EMIs paid on Time'],
                'start_date': row['Date of Approval'],
                'end_date': row['End Date'],
            }
        )
    print("LOAN DATA IMPORTED IN DB")
