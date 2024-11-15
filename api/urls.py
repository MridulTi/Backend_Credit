from django.contrib import admin
from django.urls import path,include
from rest_framework.routers import DefaultRouter
from . import views

router=DefaultRouter()
router.register(r'customer',views.CustomerViewSet,basename="customer")
router.register(r'loan',views.LoanViewSet,basename="loan")

urlpatterns = [
    path('', views.index,name="index"),
]
urlpatterns+=router.urls