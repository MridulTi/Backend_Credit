from django.shortcuts import render
from django.http import HttpResponse
from .importing import async_import_data

# Create your views here.
def index(request):
    async_import_data()
    return HttpResponse("WORKING")


def register(request):
    return HttpResponse("REGISTER")

def check_eligibility(request):
    return HttpResponse("REGISTER")

def create_loan(request):
    return HttpResponse("create_loan")

def view_loan_byCustomerId(request):
    return HttpResponse("view_loan")

def view_loan_byLoanId(request):
    return HttpResponse("view_loan")

