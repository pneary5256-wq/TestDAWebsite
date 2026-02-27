from django.urls import path
from . import views

urlpatterns = [
    path('submit-enquiry', views.submit_enquiry, name='submit_enquiry'),
    path('apprenticeships/', views.apprenticeships, name='apprenticeships'),
    path('school/<slug:slug>/', views.school_detail, name='school_detail'),
    path('school/<slug:school_slug>/course/<slug:course_slug>/', views.course_detail, name='course_detail'),
]
