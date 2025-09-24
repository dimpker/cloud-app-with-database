"""
Django models for the online course application.

This module defines the data models for courses, users, questions, and submissions.
"""

from django.conf import settings
from django.db import models
from django.utils.timezone import now

# Configure Django imports with proper error handling
try:
    # Test if Django models are properly loaded
    models.Model
except AttributeError as exc:
    print("There was an error loading django modules. Do you have django installed?")
    raise ImportError("Django modules not available") from exc


# Instructor model
class Instructor(models.Model):
    """
    Model representing a course instructor.
    
    Attributes:
        user: Foreign key to the User model
        full_time: Boolean indicating if instructor works full-time
        total_learners: Number of learners assigned to this instructor
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    full_time = models.BooleanField(default=True)
    total_learners = models.IntegerField()

    def __str__(self):
        """Return string representation of instructor."""
        return self.user.username


# Learner model
class Learner(models.Model):
    """
    Model representing a course learner/student.
    
    Attributes:
        user: Foreign key to the User model
        occupation: Learner's occupation from predefined choices
        social_link: URL to learner's social media profile
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    STUDENT = 'student'
    DEVELOPER = 'developer'
    DATA_SCIENTIST = 'data_scientist'
    DATABASE_ADMIN = 'dba'
    OCCUPATION_CHOICES = [
        (STUDENT, 'Student'),
        (DEVELOPER, 'Developer'),
        (DATA_SCIENTIST, 'Data Scientist'),
        (DATABASE_ADMIN, 'Database Admin')
    ]
    occupation = models.CharField(
        null=False,
        max_length=20,
        choices=OCCUPATION_CHOICES,
        default=STUDENT
    )
    social_link = models.URLField(max_length=200)

    def __str__(self):
        """Return string representation of learner."""
        return f"{self.user.username},{self.occupation}"


# Course model
class Course(models.Model):
    """
    Model representing an online course.
    
    Attributes:
        name: Course name (max 30 characters)
        image: Course image uploaded to course_images/
        description: Detailed course description
        pub_date: Date when course was published
        instructors: Many-to-many relationship with instructors
        users: Many-to-many relationship with users through enrollment
        total_enrollment: Total number of enrolled students
        is_enrolled: Boolean flag for enrollment status
    """
    name = models.CharField(null=False, max_length=30, default='online course')
    image = models.ImageField(upload_to='course_images/')
    description = models.CharField(max_length=1000)
    pub_date = models.DateField(null=True)
    instructors = models.ManyToManyField(Instructor)
    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='Enrollment'
    )
    total_enrollment = models.IntegerField(default=0)
    is_enrolled = False

    def __str__(self):
        """Return string representation of course."""
        return f"Name: {self.name}, Description: {self.description}"


# Lesson model
class Lesson(models.Model):
    """
    Model representing a lesson within a course.
    
    Attributes:
        title: Lesson title
        order: Order of lesson within the course
        course: Foreign key to the Course model
        content: Lesson content (text)
    """
    title = models.CharField(max_length=200, default="title")
    order = models.IntegerField(default=0)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    content = models.TextField()

    def __str__(self):
        """Return string representation of lesson."""
        return f"{self.title} (Course: {self.course.name})"


# Enrollment model
class Enrollment(models.Model):
    """
    Model representing a user's enrollment in a course.
    
    Once a user enrolls in a class, an enrollment entry is created between 
    the user and course. This can be used to track exam submissions and other
    enrollment-related information.
    
    Attributes:
        user: Foreign key to the User model
        course: Foreign key to the Course model
        date_enrolled: Date when user enrolled
        mode: Enrollment mode (audit, honor, beta)
        rating: User's rating of the course
    """
    AUDIT = 'audit'
    HONOR = 'honor'
    BETA = 'BETA'
    COURSE_MODES = [
        (AUDIT, 'Audit'),
        (HONOR, 'Honor'),
        (BETA, 'BETA')
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date_enrolled = models.DateField(default=now)
    mode = models.CharField(max_length=5, choices=COURSE_MODES, default=AUDIT)
    rating = models.FloatField(default=5.0)

    def __str__(self):
        """Return string representation of enrollment."""
        return f"{self.user.username} enrolled in {self.course.name}"


class Question(models.Model):
    """
    Model representing a question in a course exam.
    
    Attributes:
        course: Foreign key to the Course model
        content: Question text
        grade: Points awarded for correct answer
    """
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    content = models.CharField(max_length=200)
    grade = models.IntegerField(default=50)

    def __str__(self):
        """Return string representation of question."""
        return f"Question: {self.content}"

    def is_get_score(self, selected_ids):
        """
        Calculate if the learner gets the score for this question.
        
        Args:
            selected_ids: List of selected choice IDs
            
        Returns:
            bool: True if learner selected all correct answers, False otherwise
        """
        all_answers = self.choice_set.filter(is_correct=True).count()
        selected_correct = self.choice_set.filter(
            is_correct=True,
            id__in=selected_ids
        ).count()
        return all_answers == selected_correct

class Choice(models.Model):
    """
    Model representing a choice/answer option for a question.
    
    Attributes:
        question: Foreign key to the Question model
        content: Choice text
        is_correct: Boolean indicating if this is the correct answer
    """
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    content = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        """Return string representation of choice."""
        return f"{self.content} ({'Correct' if self.is_correct else 'Incorrect'})"

class Submission(models.Model):
    """
    Model representing a student's exam submission.
    
    One enrollment can have multiple submissions.
    One submission can have multiple choices.
    One choice can belong to multiple submissions.
    
    Attributes:
        enrollment: Foreign key to the Enrollment model
        choices: Many-to-many relationship with Choice model
    """
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE)
    choices = models.ManyToManyField(Choice)

    def __str__(self):
        """Return string representation of submission."""
        return f"Submission by {self.enrollment.user.username} for {self.enrollment.course.name}"
