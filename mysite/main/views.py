from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Enquiry  # we'll create this model
from django.shortcuts import render

def home(request):
    return render(request, 'main/index.html')

def submit_enquiry(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        role = request.POST.get("role")
        message = request.POST.get("message")

        # Save to database
        enquiry = Enquiry(name=name, email=email, role=role, message=message)
        enquiry.save()

        return HttpResponse("Thanks! Your enquiry has been submitted.")

    # Optional: redirect if someone visits /submit-enquiry via GET
    return redirect("home")
