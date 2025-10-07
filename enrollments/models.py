# enrollments/models.py
from django.db import models
from django.conf import settings


class Enrollment(models.Model):
    # ---- status constants & choices
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    STATUS_CHOICES = [
        (PENDING, "Pending"),
        (APPROVED, "Approved"),
        (REJECTED, "Rejected"),
    ]

    # ---- relations
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="enrollments",
    )
    course = models.ForeignKey(
        "courses.Course",
        on_delete=models.CASCADE,
        related_name="enrollments",  # used for instructor dashboards, counts, etc.
    )

    # ---- data
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=APPROVED,  # set to PENDING if you want approval flow by default
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "course")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} -> {self.course} ({self.status})"

    # -------------------------------------------------
    # Computed helpers (no DB columns; safe w/out migrations)
    # -------------------------------------------------
    @property
    def progress_percent(self) -> int:
        """
        % of lessons completed by this user in this course.
        Returns 0 if there are no lessons or if the learning app isn't wired yet.
        """
        total = self.course.lessons.count()
        if total == 0:
            return 0

        try:
            # optional dependency; student side will create these rows
            from learning.models import LessonCompletion
        except Exception:
            return 0

        completed = (
            LessonCompletion.objects.filter(
                student=self.user, course=self.course
            ).values("lesson").distinct().count()
        )
        return round(completed * 100 / total)

    @property
    def last_quiz_score(self):
        """
        Latest quiz score for this user in this course.
        Returns None if there are no submissions or quizzes app isn’t present.
        """
        try:
            from quizzes.models import Submission
        except Exception:
            return None

        submission = (
            Submission.objects.filter(
                student=self.user, quiz__course=self.course
            ).order_by("-created_at").first()
        )
        return getattr(submission, "score", None)
