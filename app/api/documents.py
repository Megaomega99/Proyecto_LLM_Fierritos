# app/api/documents.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
import os
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
    try:
        # Procesar documento y generar resumen
        content, file_path, summary = await DocumentProcessor.process_document(file)
        
        document = Document(
            title=file.filename,
            content=content,
            file_path=file_path,
            summary=summary,
            owner_id=current_user_id
        )
        
        db.add(document)
        db.commit()
        db.refresh(document)
        return document
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al procesar el documento: {str(e)}"
        )

@router.get("/documents", response_model=List[DocumentSchema])
async def get_documents(
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    documents = db.query(Document).filter(Document.owner_id == current_user_id).all()
    return documents

@router.delete("/documents/{document_id}")
async def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.owner_id == current_user_id
    ).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    try:
        # Delete the physical file if it exists
        if document.file_path and os.path.exists(document.file_path):
            os.remove(document.file_path)
        
        # Delete from database
        db.delete(document)
        db.commit()
        
        return {"message": "Document deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting document: {str(e)}"
        )

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