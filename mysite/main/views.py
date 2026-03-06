from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.conf import settings
from .models import Enquiry, School, Course, Module  # we'll create this model
import re
import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

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


def live_vacancies(request):
    page_size = 10
    api_page_size = 20
    max_scan_pages = 40
    api_error = None
    vacancy_cards = []
    total_pages = 1
    filtered_cards = []

    try:
        page_number = int(request.GET.get('page', 1))
        if page_number < 1:
            page_number = 1
    except ValueError:
        page_number = 1

    target_start = (page_number - 1) * page_size
    target_end = target_start + page_size

    headers = {
        'Ocp-Apim-Subscription-Key': settings.DISPLAY_ADVERT_API_KEY,
        'X-Version': settings.DISPLAY_ADVERT_API_VERSION,
        'Accept': 'application/json; ver=2',
        'User-Agent': 'Mozilla/5.0 (compatible; LBU-Degree-Apprenticeships/1.0)',
    }

    try:
        api_page_number = 1
        api_total_pages = 1
        scanned_pages = 0

        while api_page_number <= api_total_pages and scanned_pages < max_scan_pages:
            query_string = urlencode({
                'PageNumber': api_page_number,
                'PageSize': api_page_size,
                'Sort': 'AgeDesc',
            })
            endpoint = f"{settings.DISPLAY_ADVERT_API_BASE_URL}/vacancy?{query_string}"

            request_obj = Request(endpoint, headers=headers)
            with urlopen(request_obj, timeout=12) as response:
                payload = json.loads(response.read().decode('utf-8'))

            vacancies = payload.get('vacancies') or []
            api_total_pages = payload.get('totalPages') or 1

            for vacancy in vacancies:
                course = vacancy.get('course') or {}
                apprenticeship_level_text = (vacancy.get('apprenticeshipLevel') or '').lower()
                course_level = course.get('level')

                # Automatically exclude Level 3 and below vacancies.
                include_vacancy = False
                if isinstance(course_level, int):
                    include_vacancy = course_level >= 4
                elif any(tag in apprenticeship_level_text for tag in ['higher', 'degree', 'level 4', 'level 5', 'level 6', 'level 7']):
                    include_vacancy = True

                if not include_vacancy:
                    continue

                wage = vacancy.get('wage') or {}
                wage_display = wage.get('wageAdditionalInformation')
                if not wage_display and wage.get('wageAmount'):
                    wage_display = f"GBP {float(wage['wageAmount']):,.2f}"

                if vacancy.get('isNationalVacancy'):
                    location = vacancy.get('isNationalVacancyDetails') or 'National vacancy'
                else:
                    first_address = (vacancy.get('addresses') or [{}])[0]
                    location_parts = [
                        first_address.get('addressLine3'),
                        first_address.get('addressLine4'),
                        first_address.get('postcode'),
                    ]
                    location = ', '.join([part for part in location_parts if part]) or 'Location not specified'

                filtered_cards.append({
                    'title': vacancy.get('title') or 'Untitled vacancy',
                    'employer': vacancy.get('employerName') or 'Employer not specified',
                    'course': course.get('title') or 'Course not specified',
                    'positions': vacancy.get('numberOfPositions') or 0,
                    'closing_date': (vacancy.get('closingDate') or '')[:10],
                    'start_date': (vacancy.get('startDate') or '')[:10],
                    'location': location,
                    'wage': wage_display or 'Wage not specified',
                    'vacancy_url': vacancy.get('vacancyUrl') or vacancy.get('applicationUrl') or '',
                })

            scanned_pages += 1
            api_page_number += 1

            # Stop early once we have enough filtered rows for the requested page.
            if len(filtered_cards) >= target_end:
                break

        vacancy_cards = filtered_cards[target_start:target_end]
        total_pages = max(1, (len(filtered_cards) + page_size - 1) // page_size)

    except HTTPError as exc:
        api_error = f"API request failed with status {exc.code}."
    except URLError:
        api_error = "Unable to connect to the Government vacancies API right now."
    except Exception:
        api_error = "An unexpected error occurred while loading live vacancies."

    context = {
        'vacancy_cards': vacancy_cards,
        'api_error': api_error,
        'page_number': page_number,
        'total_pages': total_pages,
        'has_previous': page_number > 1,
        'has_next': len(filtered_cards) > target_end,
        'previous_page': page_number - 1,
        'next_page': page_number + 1,
    }
    return render(request, 'main/live_vacancies.html', context)


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
