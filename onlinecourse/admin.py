"""
Django admin configuration for the online course application.

This module defines the admin interface for managing courses, lessons, 
questions, choices, instructors, learners, and submissions.
"""

from django.contrib import admin
from .models import Course, Lesson, Instructor, Learner, Question, Choice, Submission


class LessonInline(admin.StackedInline):
    """Inline admin for lessons within course admin."""
    model = Lesson
    extra = 5


class ChoiceInline(admin.StackedInline):
    """Inline admin for choices within question admin."""
    model = Choice
    extra = 2


class QuestionInline(admin.StackedInline):
    """Inline admin for questions within course admin."""
    model = Question
    extra = 2


class CourseAdmin(admin.ModelAdmin):
    """Admin configuration for Course model."""
    inlines = [LessonInline]
    list_display = ('name', 'pub_date')
    list_filter = ['pub_date']
    search_fields = ['name', 'description']


class QuestionAdmin(admin.ModelAdmin):
    """Admin configuration for Question model."""
    inlines = [ChoiceInline]
    list_display = ['content']


class LessonAdmin(admin.ModelAdmin):
    """Admin configuration for Lesson model."""
    list_display = ['title']


# Register models with admin
admin.site.register(Course, CourseAdmin)
admin.site.register(Lesson, LessonAdmin)
admin.site.register(Instructor)
admin.site.register(Learner)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Choice)
admin.site.register(Submission)
