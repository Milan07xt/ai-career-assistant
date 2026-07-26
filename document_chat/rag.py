import os
import logging
from django.conf import settings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document as LCDocument
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from ai_services.services import SimpleMockEmbeddings, is_ai_available, generate_text

logger = logging.getLogger(__name__)

def get_embeddings():
    """
    Returns Google GenAI embeddings if API key is active,
    else falls back to SimpleMockEmbeddings.
    """
    if is_ai_available():
        try:
            return GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        except Exception as e:
            logger.error(f"Failed to load GoogleGenerativeAIEmbeddings: {e}")
    return SimpleMockEmbeddings()

def build_vector_store(document_instance, pages):
    """
    Builds and saves a local FAISS index for a specific document.
    """
    embeddings = get_embeddings()
    lc_docs = []
    
    for p in pages:
        text_content = p["text"]
        page_num = p["page_num"]
        
        # Split page content into paragraphs to improve retriever accuracy
        paragraphs = [para.strip() for para in text_content.split("\n\n") if para.strip()]
        
        if not paragraphs:
            paragraphs = [text_content]
            
        for para in paragraphs:
            lc_docs.append(
                LCDocument(
                    page_content=para,
                    metadata={"page_num": page_num, "doc_id": document_instance.id}
                )
            )
            
    if not lc_docs:
        lc_docs.append(
            LCDocument(
                page_content="Empty document.",
                metadata={"page_num": 1, "doc_id": document_instance.id}
            )
        )
        
    db = FAISS.from_documents(lc_docs, embeddings)
    
    # Save FAISS index locally under media/faiss_indices/doc_<id>/
    index_dir = os.path.join(settings.MEDIA_ROOT, "faiss_indices", f"doc_{document_instance.id}")
    os.makedirs(index_dir, exist_ok=True)
    db.save_local(index_dir)
    
    document_instance.faiss_index_path = index_dir.replace("\\", "/")
    document_instance.extracted_text = "\n".join([p["text"] for p in pages])
    document_instance.save()

def query_vector_store(document_instance, query_text):
    """
    Loads the document's FAISS index, retrieves top chunks,
    and runs a constrained Gemini prompt to answer.
    """
    embeddings = get_embeddings()
    index_dir = document_instance.faiss_index_path
    
    if not index_dir or not os.path.exists(index_dir):
        return (
            "The vector index for this document could not be found. Please try re-uploading.",
            []
        )
        
    try:
        # Load local FAISS vector store
        db = FAISS.load_local(index_dir, embeddings, allow_dangerous_deserialization=True)
        
        # Search top 4 matching blocks
        results = db.similarity_search(query_text, k=4)
        
        context_list = []
        source_info = []
        
        for doc in results:
            context_list.append(doc.page_content)
            source_info.append({
                "page_num": doc.metadata.get("page_num", 1),
                "text": doc.page_content
            })
            
        context = "\n\n---\n\n".join(context_list)
        
        # RAG Prompt
        prompt = (
            "You are a helpful AI Document Assistant. Your goal is to answer the user's question "
            "based ONLY on the provided context retrieved from an uploaded document.\n\n"
            "CRITICAL INSTRUCTIONS:\n"
            "1. Answer the question using ONLY facts directly mentioned in the context.\n"
            "2. If the context does not contain the answer, say exactly: 'I cannot find the answer to this question in the uploaded document.'\n"
            "3. Do not make up facts, use outside knowledge, or guess.\n\n"
            f"--- CONTEXT ---\n{context}\n\n"
            f"--- QUESTION ---\n{query_text}\n\n"
            "--- ANSWER ---"
        )
        
        # Call model
        answer = generate_text(prompt)
        
        # Strip potential markdown output around the target fallback text
        if "cannot find the answer to this question" in answer.lower():
            answer = "I cannot find the answer to this question in the uploaded document."
            
        return answer, source_info
        
    except Exception as e:
        logger.error(f"Error querying RAG vector store: {e}")
        return f"An error occurred during query search: {str(e)}", []
