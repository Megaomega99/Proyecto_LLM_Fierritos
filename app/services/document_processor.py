# app/services/document_processor.py
from .celery_config import celery_app
import os
from typing import Optional
from fastapi import UploadFile
import PyPDF2
import docx
import markdown

class DocumentProcessor:
    @staticmethod
    async def process_document(file: UploadFile) -> tuple[str, str]:
        content = ""
        file_path = f"uploads/{file.filename}"
        os.makedirs("uploads", exist_ok=True)
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        if file.filename.endswith('.pdf'):
            content = DocumentProcessor._process_pdf(file_path)
        elif file.filename.endswith('.docx'):
            content = DocumentProcessor._process_docx(file_path)
        elif file.filename.endswith('.md'):
            content = DocumentProcessor._process_markdown(file_path)
        elif file.filename.endswith('.txt'):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
        process_document_task.delay(file_path, content)
        return content, file_path

    @staticmethod
    def _process_pdf(file_path: str) -> str:
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text()
        return text

    @staticmethod
    def _process_docx(file_path: str) -> str:
        doc = docx.Document(file_path)
        return " ".join([paragraph.text for paragraph in doc.paragraphs])

    @staticmethod
    def _process_markdown(file_path: str) -> str:
        with open(file_path, 'r', encoding='utf-8') as file:
            return markdown.markdown(file.read())

@celery_app.task
def process_document_task(file_path: str, content: str):
    try:
        chunks = [content[i:i+1000] for i in range(0, len(content), 1000)]
        print(f"Processing document: {file_path}, chunks: {len(chunks)}")
    except Exception as e:
        print(f"Error processing document: {str(e)}")