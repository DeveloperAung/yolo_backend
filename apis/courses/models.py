from django.db import models
from apis.core.models import BaseModel  # Assuming BaseModel is in the core app


def course_file_path(instance, filename):
    return "course/{}/{}".format(instance.title, filename)


def lesson_file_path(instance, filename):
    return "course/{}/lessons/{}".format(instance.course.title, filename)


class Course(BaseModel):
    title = models.CharField(max_length=255)
    recommendation = models.CharField(max_length=255, blank=True, null=True)
    total_duration = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True, null=True)
    instructor = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        related_name='courses',
        null=True,
        blank=True
    )
    cover_image = models.ImageField(upload_to=course_file_path, blank=True, null=True)
    demo_video = models.FileField(upload_to=course_file_path, blank=True, null=True)
    is_published = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class Lesson(BaseModel):
    title = models.CharField(max_length=255)
    content = models.TextField(blank=True, null=True)
    video = models.FileField(upload_to=lesson_file_path, blank=True, null=True)  # Field for video files
    duration = models.PositiveIntegerField(help_text="Duration of lesson in minutes", default=0)  # Duration in minutes
    is_demo = models.BooleanField(default=False)
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='lessons'
    )
    order = models.PositiveIntegerField(help_text="Order of the lesson in the course")

    class Meta:
        ordering = ['order']  # Lessons will be ordered by the `order` field

    def __str__(self):
        return f"{self.course.title}: {self.title}"
