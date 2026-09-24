from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
import os
import shutil

from app.retrieval.hybrid_search import hybrid_search
from app.generation.context_builder import build_context
from app.generation.llm import generate_answer, rewrite_query
from app.ingestion.indexer import add_document_to_index, list_all_documents

from app.auth.auth import (
    authenticate_user, create_access_token, get_current_user, require_admin,
    list_all_users, add_user, update_user_departments, signup_user
)

from app.core.conversations import (
    get_user_conversations, get_conversation_messages,
    create_conversation, append_message, delete_conversation
)

app = FastAPI(title="Enterprise AI Knowledge Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


class QuestionRequest(BaseModel):
    question: str
    conversation_id: str | None = None


class AnswerResponse(BaseModel):
    answer: str
    sources: list[str]
    conversation_id: str


class SignupRequest(BaseModel):
    username: str
    password: str


class UserCreateRequest(BaseModel):
    username: str
    password: str
    role: str = "employee"
    departments: list[str]


class DepartmentsUpdateRequest(BaseModel):
    departments: list[str]


@app.get("/")
def health_check():
    return {"status": "ok", "message": "RAG API is running"}


@app.post("/signup")
def signup(payload: SignupRequest):
    success = signup_user(payload.username, payload.password)
    if not success:
        raise HTTPException(status_code=400, detail="Username already exists")
    return {"status": "created", "username": payload.username}


@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    token = create_access_token(data={"sub": user["username"]})
    return {
        "access_token": token,
        "token_type": "bearer",
        "role": user["role"],
        "departments": user["departments"]
    }


@app.get("/conversations")
def list_conversations(current_user: dict = Depends(get_current_user)):
    return get_user_conversations(current_user["username"])


@app.get("/conversations/{conversation_id}")
def get_conversation(conversation_id: str, current_user: dict = Depends(get_current_user)):
    messages = get_conversation_messages(current_user["username"], conversation_id)
    if messages is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"id": conversation_id, "messages": messages}


@app.delete("/conversations/{conversation_id}")
def remove_conversation(conversation_id: str, current_user: dict = Depends(get_current_user)):
    success = delete_conversation(current_user["username"], conversation_id)
    if not success:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"status": "deleted"}


@app.post("/ask", response_model=AnswerResponse)
def ask_question(
    request: QuestionRequest,
    current_user: dict = Depends(get_current_user)
):
    conversation_id = request.conversation_id
    if not conversation_id:
        conversation_id = create_conversation(current_user["username"])

    history = get_conversation_messages(current_user["username"], conversation_id) or []

    standalone_question = rewrite_query(request.question, history)

    retrieved_chunks = hybrid_search(
        standalone_question,
        top_k=4,
        allowed_departments=current_user["departments"]
    )

    if not retrieved_chunks:
        answer = "I couldn't find this information in the company documents."
    else:
        context = build_context(retrieved_chunks)
        answer = generate_answer(standalone_question, context)

    sources = list(set(chunk["source_file"] for chunk in retrieved_chunks))

    append_message(current_user["username"], conversation_id, "user", request.question)
    append_message(current_user["username"], conversation_id, "assistant", answer, sources=sources)

    return AnswerResponse(answer=answer, sources=sources, conversation_id=conversation_id)


# =========================================================
# ADMIN ENDPOINTS
# =========================================================

@app.post("/admin/upload")
def admin_upload(
    file: UploadFile = File(...),
    department: str = Form(...),
    current_user: dict = Depends(require_admin)
):
    save_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(save_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    chunk_count, dept = add_document_to_index(save_path, department_override=department)
    return {"filename": file.filename, "department": dept, "chunks_added": chunk_count}


@app.get("/admin/documents")
def admin_list_documents(current_user: dict = Depends(require_admin)):
    return list_all_documents()


@app.get("/admin/users")
def admin_list_users(current_user: dict = Depends(require_admin)):
    return list_all_users()


@app.post("/admin/users")
def admin_add_user(payload: UserCreateRequest, current_user: dict = Depends(require_admin)):
    success = add_user(payload.username, payload.password, payload.role, payload.departments)
    if not success:
        raise HTTPException(status_code=400, detail="Username already exists")
    return {"status": "created", "username": payload.username}


@app.put("/admin/users/{username}/departments")
def admin_update_departments(
    username: str,
    payload: DepartmentsUpdateRequest,
    current_user: dict = Depends(require_admin)
):
    success = update_user_departments(username, payload.departments)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"status": "updated", "username": username, "departments": payload.departments}