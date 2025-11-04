import os
import shutil
from typing import List, Tuple
from fastapi import UploadFile
import PyPDF2
import docx
from app.services.rag_service import RAGService
from app.config import get_settings

settings = get_settings()

class DocumentService:
    def __init__(self):
        self.rag_service = RAGService()
        self.upload_dir = "./uploads"
        os.makedirs(self.upload_dir, exist_ok=True)
    
    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF"""
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text()
        return text
    
    def extract_text_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX"""
        doc = docx.Document(file_path)
        return "\n".join([paragraph.text for paragraph in doc.paragraphs])
    
    def extract_text_from_txt(self, file_path: str) -> str:
        """Extract text from TXT"""
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    
    async def process_document(self, file: UploadFile, user_id: str) -> Tuple[str, str, int, int]:
        """Process uploaded document and create vector store"""
        # Save file
        file_path = os.path.join(self.upload_dir, f"{user_id}_{file.filename}")
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Get file size
        file_size = os.path.getsize(file_path)
        
        # Extract text based on file type
        file_extension = file.filename.split('.')[-1].lower()
        
        if file_extension == 'pdf':
            text = self.extract_text_from_pdf(file_path)
        elif file_extension in ['docx', 'doc']:
            text = self.extract_text_from_docx(file_path)
        elif file_extension == 'txt':
            text = self.extract_text_from_txt(file_path)
        else:
            raise ValueError("Unsupported file format")
        
        # Create vector store
        vector_store_id, chunk_count = self.rag_service.create_vector_store(text, user_id)
        
        return file_path, vector_store_id, file_size, chunk_count