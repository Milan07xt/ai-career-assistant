import os
import json
import logging
import google.generativeai as genai
from django.conf import settings

logger = logging.getLogger(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

def is_ai_available():
    return bool(GEMINI_API_KEY)

def generate_text(prompt, system_instruction=None):
    """
    Calls Gemini API to generate text. Falls back to mock response if key is missing.
    """
    if is_ai_available():
        try:
            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                system_instruction=system_instruction
            )
            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            logger.error(f"Gemini API Error: {e}")
            # fall through to mock

    # Mock implementation
    prompt_lower = prompt.lower()
    if "cover letter" in prompt_lower:
        return (
            "Dear Hiring Manager,\n\n"
            "I am writing to express my strong interest in the role. "
            "With my background in software development and technical expertise, I am confident that I can add great value to your team. "
            "My experience aligns well with the skills requested in your job posting.\n\n"
            "I look forward to discussing how my skills and experience can help your team succeed.\n\n"
            "Sincerely,\nAI Career Assistant User"
        )
    return f"Mock Response: I analyzed your request for '{prompt[:100]}'. Please set GEMINI_API_KEY in your environment for live AI outputs."

def get_resume_analysis(resume_text):
    """
    Analyzes resume text using Gemini API and returns structured JSON analysis.
    """
    system_instruction = (
        "You are an expert ATS (Applicant Tracking System) parser and career coach. "
        "Analyze the provided resume and return a JSON object with the following structure: "
        "{"
        "  'ats_score': 85,"
        "  'grammar_score': 90,"
        "  'formatting_score': 80,"
        "  'keyword_match': 75,"
        "  'summary': 'Brief professional summary...',"
        "  'missing_skills': ['SkillA', 'SkillB'],"
        "  'missing_tech': ['TechA', 'TechB'],"
        "  'grammar_issues': ['Issue 1', 'Issue 2'],"
        "  'improvements': ['Improvement 1', 'Improvement 2'],"
        "  'certifications': ['Cert 1', 'Cert 2'],"
        "  'projects': ['Project idea 1', 'Project idea 2'],"
        "  'resources': ['Resource 1', 'Resource 2']"
        "}"
    )

    if is_ai_available():
        try:
            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                generation_config={"response_mime_type": "application/json"},
                system_instruction=system_instruction
            )
            response = model.generate_content(f"Analyze this resume content:\n\n{resume_text}")
            return json.loads(response.text)
        except Exception as e:
            logger.error(f"Gemini Resume Analysis Error: {e}")
            # fall through

    # Fallback/Mock Resume Analysis
    # Dynamically extract some terms if they exist
    skills = []
    if "python" in resume_text.lower():
        skills.append("Django")
        skills.append("SQLAlchemy")
    else:
        skills.append("Python")
        skills.append("SQL")
    
    return {
        "ats_score": 78,
        "grammar_score": 85,
        "formatting_score": 80,
        "keyword_match": 70,
        "summary": "The resume shows a solid technical foundation. There are opportunities to emphasize project outcomes, clear metrics, and modern architectural skills.",
        "missing_skills": skills + ["REST APIs", "Git", "PostgreSQL"],
        "missing_tech": ["Docker", "Redis", "Celery", "AWS"],
        "grammar_issues": ["Consider active verbs instead of passive voice in project descriptions.", "Avoid repetitive phrases like 'responsible for'."],
        "improvements": [
            "Quantify achievements in your professional experience section (e.g., 'reduced page load time by 30%').",
            "Rearrange skills section to highlight primary technologies first.",
            "Shorten summary section to a punchy 3-sentence elevator pitch."
        ],
        "certifications": [
            "AWS Certified Developer - Associate",
            "Professional Scrum Master (PSM I)"
        ],
        "projects": [
            "Build a personal portfolio showcasing RESTful microservices and deploy it on Render.",
            "Create a real-time collaborative task planner using Django Channels/WebSockets."
        ],
        "resources": [
            "Django REST Framework documentation (django-rest-framework.org)",
            "MDN Web Docs - Advanced Client-side JavaScript Guide"
        ]
    }

