# Updated RAGService with version-aware metadata injection into LLM
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
                    "version": doc.get("version", 1),
                    "file_modified_at": doc.get("file_modified_at"),
                })
                relevant_chunks.append(c)

        relevant_chunks.sort(key=lambda x: (x["score"], x.get("file_modified_at", "")), reverse=False)

        context_text = ""
        all_dates = []
        for c in relevant_chunks[:6]:
            text = c["content"]
            dates = self.extract_dates(text)
            all_dates.extend(dates)
            context_text += f"""
[Document: {c['filename']}, Version: {c['version']}, Modified: {c.get('file_modified_at')}, Score: {c['score']:.4f}]
{text}
"""

        all_dates = list(dict.fromkeys(all_dates))
        detected_dates = ", ".join(all_dates) if all_dates else "None detected"

        prompt = f"""
You are a strict policy assistant. Use ONLY the context below.
Always choose information from the latest Modified version.
If older text conflicts with newer text, ignore older text.
If unsure, say you cannot confirm from policy.

Detected Dates: {detected_dates}

CONTEXT:
{context_text}

Question: {query}
Answer in bullet points with the version and date reference.
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
            messages=[{"role": "system", "content": "You answer only using context"},{"role": "user", "content": prompt}],
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