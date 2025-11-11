import os
import uuid
import time
import httpx
import re
from typing import List, Dict, Tuple, Optional
from datetime import datetime
from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document
from app.utils.embeddings import get_embeddings, chunk_text
from app.config import get_settings

settings = get_settings()

class RAGService:
    def __init__(self):
        self.embeddings = get_embeddings()
        self.model_name = settings.GROQ_MODEL

        if settings.GROQ_API_KEY and settings.GROQ_API_KEY.strip():
            try:
                from groq import Groq
                http_client = httpx.Client(timeout=30.0, verify=False)
                self.groq_client = Groq(api_key=settings.GROQ_API_KEY, http_client=http_client)
                print(f"✅ Groq client initialized with model: {self.model_name}")
            except Exception as e:
                self.groq_client = None
                print(f"⚠️ Failed to initialize Groq client: {e}")
        else:
            self.groq_client = None
            print("⚠️ GROQ_API_KEY not set. Limited functionality.")

    def create_vector_store(self, text: str, document_name: str) -> Tuple[str, int]:
        chunks = chunk_text(text)
        documents = [Document(page_content=chunk, metadata={"document_name": document_name, "chunk_id": i, "chunk_count": len(chunks)}) for i, chunk in enumerate(chunks)]
        vector_store = FAISS.from_documents(documents, self.embeddings)
        vector_store_id = str(uuid.uuid4())
        store_path = os.path.join(settings.VECTOR_STORE_PATH, vector_store_id)
        os.makedirs(settings.VECTOR_STORE_PATH, exist_ok=True)
        vector_store.save_local(store_path)
        return vector_store_id, len(chunks)

    def create_vector_store_from_pages(self, pages: List[Dict], document_name: str, folder_path: str = "") -> Tuple[str, int]:
        """Create vector store from page-by-page extracted content"""
        documents = []
        total_chunks = 0
        
        for page in pages:
            page_text = page["text"]
            if not page_text.strip():
                continue
                
            # Chunk each page individually to maintain page context
            page_chunks = chunk_text(page_text)
            
            for i, chunk in enumerate(page_chunks):
                # Enhanced metadata with page and folder information
                metadata = {
                    "document_name": document_name,
                    "folder_path": folder_path,
                    "page_number": page["page_number"],
                    "chunk_id": i,
                    "total_page_chunks": len(page_chunks),
                    "char_count": page.get("char_count", 0),
                    "source_type": "page_chunk"
                }
                
                documents.append(Document(page_content=chunk, metadata=metadata))
                total_chunks += 1
        
        if not documents:
            raise ValueError("No valid content found in pages to create vector store")
        
        # Create vector store
        vector_store = FAISS.from_documents(documents, self.embeddings)
        vector_store_id = str(uuid.uuid4())
        store_path = os.path.join(settings.VECTOR_STORE_PATH, vector_store_id)
        os.makedirs(settings.VECTOR_STORE_PATH, exist_ok=True)
        vector_store.save_local(store_path)
        
        print(f"✅ Created vector store with {total_chunks} chunks from {len(pages)} pages for: {document_name}")
        return vector_store_id, total_chunks

    def load_vector_store(self, vector_store_id: str) -> FAISS:
        store_path = os.path.join(settings.VECTOR_STORE_PATH, vector_store_id)
        try:
            return FAISS.load_local(store_path, self.embeddings, allow_dangerous_deserialization=True)
        except Exception:
            return FAISS.load_local(store_path, self.embeddings)

    def search_related_content(self, vector_store_id: str, query: str, k: int = 5) -> List[Dict]:
        vector_store = self.load_vector_store(vector_store_id)
        docs_with_scores = vector_store.similarity_search_with_score(query, k=k*2)
        relevant = []
        for doc, score in docs_with_scores:
            relevant.append({"content": doc.page_content, "score": score, "metadata": doc.metadata})
        relevant.sort(key=lambda x: x["score"])
        return relevant[:k]

    def extract_dates(self, text: str) -> List[str]:
        patterns = [
            r"\b(?:\d{1,2}[/-]){2}\d{2,4}\b",
            r"\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b",
            r"\b\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*\s+\d{2,4}\b",
        ]
        found = []
        for p in patterns:
            found += re.findall(p, text, flags=re.IGNORECASE)
        seen = set(); out=[]
        for d in found:
            if d not in seen:
                seen.add(d); out.append(d)
        return out[:10]

    def query_documents_with_versions(self, query: str, documents: List[Dict], document_service) -> Dict:
        start = time.time()
        relevant_chunks = []
        
        for doc in documents:
            vs_id = doc.get("vector_store_id")
            if not vs_id:
                continue
            chunks = self.search_related_content(vs_id, query, k=4)
            for c in chunks:
                c.update({
                    "filename": doc["filename"],
                    "folder_path": doc.get("folder_path", ""),
                    "version": doc.get("version", 1),
                    "file_modified_at": doc.get("file_modified_at"),
                })
                relevant_chunks.append(c)

        # Sort by score and recency
        relevant_chunks.sort(key=lambda x: (x["score"], x.get("file_modified_at", "")), reverse=False)

        # Build context with enhanced folder information
        context_text = ""
        all_dates = []
        sources_metadata = []
        
        for c in relevant_chunks[:6]:
            text = c["content"]
            dates = self.extract_dates(text)
            all_dates.extend(dates)
            
            # Store enhanced metadata
            sources_metadata.append({
                "filename": c['filename'],
                "folder_path": c.get('folder_path', ''),
                "version": c['version'],
                "modified": c.get('file_modified_at', 'N/A'),
                "page_number": c.get('metadata', {}).get('page_number', 'N/A')
            })
            
            # Add context with folder information
            folder_info = f" in {c.get('folder_path', '')}" if c.get('folder_path') else ""
            context_text += f"""
[Document: {c['filename']}{folder_info}, Page: {c.get('metadata', {}).get('page_number', 'N/A')}]
{text}

"""

        all_dates = list(dict.fromkeys(all_dates))
        detected_dates = ", ".join(all_dates) if all_dates else "None detected"
        
        # Build metadata summary
        unique_sources = {}
        for meta in sources_metadata:
            key = f"{meta['filename']}_{meta['folder_path']}"
            if key not in unique_sources or meta['version'] > unique_sources[key]['version']:
                unique_sources[key] = meta
        
        sources_info = "\n".join([
            f"- {meta['filename']} (Folder: {meta['folder_path']}, Version: {meta['version']}, Page: {meta['page_number']})"
            for meta in unique_sources.values()
        ])

        prompt = f"""You are a strict policy assistant. Use ONLY the context below.
Always prioritize information from the most recent document versions.
Consider the folder structure for context relevance.
If older text conflicts with newer text, ignore older text.
If unsure, say you cannot confirm from the available policy documents.

Detected Dates: {detected_dates}

CONTEXT:
{context_text}

Question: {query}

Instructions:
1. Answer the question clearly using information from the context
2. Use bullet points for clarity  
3. Do NOT mention versions, document names, or dates in the main answer
4. Be concise and direct
5. After your answer, add a "Sources:" section listing the documents used with folder locations

Format your response EXACTLY like this:

[Your clear, direct answer here in bullet points]

**Sources:**
{sources_info}
"""

        if not self.groq_client:
            end = time.time()
            return {
                "answer": "Model unavailable",
                "sources": list({c['filename'] for c in relevant_chunks}),
                "dates_found": all_dates,
                "response_time": round(end - start, 3),
                "model_used": None
            }

        chat = self.groq_client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": "You are a precise policy assistant. Answer questions directly using only the provided context. Keep version and folder information for the Sources section at the end."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )

        end = time.time()
        answer = chat.choices[0].message.content
        
        return {
            "answer": answer,
            "sources": list({c['filename'] for c in relevant_chunks}),
            "dates_found": all_dates,
            "response_time": round(end - start, 3),
            "model_used": self.model_name
        }