def generate_interview_questions(role, count=5):
    """
    Generates list of questions for a role.
    """
    system_instruction = (
        "You are an technical interviewer. "
        "Provide a JSON list of objects representing interview questions for the specified role. "
        "Each question should have: 'id' (integer), 'question' (string), 'type' (string: 'Coding', 'Behavioral', 'Technical'). "
        "Format: [{'id': 1, 'question': '...', 'type': '...'}]"
    )

    if is_ai_available():
        try:
            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                generation_config={"response_mime_type": "application/json"},
                system_instruction=system_instruction
            )
            response = model.generate_content(f"Generate {count} questions for a {role} role.")
            return json.loads(response.text)
        except Exception as e:
            logger.error(f"Gemini Interview Questions Error: {e}")

    # Fallback mock questions based on role
    role_lower = role.lower()
    if "python" in role_lower or "django" in role_lower or "backend" in role_lower:
        return [
            {"id": 1, "question": "What is the difference between lists and tuples in Python, and when would you use each?", "type": "Technical"},
            {"id": 2, "question": "How does Django's middleware work, and how would you implement a custom middleware?", "type": "Technical"},
            {"id": 3, "question": "Write a Python function to reverse a linked list in-place.", "type": "Coding"},
            {"id": 4, "question": "Describe a time when you had to debug a complex database performance issue. What steps did you take?", "type": "Behavioral"},
            {"id": 5, "question": "What are Python decorators, and how do you write a decorator that accepts arguments?", "type": "Technical"},
        ]
    elif "sql" in role_lower or "database" in role_lower:
        return [
            {"id": 1, "question": "What is the difference between WHERE and HAVING clauses in SQL?", "type": "Technical"},
            {"id": 2, "question": "Explain database normalization up to 3NF.", "type": "Technical"},
            {"id": 3, "question": "Write a query to find the second highest salary from an Employee table.", "type": "Coding"},
            {"id": 4, "question": "How do indexes speed up query execution, and what are their drawbacks?", "type": "Technical"},
            {"id": 5, "question": "How would you resolve a deadlock issue in a highly concurrent database system?", "type": "Behavioral"},
        ]
    elif "ml" in role_lower or "ai" in role_lower or "machine learning" in role_lower:
        return [
            {"id": 1, "question": "What is the difference between L1 (Lasso) and L2 (Ridge) regularization?", "type": "Technical"},
            {"id": 2, "question": "Explain the concept of overfitting and how you can prevent it.", "type": "Technical"},
            {"id": 3, "question": "Describe how a transformer self-attention mechanism works.", "type": "Technical"},
            {"id": 4, "question": "Write a simple helper function to calculate precision, recall, and F1-score from a confusion matrix.", "type": "Coding"},
            {"id": 5, "question": "Tell me about a time you worked on a machine learning model that underperformed in production. How did you diagnose and fix it?", "type": "Behavioral"},
        ]
    else:  # HR / General
        return [
            {"id": 1, "question": "Tell me about yourself and your career goals.", "type": "Behavioral"},
            {"id": 2, "question": "How do you handle disagreements or conflicts within a technical team?", "type": "Behavioral"},
            {"id": 3, "question": "Describe a challenging project you worked on. What was your role and how did you ensure its success?", "type": "Behavioral"},
            {"id": 4, "question": "What is your approach to learning new technologies or frameworks quickly?", "type": "Behavioral"},
            {"id": 5, "question": "Why do you want to join our company, and what value can you bring to our team?", "type": "Behavioral"},
        ]

