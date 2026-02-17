from django.urls import path
from . import views

urlpatterns = [
    path('submit-enquiry', views.submit_enquiry, name='submit_enquiry'),
    path('school/<slug:slug>/', views.school_detail, name='school_detail'),
]
