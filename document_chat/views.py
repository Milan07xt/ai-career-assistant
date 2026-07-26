from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser

from .models import Document, ChatMessage
from .serializers import DocumentSerializer, ChatMessageSerializer
from .utils import extract_pages_from_file
from .rag import build_vector_store, query_vector_store

# =====================================================================
# HTML TEMPLATE VIEWS
# =====================================================================

@login_required
def chat_session_view(request, doc_id=None):
    documents = Document.objects.filter(user=request.user)
    active_doc = None
    chat_messages = []
    
    if doc_id:
        active_doc = get_object_or_404(Document, id=doc_id, user=request.user)
        chat_messages = ChatMessage.objects.filter(user=request.user, document=active_doc)
        
        # Handle chat form submissions via POST
        if request.method == "POST":
            message_text = request.POST.get("message", "").strip()
            if message_text:
                # 1. Save User Message
                ChatMessage.objects.create(
                    user=request.user,
                    document=active_doc,
                    sender="user",
                    message=message_text
                )
                
                # 2. Query Vector Store (RAG)
                ai_answer, source_info = query_vector_store(active_doc, message_text)
                
                # 3. Save AI Message
                ChatMessage.objects.create(
                    user=request.user,
                    document=active_doc,
                    sender="ai",
                    message=ai_answer,
                    source_info=source_info
                )
                return redirect("document_chat:session_detail", doc_id=active_doc.id)
                
    return render(request, "document_chat/chat.html", {
        "documents": documents,
        "active_doc": active_doc,
        "chat_messages": chat_messages
    })

@login_required
def upload_document_view(request):
    if request.method == "POST" and request.FILES.get("doc_file"):
        uploaded_file = request.FILES["doc_file"]
        
        # Limit size to 5MB
        if uploaded_file.size > 5 * 1024 * 1024:
            messages.error(request, "File size must be under 5MB.")
            return redirect("document_chat:session")
            
        doc = Document(user=request.user, file=uploaded_file, title=uploaded_file.name)
        doc.save()
        
        # Parse page-by-page text
        pages = extract_pages_from_file(doc.file, uploaded_file.name)
        
        # Build Vector Store
        build_vector_store(doc, pages)
        
        messages.success(request, f"Document '{doc.title}' uploaded and indexed successfully!")
        return redirect("document_chat:session_detail", doc_id=doc.id)
        
    return redirect("document_chat:session")


# =====================================================================
# REST API VIEWS
# =====================================================================

class APIDocumentUploadView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        if not request.FILES.get("file"):
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)
            
        uploaded_file = request.FILES["file"]
        doc = Document(user=request.user, file=uploaded_file, title=uploaded_file.name)
        doc.save()
        
        pages = extract_pages_from_file(doc.file, uploaded_file.name)
        build_vector_store(doc, pages)
        
        serializer = DocumentSerializer(doc)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class APIChatMessageListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ChatMessageSerializer

    def get_queryset(self):
        doc_id = self.kwargs.get("doc_id")
        doc = get_object_or_404(Document, id=doc_id, user=self.request.user)
        return ChatMessage.objects.filter(user=self.request.user, document=doc)

class APIChatAskView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, doc_id, *args, **kwargs):
        doc = get_object_or_404(Document, id=doc_id, user=request.user)
        query_text = request.data.get("message", "").strip()
        
        if not query_text:
            return Response({"error": "Message is required"}, status=status.HTTP_400_BAD_REQUEST)
            
        # 1. Save User Message
        user_msg = ChatMessage.objects.create(
            user=request.user,
            document=doc,
            sender="user",
            message=query_text
        )
        
        # 2. Query Vector Store (RAG)
        ai_answer, source_info = query_vector_store(doc, query_text)
        
        # 3. Save AI Message
        ai_msg = ChatMessage.objects.create(
            user=request.user,
            document=doc,
            sender="ai",
            message=ai_answer,
            source_info=source_info
        )
        
        return Response({
            "user_message": ChatMessageSerializer(user_msg).data,
            "ai_message": ChatMessageSerializer(ai_msg).data
        }, status=status.HTTP_200_OK)
