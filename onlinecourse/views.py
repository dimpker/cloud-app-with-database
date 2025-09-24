"""
Django views for the online course application.

This module contains view functions and classes for handling user registration,
authentication, course display, enrollment, and exam functionality.
"""

import logging

from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views import generic

from .models import Course, Enrollment, Submission

# Get an instance of a logger
logger = logging.getLogger(__name__)


def registration_request(request):
    """Handle user registration requests."""
    context = {}
    if request.method == 'GET':
        return render(request, 'onlinecourse/user_registration_bootstrap.html', context)

    if request.method == 'POST':
        # Check if user exists
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except User.DoesNotExist:
            logger.info("New user registration: %s", username)

        if not user_exist:
            user = User.objects.create_user(
                username=username,
                first_name=first_name,
                last_name=last_name,
                password=password
            )
            login(request, user)
            return redirect("onlinecourse:index")

        context['message'] = "User already exists."
        return render(request, 'onlinecourse/user_registration_bootstrap.html', context)

    return render(request, 'onlinecourse/user_registration_bootstrap.html', context)


def login_request(request):
    """Handle user login requests."""
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['psw']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('onlinecourse:index')

        context['message'] = "Invalid username or password."
        return render(request, 'onlinecourse/user_login_bootstrap.html', context)

    return render(request, 'onlinecourse/user_login_bootstrap.html', context)


def logout_request(request):
    """Handle user logout requests."""
    logout(request)
    return redirect('onlinecourse:index')


def check_if_enrolled(user, course):
    """Check if a user is enrolled in a specific course."""
    is_enrolled = False
    if user.id is not None:
        # Check if user enrolled
        num_results = Enrollment.objects.filter(user=user, course=course).count()
        if num_results > 0:
            is_enrolled = True
    return is_enrolled

def submit(request, course_id):
    """Create an exam submission record for a course enrollment."""
    course = get_object_or_404(Course, pk=course_id)
    user = request.user
    enrollment = Enrollment.objects.get(user=user, course=course)
    submission = Submission.objects.create(enrollment=enrollment)
    choices = extract_answers(request)
    submission.choices.set(choices)
    submission_id = submission.id
    return HttpResponseRedirect(
        reverse(viewname='onlinecourse:exam_result', args=(course_id, submission_id,))
    )

def extract_answers(request):
    """Collect the selected choices from the exam form from the request object."""
    submitted_answers = []
    for key in request.POST:
        if key.startswith('choice'):
            value = request.POST[key]
            choice_id = int(value)
            submitted_answers.append(choice_id)
    return submitted_answers

def show_exam_result(request, course_id, submission_id):
    """Show exam result to student after submission."""
    context = {}
    course = get_object_or_404(Course, pk=course_id)
    submission = Submission.objects.get(id=submission_id)
    choices = submission.choices.all()

    total_score = 0
    questions = course.question_set.all()

    for question in questions:
        # Get all correct choices for the question
        correct_choices = question.choice_set.filter(is_correct=True)
        # Get the user's selected choices for the question
        selected_choices = choices.filter(question=question)

        # Check if the selected choices are the same as the correct choices
        if set(correct_choices) == set(selected_choices):
            # Add the question's grade only if all correct answers are selected
            total_score += question.grade

    context['course'] = course
    context['grade'] = total_score
    context['choices'] = choices

    return render(request, 'onlinecourse/exam_result_bootstrap.html', context)


class CourseListView(generic.ListView):
    """Display a list of courses ordered by enrollment."""
    template_name = 'onlinecourse/course_list_bootstrap.html'
    context_object_name = 'course_list'

    def get_queryset(self):
        """Get the list of courses with enrollment status."""
        user = self.request.user
        courses = Course.objects.order_by('-total_enrollment')[:10]
        for course in courses:
            if user.is_authenticated:
                course.is_enrolled = check_if_enrolled(user, course)
        return courses


class CourseDetailView(generic.DetailView):
    """Display detailed view of a single course."""
    model = Course
    template_name = 'onlinecourse/course_detail_bootstrap.html'


def enroll(request, course_id):
    """Handle course enrollment for authenticated users."""
    course = get_object_or_404(Course, pk=course_id)
    user = request.user

    is_enrolled = check_if_enrolled(user, course)
    if not is_enrolled and user.is_authenticated:
        # Create an enrollment
        Enrollment.objects.create(user=user, course=course, mode='honor')
        course.total_enrollment += 1
        course.save()

    return HttpResponseRedirect(
        reverse(viewname='onlinecourse:course_details', args=(course.id,))
    )
