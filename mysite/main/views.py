from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import Enquiry, School, Course, Module  # we'll create this model
import re

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


def course_detail(request, school_slug, course_slug):
    school = get_object_or_404(School, slug=school_slug)
    course = get_object_or_404(Course, slug=course_slug, school=school)
    modules = course.modules.all()
    level_order = [
        ('4', 'Level 4'),
        ('5', 'Level 5'),
        ('6', 'Level 6'),
        ('7', 'Level 7'),
    ]
    modules_by_level = []
    for level_value, level_label in level_order:
        level_modules = modules.filter(level=level_value)
        if level_modules.exists():
            modules_by_level.append({
                'label': level_label,
                'modules': level_modules,
            })
    return render(request, 'main/course_detail.html', {
        'school': school,
        'course': course,
        'modules_by_level': modules_by_level
    })

def apprenticeships(request):
    return render(request, 'main/apprenticeships.html')


def employers(request):
    course_options = []
    courses = Course.objects.select_related('school').all().order_by('school__name', 'title')

    for course in courses:
        raw_cost = (course.cost or '').strip()
        numeric_cost = None

        if raw_cost:
            cleaned = raw_cost.replace(',', '')
            # Pull the first numeric amount from values like "£9,250 per year".
            match = re.search(r'(\d+(?:\.\d+)?)', cleaned)
            if match:
                try:
                    numeric_cost = float(match.group(1))
                except ValueError:
                    numeric_cost = None

        course_options.append({
            'title': course.title,
            'school': course.school.name,
            'display_cost': raw_cost or 'Not set',
            'numeric_cost': numeric_cost,
        })

    return render(request, 'main/employers.html', {'course_options': course_options})
