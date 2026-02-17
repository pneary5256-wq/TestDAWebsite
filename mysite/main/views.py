from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import Enquiry, School, Course  # we'll create this model
from django.shortcuts import render

def home(request):
    schools = School.objects.all()
    return render(request, 'main/index.html', {'schools': schools})

def submit_enquiry(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        role = request.POST.get("role")
        message = request.POST.get("message")

        # Save to database
        enquiry = Enquiry(name=name, email=email, role=role, message=message)
        enquiry.save()

        return HttpResponse("Thanks! Your enquiry has been submitted. <a href='/'>Return to home</a>")

    # Optional: redirect if someone visits /submit-enquiry via GET
    return redirect("home")

def school_detail(request, slug):
    school = get_object_or_404(School, slug=slug)
    courses = school.courses.all()
    return render(request, 'main/school_detail.html', {'school': school, 'courses': courses})
