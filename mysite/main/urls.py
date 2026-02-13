from django.urls import path
from . import views

urlpatterns = [
    path('submit-enquiry', views.submit_enquiry, name='submit_enquiry'),
]
