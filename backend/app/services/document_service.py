
# import os
# import shutil
# import hashlib
# from typing import List, Tuple, Optional, Dict, Any
# from fastapi import UploadFile, HTTPException
# import PyPDF2
# import docx
# from datetime import datetime, timezone
# from app.services.rag_service import RAGService
# from app.config import get_settings

# settings = get_settings()

# class DocumentService:
#     def __init__(self):
#         self.rag_service = RAGService()
#         self.upload_dir = "./uploads"
#         self.vector_store_dir = "./vector_store"
#         os.makedirs(self.upload_dir, exist_ok=True)
#         os.makedirs(self.vector_store_dir, exist_ok=True)
    
#     def get_file_timestamps(self, file_path: str) -> Tuple[datetime, datetime]:
#         """Get actual file creation and modification timestamps from OS"""
#         try:
#             stat = os.stat(file_path)
#             modified_at = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)
#             created_at = datetime.fromtimestamp(stat.st_ctime, tz=timezone.utc)
#             return created_at, modified_at
#         except Exception as e:
#             print(f"⚠️ Could not get file timestamps: {e}")
#             now = datetime.now(timezone.utc)
#             return now, now
    
#     def calculate_content_hash(self, file_path: str) -> str:
#         """Calculate MD5 hash of file content"""
#         hash_md5 = hashlib.md5()
#         with open(file_path, "rb") as f:
#             for chunk in iter(lambda: f.read(4096), b""):
#                 hash_md5.update(chunk)
#         return hash_md5.hexdigest()
    
#     def extract_text_from_pdf(self, file_path: str) -> str:
#         """Extract text from PDF"""
#         try:
#             text = ""
#             with open(file_path, 'rb') as file:
#                 pdf_reader = PyPDF2.PdfReader(file)
#                 for page in pdf_reader.pages:
#                     text += page.extract_text()
#             return text
#         except Exception as e:
#             print(f"❌ Error extracting text from PDF {file_path}: {e}")
#             return ""
    
#     def extract_text_from_docx(self, file_path: str) -> str:
#         """Extract text from DOCX"""
#         try:
#             doc = docx.Document(file_path)
#             return "\n".join([paragraph.text for paragraph in doc.paragraphs])
#         except Exception as e:
#             print(f"❌ Error extracting text from DOCX {file_path}: {e}")
#             return ""
    
#     def extract_text_from_txt(self, file_path: str) -> str:
#         """Extract text from TXT"""
#         try:
#             with open(file_path, 'r', encoding='utf-8') as file:
#                 return file.read()
#         except Exception as e:
#             print(f"❌ Error extracting text from TXT {file_path}: {e}")
#             return ""
    
#     def get_file_metadata(self, file_path: str) -> Dict[str, Any]:
#         """Extract comprehensive file metadata"""
#         filename = os.path.basename(file_path)
#         file_size = os.path.getsize(file_path)
#         created_at, modified_at = self.get_file_timestamps(file_path)
#         content_hash = self.calculate_content_hash(file_path)
        
#         return {
#             "filename": filename,
#             "file_size": file_size,
#             "file_created_at": created_at,
#             "file_modified_at": modified_at,
#             "content_hash": content_hash,
#             "file_extension": filename.split('.')[-1].lower() if '.' in filename else '',
#             "file_path": file_path,
#         }
    
#     async def save_uploaded_file(self, file: UploadFile) -> str:
#         """Save uploaded file to uploads folder and return file path"""
#         # Save file directly to uploads folder
#         file_path = os.path.join(self.upload_dir, file.filename)
        
#         with open(file_path, "wb") as buffer:
#             shutil.copyfileobj(file.file, buffer)
        
#         print(f"✅ Saved file to: {file_path}")
#         return file_path
    
#     async def process_document(self, file_path: str) -> Tuple[str, int, Dict[str, Any]]:
#         """Process document and create vector store"""
        
#         # Extract file metadata
#         file_metadata = self.get_file_metadata(file_path)
        
#         # Extract text based on file type
#         file_extension = file_metadata["file_extension"]
        
#         text = ""
#         if file_extension == 'pdf':
#             text = self.extract_text_from_pdf(file_path)
#         elif file_extension in ['docx', 'doc']:
#             text = self.extract_text_from_docx(file_path)
#         elif file_extension == 'txt':
#             text = self.extract_text_from_txt(file_path)
#         else:
#             raise ValueError(f"Unsupported file format: {file_extension}")
        
