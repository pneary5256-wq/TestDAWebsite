from django.db import migrations
from django.utils.text import slugify


def populate_course_slugs(apps, schema_editor):
    Course = apps.get_model("main", "Course")
    existing = set(Course.objects.exclude(slug__isnull=True).exclude(slug="").values_list("slug", flat=True))

    for course in Course.objects.all():
        if course.slug:
            continue
        base_slug = slugify(course.title)
        slug = base_slug
        counter = 1
        while not slug or slug in existing:
            slug = f"{base_slug}-{counter}"
            counter += 1
        course.slug = slug
        course.save(update_fields=["slug"])
        existing.add(slug)


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0006_course_attendance_course_cost_course_duration_and_more"),
    ]

    operations = [
        migrations.RunPython(populate_course_slugs, noop_reverse),
    ]