def evaluate_interview_answer(question, answer, role):
    """
    Evaluates interview response and returns score and feedback.
    """
    system_instruction = (
        "You are a technical interviewer evaluating an applicant's answer. "
        "Return a JSON object with: 'score' (integer between 1 and 10), 'feedback' (string), and 'suggested_answer' (string). "
        "Format: {'score': 8, 'feedback': '...', 'suggested_answer': '...'}"
    )

    if is_ai_available():
        try:
            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                generation_config={"response_mime_type": "application/json"},
                system_instruction=system_instruction
            )
            prompt = f"Role: {role}\nQuestion: {question}\nApplicant Answer: {answer}"
            response = model.generate_content(prompt)
            return json.loads(response.text)
        except Exception as e:
            logger.error(f"Gemini Answer Evaluation Error: {e}")

    # Fallback mock evaluation
    word_count = len(answer.split())
    if word_count < 5:
        score = 2
        feedback = "Your answer is extremely brief. Try to explain the concepts in more depth and give practical examples."
    elif word_count < 20:
        score = 5
        feedback = "You mentioned some key points, but the answer lacks technical depth and examples. Expand on the inner workings of the concept."
    else:
        score = 8
        feedback = "Good response! You clearly understand the core principles. To make it a perfect 10, explain how you would apply this in real-world scale or production debugging."

    return {
        "score": score,
        "feedback": feedback,
        "suggested_answer": f"For '{question[:60]}...', a complete answer would explain the definition, inner mechanics, complexity trade-offs, and practical examples of use."
    }

# Mock LangChain embedding class to avoid PyTorch loading/network timeouts
from langchain_core.embeddings import Embeddings

class SimpleMockEmbeddings(Embeddings):
    """
    A lightweight mock embeddings engine using basic word-overlap mapping.
    Avoids loading torch or tensorflow.
    """
    def embed_documents(self, texts):
        return [self.embed_query(text) for text in texts]

    def embed_query(self, text):
        # Generate a deterministic pseudo-embedding based on character counts
        import hashlib
        vector = [0.0] * 128
        words = text.lower().split()
        for word in words:
            # Hash each word to distribute weight across 128 dimensions
            h = int(hashlib.md5(word.encode('utf-8')).hexdigest(), 16)
            for idx in range(4):
                dim = (h >> (idx * 7)) % 128
                val = float((h >> (idx * 7 + 1)) % 100) / 100.0
                vector[dim] += val
        
        # Normalize vector
        magnitude = sum(x*x for x in vector) ** 0.5
        if magnitude > 0:
            vector = [x / magnitude for x in vector]
        return vector

def generate_cover_letter(resume_text, job_desc, company_name):
    """
    Generates a personalized cover letter using Gemini based on resume, job description, and company name.
    """
    system_instruction = (
        "You are an expert career consultant. Write a professional, polite, and persuasive cover letter "
        "matching the candidate's skills/experience to the job description and company goals. "
        "The tone should be natural, modern, and engaging (not overly formal or cliché)."
    )
    prompt = (
        f"Write a cover letter for {company_name}.\n\n"
        f"--- Candidate Resume / Profile Info ---\n{resume_text}\n\n"
        f"--- Job Description / Requirements ---\n{job_desc}\n\n"
        f"Provide ONLY the plain text content of the letter. Do not add markdown code blocks or wrapper text."
    )
    
    if is_ai_available():
        try:
            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                system_instruction=system_instruction
            )
            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            logger.error(f"Gemini Cover Letter Error: {e}")
            
    # Fallback mock letter
    return (
        f"Hiring Committee\n"
        f"{company_name}\n\n"
        f"Dear Hiring Committee,\n\n"
        f"I am writing to express my enthusiastic interest in joining {company_name}. "
        f"With my technical background and hands-on skills, I am confident that I can make a meaningful contribution to your engineering goals.\n\n"
        f"My profile align well with the skills requested in your job posting, specifically regarding core technical systems. "
        f"I am particularly drawn to {company_name}'s culture of excellence and would welcome the chance to apply my skills to your initiatives.\n\n"
        f"Thank you for your time and consideration. I look forward to discussing how my experience can help your team succeed.\n\n"
        f"Sincerely,\n"
        f"AI Career Assistant User"
    )

