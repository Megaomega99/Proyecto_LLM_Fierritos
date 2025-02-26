# app/api/documents.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.models.document import Document
from app.schemas.document import Document as DocumentSchema, DocumentCreate
from app.services.document_processor import DocumentProcessor
from app.services.llm_service import LLMService
from app.api.auth import get_current_user_id

router = APIRouter()

@router.post("/upload", response_model=DocumentSchema)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    content, file_path = await DocumentProcessor.process_document(file)
    
    document = Document(
        title=file.filename,
        content=content,
        file_path=file_path,
        owner_id=current_user_id
    )
    
    # Crear instancia de LLMService
    
    
    db.add(document)
    db.commit()
    db.refresh(document)
    return document

@router.get("/documents", response_model=List[DocumentSchema])
async def get_documents(
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    documents = db.query(Document).filter(Document.owner_id == current_user_id).all()
    return documents

@router.post("/ask/{document_id}")
async def ask_question(
    document_id: int,
    question: str,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.owner_id == current_user_id
    ).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Crear instancia de LLMService
    llm_service = LLMService()
    answer = await llm_service.answer_question(document.content, question)
    return {"answer": answer}