#         if not text.strip():
#             raise ValueError("No text could be extracted from the document")
        
#         # Create vector store (use "common" as owner_id for all documents)
#         vector_store_id, chunk_count = self.rag_service.create_vector_store(text, "common")
        
#         return vector_store_id, chunk_count, file_metadata
    
#     def get_available_documents(self):
#         """Get all documents directly from uploads folder"""
#         uploads_dir = "./uploads"
#         documents = []
        
#         if os.path.exists(uploads_dir):
#             for filename in os.listdir(uploads_dir):
#                 file_path = os.path.join(uploads_dir, filename)
#                 if os.path.isfile(file_path) and not filename.startswith('.'):
#                     documents.append({
#                         "filename": filename,
#                         "file_path": file_path,
#                         "file_size": os.path.getsize(file_path),
#                         "file_modified": os.path.getmtime(file_path)
#                     })
        
#         return documents

#     async def process_existing_documents(self):
#         """Process all existing documents in uploads folder and return processed documents info"""
#         processed_docs = []
        
#         # Get all PDF files from uploads
#         all_documents = self.get_available_documents()
#         pdf_documents = [doc for doc in all_documents if doc['filename'].lower().endswith('.pdf')]
        
#         print(f"📁 Found {len(pdf_documents)} PDF documents to process")
        
#         for doc in pdf_documents:
#             try:
#                 # Check if vector store already exists for this file
#                 file_hash = self.calculate_content_hash(doc["file_path"])
#                 vector_store_path = os.path.join(self.vector_store_dir, f"{file_hash}_vector_store")
                
#                 if os.path.exists(vector_store_path):
#                     print(f"ℹ️ Vector store already exists for: {doc['filename']}")
#                     # Get existing vector store info
#                     processed_docs.append({
#                         "filename": doc["filename"],
#                         "file_path": doc["file_path"],
#                         "vector_store_id": file_hash,  # Use file hash as vector store ID
#                         "file_size": doc["file_size"],
#                         "chunk_count": 0,  # We don't store this info in file system
#                         "status": "already_processed"
#                     })
#                 else:
#                     print(f"🔄 Processing document: {doc['filename']}")
#                     # Process the document
#                     vector_store_id, chunk_count, file_metadata = await self.process_document(doc["file_path"])
                    
#                     processed_docs.append({
#                         "filename": doc["filename"],
#                         "file_path": doc["file_path"],
#                         "vector_store_id": vector_store_id,
#                         "file_size": doc["file_size"],
#                         "chunk_count": chunk_count,
#                         "status": "processed"
#                     })
#                     print(f"✅ Processed existing document: {doc['filename']} -> {vector_store_id}")
                
#             except Exception as e:
#                 print(f"❌ Error processing document {doc['filename']}: {e}")
#                 processed_docs.append({
#                     "filename": doc["filename"],
#                     "file_path": doc["file_path"],
#                     "error": str(e),
#                     "status": "error"
#                 })
        
#         print(f"🎯 Total documents processed: {len([d for d in processed_docs if d['status'] in ['processed', 'already_processed']])}")
#         return processed_docs

#     async def get_processed_documents(self):
#         """Get all documents that have been processed and have vector stores"""
#         processed_docs = []
        
#         # Get all documents from uploads folder
#         all_documents = self.get_available_documents()
        
#         for doc in all_documents:
#             try:
#                 # Check if vector store exists for this file
#                 file_hash = self.calculate_content_hash(doc["file_path"])
#                 vector_store_path = os.path.join(self.vector_store_dir, f"{file_hash}_vector_store")
                
#                 # Also check for any vector store directories that might exist
#                 vector_store_exists = os.path.exists(vector_store_path)
                
#                 # If the specific hash path doesn't exist, check if any vector store contains this file
#                 if not vector_store_exists:
#                     # Look for any vector store that might be associated with this file
#                     for vs_dir in os.listdir(self.vector_store_dir):
#                         vs_path = os.path.join(self.vector_store_dir, vs_dir)
#                         if os.path.isdir(vs_path):
#                             # Check if this vector store was created from our file
#                             # We'll assume it's processed if vector store directory exists
#                             vector_store_exists = True
#                             file_hash = vs_dir  # Use the directory name as vector store ID
#                             break
                
