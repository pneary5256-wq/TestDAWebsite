from django.db import migrations


def normalize_course_fields(apps, schema_editor):
    Course = apps.get_model("main", "Course")

    for course in Course.objects.all():
        updated = False

        # Normalize attendance choice
        if course.attendance == "flexible":
            course.attendance = "part_time"
            updated = True

        # Normalize location choice
        if course.location:
            normalized = course.location.strip().lower()
            if normalized in {"headingley campus", "headingley"}:
                course.location = "headingley"
                updated = True
            elif normalized in {"city campus", "city"}:
                course.location = "city"
                updated = True

        # Normalize cost to always start with £
        if course.cost:
            normalized_cost = course.cost.strip()
            if normalized_cost and not normalized_cost.startswith("£"):
                course.cost = f"£{normalized_cost}"
                updated = True

        if updated:
            course.save(update_fields=["attendance", "location", "cost"])


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0008_alter_module_options_module_level_and_more"),
    ]

    operations = [
        migrations.RunPython(normalize_course_fields, noop_reverse),
    ]
