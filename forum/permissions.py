from enrollments.models import Enrollment

def is_instructor(user):
    return callable(getattr(user, "is_instructor", None)) and user.is_instructor()

def is_student(user):
    return callable(getattr(user, "is_student", None)) and user.is_student()

def student_is_enrolled(user, course):
    return Enrollment.objects.filter(user=user, course=course, status=Enrollment.APPROVED).exists()
