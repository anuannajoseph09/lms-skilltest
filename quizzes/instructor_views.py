from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django import forms
from .models import Quiz, Question, Option
from courses.models import Course

class QuizForm(forms.ModelForm):
    class Meta: model = Quiz; fields = ["title"]

class QuestionForm(forms.ModelForm):
    class Meta: model = Question; fields = ["text","type"]

class OptionForm(forms.ModelForm):
    class Meta: model = Option; fields = ["text","is_correct"]

@login_required
def quiz_manage(request, course_id):
    c = get_object_or_404(Course, pk=course_id, instructor=request.user)
    return render(request, "instructor/quiz_manage.html", {"course": c, "quizzes": c.quizzes.all()})

@login_required
def quiz_create(request, course_id):
    c = get_object_or_404(Course, pk=course_id, instructor=request.user)
    form = QuizForm(request.POST or None)
    if request.method=="POST" and form.is_valid():
        q = form.save(commit=False); q.course=c; q.save()
        messages.success(request,"Quiz created."); return redirect("quizzes:quiz_manage", course_id=c.id)
    return render(request,"instructor/quiz_form.html",{"form":form,"course":c})

@login_required
def question_create(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id, course__instructor=request.user)
    form = QuestionForm(request.POST or None)
    if request.method=="POST" and form.is_valid():
        obj = form.save(commit=False); obj.quiz=quiz; obj.save()
        messages.success(request,"Question added."); return redirect("quizzes:quiz_manage", course_id=quiz.course.id)
    return render(request,"instructor/question_form.html",{"form":form,"quiz":quiz})

@login_required
def option_create(request, q_id):
    question = get_object_or_404(Question, pk=q_id, quiz__course__instructor=request.user)
    form = OptionForm(request.POST or None)
    if request.method=="POST" and form.is_valid():
        op = form.save(commit=False); op.question=question; op.save()
        messages.success(request,"Option added."); return redirect("quizzes:quiz_manage", course_id=question.quiz.course.id)
    return render(request,"instructor/option_form.html",{"form":form,"question":question})

# ====== QUIZ EDIT / DELETE ======

@login_required
def quiz_edit(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id, course__instructor=request.user)
    form = QuizForm(request.POST or None, instance=quiz)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Quiz updated.")
        return redirect("quizzes:quiz_manage", course_id=quiz.course.id)
    return render(request, "instructor/quiz_form.html", {"form": form, "quiz": quiz, "course": quiz.course})

@login_required
def quiz_delete(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id, course__instructor=request.user)
    if request.method == "POST":
        quiz.delete()
        messages.success(request, "Quiz deleted.")
        return redirect("quizzes:quiz_manage", course_id=quiz.course.id)
    return render(request, "instructor/confirm_delete.html", {"what": f"quiz '{quiz.title}'"})

# ====== QUESTION EDIT / DELETE ======

@login_required
def question_edit(request, q_id):
    question = get_object_or_404(Question, pk=q_id, quiz__course__instructor=request.user)
    form = QuestionForm(request.POST or None, instance=question)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Question updated.")
        return redirect("quizzes:quiz_manage", course_id=question.quiz.course.id)
    return render(request, "instructor/question_form.html", {"form": form, "quiz": question.quiz})

@login_required
def question_delete(request, q_id):
    question = get_object_or_404(Question, pk=q_id, quiz__course__instructor=request.user)
    if request.method == "POST":
        cid = question.quiz.course.id
        question.delete()
        messages.success(request, "Question deleted.")
        return redirect("quizzes:quiz_manage", course_id=cid)
    return render(request, "instructor/confirm_delete.html", {"what": f"question '{question.text[:40]}...'"})

# ====== OPTION EDIT / DELETE ======

@login_required
def option_edit(request, op_id):
    option = get_object_or_404(Option, pk=op_id, question__quiz__course__instructor=request.user)
    form = OptionForm(request.POST or None, instance=option)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Option updated.")
        return redirect("quizzes:quiz_manage", course_id=option.question.quiz.course.id)
    return render(request, "instructor/option_form.html", {"form": form, "question": option.question})

@login_required
def option_delete(request, op_id):
    option = get_object_or_404(Option, pk=op_id, question__quiz__course__instructor=request.user)
    if request.method == "POST":
        cid = option.question.quiz.course.id
        option.delete()
        messages.success(request, "Option deleted.")
        return redirect("quizzes:quiz_manage", course_id=cid)
    return render(request, "instructor/confirm_delete.html", {"what": f"option '{option.text[:40]}...'"})

