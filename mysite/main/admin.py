from django.contrib import admin
from .models import Enquiry, School, Course, Module

@admin.register(Enquiry)
class EnquiryAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'role')

@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'image_url')
    prepopulated_fields = {'slug': ('name',)}


class ModuleInline(admin.TabularInline):
    model = Module
    extra = 3
    fields = ('level', 'order', 'title', 'description')


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'school', 'attendance', 'duration', 'location')
    prepopulated_fields = {'slug': ('title',)}
    list_filter = ('school', 'attendance', 'location')
    search_fields = ('title', 'description')
    inlines = [ModuleInline]
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'school', 'description', 'image_url')
        }),
        ('Course Details', {
            'fields': ('attendance', 'duration', 'location', 'cost', 'entry_requirements')
        }),
    )
