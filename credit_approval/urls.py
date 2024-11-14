from django.urls import path
from credit_approval import views

urlpatterns = [
    path('',views.index, name="index"),
    path('register/',views.register, name="register"),
    path('view-loan/<int:loan_id>/',views.view_loan_byLoanId, name="view_loan_byLoanId"),
    path('view-loans/<int:customer_id>/',views.view_loan_byCustomerId, name="view_loan_byCustomerId"),
    path('create-loan/',views.create_loan, name="create_loan"),
]