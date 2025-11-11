import os
import shutil
import hashlib
import json
from typing import List, Tuple, Optional, Dict, Any
from pathlib import Path
from fastapi import UploadFile, HTTPException
import PyPDF2
import docx
from datetime import datetime, timezone
from app.services.rag_service import RAGService
from app.config import get_settings

settings = get_settings()

class DocumentService:
    def __init__(self):
        self.rag_service = RAGService()
        self.upload_dir = "./uploads"
        self.vector_store_dir = "./vector_store"
        self.metadata_file = os.path.join(self.vector_store_dir, "document_metadata.json")
        os.makedirs(self.upload_dir, exist_ok=True)
        os.makedirs(self.vector_store_dir, exist_ok=True)
    
    def _load_metadata(self) -> Dict:
        """Load document metadata from file"""
        if os.path.exists(self.metadata_file):
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"❌ Error loading metadata: {e}")
                return {}
        return {}
    
    def _save_metadata(self, metadata: Dict):
        """Save document metadata to file"""
        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, default=str)
        except Exception as e:
            print(f"❌ Error saving metadata: {e}")
    
    def get_folder_structure(self, base_path: str = None) -> Dict:
        """Get complete folder structure recursively"""
        if base_path is None:
            base_path = self.upload_dir
        
        structure = {
            "path": base_path,
            "name": os.path.basename(base_path) or "uploads",
            "type": "folder",
            "children": []
        }
        
        try:
            for item in sorted(os.listdir(base_path)):
                if item.startswith('.'):
                    continue
                    
                item_path = os.path.join(base_path, item)
                
                if os.path.isdir(item_path):
                    structure["children"].append(self.get_folder_structure(item_path))
                else:
                    structure["children"].append({
                        "path": item_path,
                        "name": item,
                        "type": "file",
                        "size": os.path.getsize(item_path),
                        "extension": os.path.splitext(item)[1].lower()
                    })
        except Exception as e:
            print(f"⚠️ Error reading folder {base_path}: {e}")
        
        return structure
    
    def get_all_documents_recursive(self, base_path: str = None) -> List[Dict]:
        """Get all documents from all folders recursively"""
        if base_path is None:
            base_path = self.upload_dir
        
        documents = []
        
        try:
            for root, dirs, files in os.walk(base_path):
                # Filter out hidden directories
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                
                for file in files:
                    if file.startswith('.'):
                        continue
                    
                    file_path = os.path.join(root, file)
                    ext = os.path.splitext(file)[1].lower()
                    
                    if ext in ['.pdf', '.docx', '.doc', '.txt']:
                        relative_path = os.path.relpath(root, base_path)
                        folder_path = relative_path if relative_path != '.' else ''
                        
                        documents.append({
                            "filename": file,
                            "file_path": file_path,
                            "folder_path": folder_path,
                            "full_path": file_path,
                            "file_size": os.path.getsize(file_path),
                            "file_modified": os.path.getmtime(file_path),
                            "extension": ext
                        })
        except Exception as e:
            print(f"❌ Error scanning folders: {e}")
        
        return documents
    
    def extract_text_from_pdf_by_page(self, file_path: str) -> List[Dict]:
        """Extract text from PDF page by page"""
        pages = []
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                total_pages = len(pdf_reader.pages)
                
                for page_num in range(total_pages):
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    
                    if text.strip():
                        pages.append({
                            "page_number": page_num + 1,
                            "text": text,
                            "char_count": len(text)
                        })
                
                print(f"📄 Extracted {len(pages)} pages from PDF: {os.path.basename(file_path)}")
        except Exception as e:
            print(f"❌ Error extracting text from PDF {file_path}: {e}")
        
        return pages
    
    def extract_text_from_docx_by_page(self, file_path: str) -> List[Dict]:
        """Extract text from DOCX by paragraphs (simulated pages)"""
        pages = []
        try:
            doc = docx.Document(file_path)
            
            # Group paragraphs into approximate pages (every 500 words)
            current_page = []
            current_word_count = 0
            page_num = 1
            
            for paragraph in doc.paragraphs:
                text = paragraph.text.strip()
                if not text:
                    continue
                
                words = len(text.split())
                current_page.append(text)
                current_word_count += words
                
                # Create new page every ~500 words
                if current_word_count >= 500:
                    pages.append({
                        "page_number": page_num,
                        "text": "\n".join(current_page),
                        "char_count": sum(len(p) for p in current_page)
                    })
                    page_num += 1
                    current_page = []
                    current_word_count = 0
            
            # Add remaining content as last page
            if current_page:
                pages.append({
                    "page_number": page_num,
                    "text": "\n".join(current_page),
                    "char_count": sum(len(p) for p in current_page)
                })
            
            print(f"📄 Extracted {len(pages)} sections from DOCX: {os.path.basename(file_path)}")
        except Exception as e:
            print(f"❌ Error extracting text from DOCX {file_path}: {e}")
        
        return pages
    
    def calculate_content_hash(self, file_path: str) -> str:
        """Calculate MD5 hash of file content"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def get_file_timestamps(self, file_path: str) -> Tuple[datetime, datetime]:
        """Get actual file creation and modification timestamps"""
        try:
            stat = os.stat(file_path)
            modified_at = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)
            created_at = datetime.fromtimestamp(stat.st_ctime, tz=timezone.utc)
            return created_at, modified_at
        except Exception as e:
            print(f"⚠️ Could not get file timestamps: {e}")
            now = datetime.now(timezone.utc)
            return now, now
    
    def get_file_metadata(self, file_path: str, folder_path: str = "") -> Dict[str, Any]:
        """Extract comprehensive file metadata including folder info"""
        filename = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        created_at, modified_at = self.get_file_timestamps(file_path)
        content_hash = self.calculate_content_hash(file_path)
        
        return {
            "filename": filename,
            "folder_path": folder_path,
            "file_size": file_size,
            "file_created_at": created_at.isoformat(),
            "file_modified_at": modified_at.isoformat(),
            "content_hash": content_hash,
            "file_extension": filename.split('.')[-1].lower() if '.' in filename else '',
            "file_path": file_path,
        }
    
    async def process_document_by_pages(self, file_path: str, folder_path: str = "") -> Tuple[str, int, Dict[str, Any]]:
        """Process document page by page and create vector store"""
        
        file_metadata = self.get_file_metadata(file_path, folder_path)
        file_extension = file_metadata["file_extension"]
        
        # Extract pages based on file type
        pages = []
        if file_extension == 'pdf':
            pages = self.extract_text_from_pdf_by_page(file_path)
        elif file_extension in ['docx', 'doc']:
            pages = self.extract_text_from_docx_by_page(file_path)
        elif file_extension == 'txt':
            # For txt files, treat entire content as one page
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
                pages = [{"page_number": 1, "text": text, "char_count": len(text)}]
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")
        
        if not pages:
            raise ValueError("No text could be extracted from the document")
        
        # Create vector store with page-level metadata
        vector_store_id, chunk_count = self.rag_service.create_vector_store_from_pages(
            pages, 
            file_metadata["filename"],
            folder_path
        )
        
        return vector_store_id, chunk_count, file_metadata
    
    async def process_existing_documents(self) -> List[Dict]:
        """Process all documents in all folders recursively"""
        processed_docs = []
        
        # Get all documents recursively
        all_documents = self.get_all_documents_recursive()
        print(f"🔍 Found {len(all_documents)} documents in folder structure")
        
        for doc in all_documents:
            try:
                file_metadata = self.get_file_metadata(doc["file_path"], doc["folder_path"])
                metadata = self._load_metadata()
                
                # Create unique key combining folder path and filename
                document_key = os.path.join(doc["folder_path"], doc["filename"]) if doc["folder_path"] else doc["filename"]
                
                # Check if this version already exists
                content_exists = False
                if document_key in metadata:
                    for version in metadata[document_key]:
                        if version["file_metadata"]["content_hash"] == file_metadata["content_hash"]:
                            content_exists = True
                            print(f"ℹ️ Document unchanged: {document_key}")
                            break
                
                if not content_exists:
                    print(f"📄 Processing: {document_key}")
                    vector_store_id, chunk_count, processed_metadata = await self.process_document_by_pages(
                        doc["file_path"],
                        doc["folder_path"]
                    )
                    
                    # Update metadata
                    if document_key not in metadata:
                        metadata[document_key] = []
                    
                    version_entry = {
                        "vector_store_id": vector_store_id,
                        "file_metadata": file_metadata,
                        "chunk_count": chunk_count,
                        "processed_at": datetime.now(timezone.utc).isoformat(),
                        "version": len(metadata[document_key]) + 1,
                        "is_latest": True
                    }
                    
                    # Mark previous versions as not latest
                    for entry in metadata[document_key]:
                        entry["is_latest"] = False
                    
                    metadata[document_key].append(version_entry)
                    self._save_metadata(metadata)
                    
                    processed_docs.append({
                        "filename": doc["filename"],
                        "folder_path": doc["folder_path"],
                        "file_path": doc["file_path"],
                        "vector_store_id": vector_store_id,
                        "chunk_count": chunk_count,
                        "status": "processed"
                    })
                    print(f"✅ Processed: {document_key}")
                
            except Exception as e:
                print(f"❌ Error processing {doc['filename']}: {e}")
                processed_docs.append({
                    "filename": doc["filename"],
                    "folder_path": doc.get("folder_path", ""),
                    "error": str(e),
                    "status": "error"
                })
        
        return processed_docs
    
    async def get_processed_documents(self) -> List[Dict]:
        """Get all processed documents with folder information"""
        metadata = self._load_metadata()
        processed_docs = []
        
        for document_key, versions in metadata.items():
            if versions:
                latest_version = max(versions, key=lambda x: x["version"])
                
                processed_docs.append({
                    "filename": latest_version["file_metadata"]["filename"],
                    "folder_path": latest_version["file_metadata"].get("folder_path", ""),
                    "full_key": document_key,
                    "file_path": latest_version["file_metadata"]["file_path"],
                    "vector_store_id": latest_version["vector_store_id"],
                    "file_size": latest_version["file_metadata"]["file_size"],
                    "chunk_count": latest_version["chunk_count"],
                    "file_modified_at": latest_version["file_metadata"]["file_modified_at"],
                    "version": latest_version["version"],
                    "is_latest": latest_version["is_latest"],
                    "total_versions": len(versions)
                })
        
        return processed_docs
    
    def find_relevant_folders(self, query: str, folder_structure: Dict = None) -> List[str]:
        """Intelligently find relevant folders based on query"""
        if folder_structure is None:
            folder_structure = self.get_folder_structure()
        
        relevant_folders = []
        query_lower = query.lower()
        
        # Keywords to folder mapping (customize based on your needs)
        folder_keywords = {
            "policy": ["policy", "policies", "hr", "human resources"],
            "leave": ["leave", "vacation", "time-off", "pto"],
            "finance": ["finance", "financial", "accounting", "payroll"],
            "legal": ["legal", "contracts", "compliance"],
            "tech": ["technical", "technology", "it", "engineering"]
        }
        
        def search_folders(node, path=""):
            if node["type"] == "folder":
                folder_name = node["name"].lower()
                current_path = os.path.join(path, node["name"]) if path else node["name"]
                
                # Check if folder name matches query keywords
                for keyword_type, keywords in folder_keywords.items():
                    if any(kw in query_lower for kw in keywords):
                        if any(kw in folder_name for kw in keywords):
                            relevant_folders.append(current_path)
                            break
                
                # Recursively search children
                for child in node.get("children", []):
                    search_folders(child, current_path)
        
        search_folders(folder_structure)
        
        # If no specific folders found, return empty list (search all)
        return relevant_folders if relevant_folders else []
    
    async def save_uploaded_file(self, file: UploadFile, folder_path: str = "") -> str:
        """Save uploaded file to specific folder in uploads"""
        target_dir = os.path.join(self.upload_dir, folder_path) if folder_path else self.upload_dir
        os.makedirs(target_dir, exist_ok=True)
        
        file_path = os.path.join(target_dir, file.filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        print(f"✅ Saved file to: {file_path}")
        return file_path