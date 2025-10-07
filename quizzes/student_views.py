from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Quiz, Question, Option, Submission
from enrollments.models import Enrollment
from courses.models import Course


@login_required
def take_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    course = quiz.course

    # Ensure the student is enrolled & approved
    if not Enrollment.objects.filter(user=request.user, course=course, status="approved").exists():
        messages.error(request, "You are not enrolled in this course.")
        return redirect("courses:catalog")

    questions = quiz.questions.prefetch_related("options")

    if request.method == "POST":
        score = 0
        total = questions.count()

        for q in questions:
            selected = request.POST.get(f"question_{q.id}")
            if selected:
                try:
                    opt = Option.objects.get(id=selected, question=q)
                    if opt.is_correct:
                        score += 1
                except Option.DoesNotExist:
                    pass

        percent = round((score / total) * 100, 2) if total > 0 else 0
        Submission.objects.create(quiz=quiz, user=request.user, score=percent)

        messages.success(request, f"Quiz submitted! You scored {percent}%.")
        return redirect("quizzes:quiz_result", quiz_id=quiz.id)

    return render(request, "student/quizzes/take_quiz.html", {
        "quiz": quiz,
        "questions": questions,
    })


@login_required
def quiz_result(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    sub = Submission.objects.filter(user=request.user, quiz=quiz).order_by("-submitted_at").first()
    return render(request, "student/quizzes/result.html", {"quiz": quiz, "submission": sub})

@login_required
def student_quizzes(request):
    submissions = (Submission.objects
                   .filter(user=request.user)
                   .select_related("quiz", "quiz__course")
                   .order_by("-submitted_at"))
    return render(request, "student/quizzes/list.html", {
        "submissions": submissions,
    })