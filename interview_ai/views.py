from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import InterviewSession, InterviewQuestionResponse
from .serializers import InterviewSessionSerializer, InterviewQuestionResponseSerializer
from ai_services.services import generate_interview_questions, evaluate_interview_answer

# =====================================================================
# HTML TEMPLATE VIEWS
# =====================================================================

@login_required
def start_session_view(request):
    roles = ["Python Developer", "Django Developer", "Machine Learning Engineer", "AI Researcher", "SQL Expert", "HR Manager", "Frontend Developer", "Backend Developer"]
    
    if request.method == "POST":
        selected_role = request.POST.get("role")
        if selected_role not in roles:
            selected_role = "Python Developer"
            
        # 1. Create session
        session = InterviewSession.objects.create(user=request.user, role=selected_role)
        
        # 2. Generate questions from AI service
        questions_list = generate_interview_questions(selected_role, count=5)
        
        # 3. Save questions in DB
        for q in questions_list:
            InterviewQuestionResponse.objects.create(
                session=session,
                question_text=q.get("question"),
                question_type=q.get("type", "Technical")
            )
            
        messages.success(request, f"Mock interview started for {selected_role}!")
        return redirect("interview_ai:question", session_id=session.id, question_idx=1)
        
    return render(request, "interview_ai/start.html", {"roles": roles})

@login_required
def question_view(request, session_id, question_idx):
    session = get_object_or_404(InterviewSession, id=session_id, user=request.user, is_completed=False)
    questions = session.questions.all()
    total_questions = questions.count()
    
    if question_idx < 1 or question_idx > total_questions:
        return redirect("interview_ai:start")
        
    # Get current question
    curr_q = questions[question_idx - 1]
    
    if request.method == "POST":
        ans = request.POST.get("answer", "").strip()
        if not ans:
            messages.warning(request, "Please enter an answer to proceed.")
            return redirect("interview_ai:question", session_id=session_id, question_idx=question_idx)
            
        # Call evaluation service
        evaluation = evaluate_interview_answer(curr_q.question_text, ans, session.role)
        
        curr_q.user_answer = ans
        curr_q.score = evaluation.get("score", 5)
        curr_q.feedback = evaluation.get("feedback", "")
        curr_q.suggested_answer = evaluation.get("suggested_answer", "")
        curr_q.save()
        
        # Update overall score
        session.calculate_overall_score()
        
        if question_idx == total_questions:
            session.is_completed = True
            session.save()
            messages.success(request, "Interview completed! View your summary below.")
            return redirect("interview_ai:summary", session_id=session.id)
        else:
            return redirect("interview_ai:question", session_id=session_id, question_idx=question_idx + 1)
            
    context = {
        "session": session,
        "question": curr_q,
        "index": question_idx,
        "total": total_questions,
    }
    return render(request, "interview_ai/question.html", context)

@login_required
def summary_view(request, session_id):
    session = get_object_or_404(InterviewSession, id=session_id, user=request.user)
    
    # overall_score is between 0.0 and 10.0
    overall_score = session.overall_score
    score_percentage = int(overall_score * 10)
    score_dashoffset = int(377 * (100 - score_percentage) / 100)
    
    context = {
        "session": session,
        "score_dashoffset": score_dashoffset,
    }
    return render(request, "interview_ai/summary.html", context)



# =====================================================================
# REST API VIEWS
# =====================================================================

class APIStartSessionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        role = request.data.get("role", "Python Developer")
        session = InterviewSession.objects.create(user=request.user, role=role)
        
        questions_list = generate_interview_questions(role, count=5)
        for q in questions_list:
            InterviewQuestionResponse.objects.create(
                session=session,
                question_text=q.get("question"),
                question_type=q.get("type", "Technical")
            )
            
        serializer = InterviewSessionSerializer(session)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class APISubmitAnswerView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, question_id, *args, **kwargs):
        curr_q = get_object_or_404(InterviewQuestionResponse, id=question_id, session__user=request.user)
        ans = request.data.get("answer", "").strip()
        
        if not ans:
            return Response({"error": "Answer cannot be empty"}, status=status.HTTP_400_BAD_REQUEST)
            
        evaluation = evaluate_interview_answer(curr_q.question_text, ans, curr_q.session.role)
        
        curr_q.user_answer = ans
        curr_q.score = evaluation.get("score", 5)
        curr_q.feedback = evaluation.get("feedback", "")
        curr_q.suggested_answer = evaluation.get("suggested_answer", "")
        curr_q.save()
        
        # Recalculate session score
        curr_q.session.calculate_overall_score()
        
        serializer = InterviewQuestionResponseSerializer(curr_q)
        return Response(serializer.data, status=status.HTTP_200_OK)

class APISessionDetailView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = InterviewSessionSerializer

    def get_object(self):
        session_id = self.kwargs.get("pk")
        return get_object_or_404(InterviewSession, id=session_id, user=self.request.user)