#                 if vector_store_exists:
#                     processed_docs.append({
#                         "filename": doc["filename"],
#                         "file_path": doc["file_path"],
#                         "vector_store_id": file_hash,
#                         "file_size": doc["file_size"],
#                         "chunk_count": 0,  # We don't store this in file system
#                         "status": "processed"
#                     })
                
#             except Exception as e:
#                 print(f"❌ Error checking processed status for {doc['filename']}: {e}")
        
#         print(f"📊 Found {len(processed_docs)} processed documents in file system")
#         return processed_docs

#     def get_vector_store_ids_for_documents(self, filenames: List[str] = None) -> List[str]:
#         """Get vector store IDs for specific documents or all documents"""
#         processed_docs = []
        
#         # Get processed documents
#         all_processed = self.get_processed_documents()
        
#         if filenames:
#             # Filter for specific filenames
#             processed_docs = [doc for doc in all_processed if doc['filename'] in filenames]
#         else:
#             processed_docs = all_processed
        
#         # Extract vector store IDs
#         vector_store_ids = [doc['vector_store_id'] for doc in processed_docs]
        
#         print(f"🔑 Found {len(vector_store_ids)} vector store IDs for querying")
#         return vector_store_ids


import os
import shutil
import hashlib
import json
from typing import List, Tuple, Optional, Dict, Any
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
    
    def get_file_timestamps(self, file_path: str) -> Tuple[datetime, datetime]:
        """Get actual file creation and modification timestamps from OS"""
        try:
            stat = os.stat(file_path)
            modified_at = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)
            created_at = datetime.fromtimestamp(stat.st_ctime, tz=timezone.utc)
            return created_at, modified_at
        except Exception as e:
            print(f"⚠️ Could not get file timestamps: {e}")
            now = datetime.now(timezone.utc)
            return now, now
    
    def calculate_content_hash(self, file_path: str) -> str:
        """Calculate MD5 hash of file content"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF"""
        try:
            text = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text()
            return text
        except Exception as e:
            print(f"❌ Error extracting text from PDF {file_path}: {e}")
            return ""
    
    def extract_text_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX"""
        try:
            doc = docx.Document(file_path)
            return "\n".join([paragraph.text for paragraph in doc.paragraphs])
        except Exception as e:
            print(f"❌ Error extracting text from DOCX {file_path}: {e}")
            return ""
    
    def extract_text_from_txt(self, file_path: str) -> str:
        """Extract text from TXT"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            print(f"❌ Error extracting text from TXT {file_path}: {e}")
            return ""
    
    def get_file_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract comprehensive file metadata"""
        filename = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        created_at, modified_at = self.get_file_timestamps(file_path)
        content_hash = self.calculate_content_hash(file_path)
        
        return {
            "filename": filename,
            "file_size": file_size,
            "file_created_at": created_at.isoformat(),
            "file_modified_at": modified_at.isoformat(),
            "content_hash": content_hash,
            "file_extension": filename.split('.')[-1].lower() if '.' in filename else '',
            "file_path": file_path,
        }
    
    async def save_uploaded_file(self, file: UploadFile) -> str:
        """Save uploaded file to uploads folder and return file path"""
        file_path = os.path.join(self.upload_dir, file.filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        print(f"✅ Saved file to: {file_path}")
        return file_path
    
    async def process_document(self, file_path: str) -> Tuple[str, int, Dict[str, Any]]:
        """Process document and create vector store with version tracking"""
        
        # Extract file metadata
        file_metadata = self.get_file_metadata(file_path)
        
        # Extract text based on file type
        file_extension = file_metadata["file_extension"]
        
        text = ""
        if file_extension == 'pdf':
            text = self.extract_text_from_pdf(file_path)
        elif file_extension in ['docx', 'doc']:
            text = self.extract_text_from_docx(file_path)
        elif file_extension == 'txt':
            text = self.extract_text_from_txt(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")
        
        if not text.strip():
            raise ValueError("No text could be extracted from the document")
        
        # Create vector store
        vector_store_id, chunk_count = self.rag_service.create_vector_store(text, file_metadata["filename"])
        
        # Update metadata
        metadata = self._load_metadata()
        document_key = file_metadata["filename"]
        
        if document_key not in metadata:
            metadata[document_key] = []
        
        # Add new version entry
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
        
        return vector_store_id, chunk_count, file_metadata
    
    def get_available_documents(self):
        """Get all documents directly from uploads folder"""
        uploads_dir = "./uploads"
        documents = []
        
        if os.path.exists(uploads_dir):
            for filename in os.listdir(uploads_dir):
                file_path = os.path.join(uploads_dir, filename)
                if os.path.isfile(file_path) and not filename.startswith('.'):
                    documents.append({
                        "filename": filename,
                        "file_path": file_path,
                        "file_size": os.path.getsize(file_path),
                        "file_modified": os.path.getmtime(file_path)
                    })
        
        return documents

    async def process_existing_documents(self):
        """Process all existing documents in uploads folder with version tracking"""
        processed_docs = []
        
        # Get all PDF files from uploads
        all_documents = self.get_available_documents()
        pdf_documents = [doc for doc in all_documents if doc['filename'].lower().endswith('.pdf')]
        
        print(f"📁 Found {len(pdf_documents)} PDF documents to process")
        
        for doc in pdf_documents:
            try:
                # Check if already processed by comparing content hash
                file_metadata = self.get_file_metadata(doc["file_path"])
                metadata = self._load_metadata()
                document_key = doc["filename"]
                
                # Check if this exact content already exists
                content_exists = False
                if document_key in metadata:
                    for version in metadata[document_key]:
                        if version["file_metadata"]["content_hash"] == file_metadata["content_hash"]:
                            content_exists = True
                            print(f"ℹ️ Document content unchanged: {doc['filename']}")
                            break
                
                if not content_exists:
                    print(f"🔄 Processing document: {doc['filename']}")
                    vector_store_id, chunk_count, processed_metadata = await self.process_document(doc["file_path"])
                    
                    processed_docs.append({
                        "filename": doc["filename"],
                        "file_path": doc["file_path"],
                        "vector_store_id": vector_store_id,
                        "file_size": doc["file_size"],
                        "chunk_count": chunk_count,
                        "status": "processed",
                        "version": len(metadata.get(document_key, [])) if document_key in metadata else 1
                    })
                    print(f"✅ Processed document: {doc['filename']} -> {vector_store_id}")
                else:
                    print(f"ℹ️ Document already processed: {doc['filename']}")
                    processed_docs.append({
                        "filename": doc["filename"],
                        "file_path": doc["file_path"],
                        "status": "already_processed"
                    })
                
            except Exception as e:
                print(f"❌ Error processing document {doc['filename']}: {e}")
                processed_docs.append({
                    "filename": doc["filename"],
                    "file_path": doc["file_path"],
                    "error": str(e),
                    "status": "error"
                })
        
        print(f"🎯 Total documents processed: {len([d for d in processed_docs if d['status'] in ['processed', 'already_processed']])}")
        return processed_docs

    async def get_processed_documents(self):
        """Get all documents that have been processed with version information"""
        metadata = self._load_metadata()
        processed_docs = []
        
        for filename, versions in metadata.items():
            if versions:
                # Get the latest version
                latest_version = max(versions, key=lambda x: x["version"])
                
                processed_docs.append({
                    "filename": filename,
                    "file_path": latest_version["file_metadata"]["file_path"],
                    "vector_store_id": latest_version["vector_store_id"],
                    "file_size": latest_version["file_metadata"]["file_size"],
                    "chunk_count": latest_version["chunk_count"],
                    "file_modified_at": latest_version["file_metadata"]["file_modified_at"],
                    "version": latest_version["version"],
                    "is_latest": latest_version["is_latest"],
                    "total_versions": len(versions)
                })
        
        print(f"📊 Found {len(processed_docs)} processed documents with version info")
        return processed_docs

    def get_document_versions(self, filename: str) -> List[Dict]:
        """Get all versions of a specific document"""
        metadata = self._load_metadata()
        return metadata.get(filename, [])

    def get_latest_vector_store_id(self, filename: str) -> Optional[str]:
        """Get the vector store ID for the latest version of a document"""
        versions = self.get_document_versions(filename)
        if versions:
            latest = max(versions, key=lambda x: x["version"])
            return latest["vector_store_id"]
        return None

    def find_related_documents(self, query: str, documents: List[Dict]) -> List[Dict]:
        """Find documents related to the query using semantic search"""
        # This will be enhanced in the RAG service
        # For now, return all documents
        return documents