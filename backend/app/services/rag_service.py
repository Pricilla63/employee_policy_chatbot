import os
import uuid
import time
import httpx
from typing import List, Dict, Tuple
from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document
from app.utils.embeddings import get_embeddings, chunk_text
from app.config import get_settings

settings = get_settings()

class RAGService:
    def __init__(self):
        self.embeddings = get_embeddings()
        self.model_name = settings.GROQ_MODEL  # This will now be "llama-3.1-8b-instant"
        
        # Only initialize Groq if API key is provided
        if settings.GROQ_API_KEY and settings.GROQ_API_KEY.strip():
            try:
                from groq import Groq
                
                # Create httpx client with timeout and proxy support
                http_client = httpx.Client(
                    timeout=30.0,
                    verify=False,  # Disable SSL verification for corporate proxies
                )
                
                self.groq_client = Groq(
                    api_key=settings.GROQ_API_KEY,
                    http_client=http_client
                )
                print(f"✅ Groq client initialized with model: {self.model_name}")
            except Exception as e:
                self.groq_client = None
                print(f"⚠️  Warning: Failed to initialize Groq client: {e}")
        else:
            self.groq_client = None
            print("⚠️  Warning: GROQ_API_KEY not set. Q&A functionality will be limited.")
        
    def create_vector_store(self, text: str, document_id: str) -> Tuple[str, int]:
        """Create FAISS vector store from text chunks"""
        chunks = chunk_text(text)
        
        if not chunks:
            raise ValueError("No text chunks created from document")
        
        # Create documents
        documents = [Document(page_content=chunk, metadata={"doc_id": document_id}) 
                    for chunk in chunks]
        
        # Create FAISS index
        vector_store = FAISS.from_documents(documents, self.embeddings)
        
        # Save vector store
        vector_store_id = str(uuid.uuid4())
        store_path = os.path.join(settings.VECTOR_STORE_PATH, vector_store_id)
        os.makedirs(settings.VECTOR_STORE_PATH, exist_ok=True)
        vector_store.save_local(store_path)
        
        return vector_store_id, len(chunks)
    
    def load_vector_store(self, vector_store_id: str) -> FAISS:
        """Load FAISS vector store - compatible with multiple versions"""
        store_path = os.path.join(settings.VECTOR_STORE_PATH, vector_store_id)
        
        # Try with newer API first
        try:
            return FAISS.load_local(
                store_path, 
                self.embeddings, 
                allow_dangerous_deserialization=True
            )
        except TypeError:
            # Fall back to older API
            return FAISS.load_local(store_path, self.embeddings)
    
    def retrieve_context(self, vector_store_id: str, query: str, k: int = 4) -> List[str]:
        """Retrieve relevant chunks from vector store"""
        try:
            vector_store = self.load_vector_store(vector_store_id)
            docs = vector_store.similarity_search(query, k=k)
            return [doc.page_content for doc in docs]
        except Exception as e:
            print(f"Error in retrieve_context for {vector_store_id}: {e}")
            return []
    
    def generate_answer(self, query: str, context: List[str]) -> Dict:
        """Generate answer using Groq AI with retry logic"""
        if not self.groq_client:
            return {
                "answer": self._fallback_answer(query, context),
                "response_time": 0,
                "tokens_used": 0,
                "model_used": "fallback"
            }
        
        start_time = time.time()
        context_text = "\n\n".join(context)
        
        prompt = f"""You are a helpful HR assistant for LoanDNA. Answer the employee's question based on the company policy documents.

Context from company documents:
{context_text}

Question: {query}

Instructions: 
- Provide a clear, professional answer based on the context
- If the answer is not in the context, say "I don't have information about this in the available policy documents. Please contact HR at hr@loandna.com"
- Be concise but complete
- Format your response in a professional manner

Answer:"""
        
        # Retry logic for connection errors
        max_retries = 3
        for attempt in range(max_retries):
            try:
                chat_completion = self.groq_client.chat.completions.create(
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a helpful HR assistant for LoanDNA that answers employee questions based on company policy documents. Be professional, accurate, and helpful."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    model=self.model_name,  # Now uses "llama-3.1-8b-instant"
                    temperature=0.3,
                    max_tokens=1024,
                )
                
                end_time = time.time()
                response_time = end_time - start_time
                
                return {
                    "answer": chat_completion.choices[0].message.content,
                    "response_time": response_time,
                    "tokens_used": chat_completion.usage.total_tokens if hasattr(chat_completion, 'usage') else None,
                    "model_used": self.model_name
                }
                
            except Exception as e:
                print(f"Groq API attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(1)  # Wait before retry
                else:
                    # All retries failed, return fallback
                    return {
                        "answer": self._fallback_answer(query, context),
                        "response_time": 0,
                        "tokens_used": 0,
                        "model_used": "fallback"
                    }
    
    def _fallback_answer(self, query: str, context: List[str]) -> str:
        """Fallback answer when Groq API is unavailable"""
        context_text = "\n\n---\n\n".join(context[:3])
        
        return f"""⚠️ AI service temporarily unavailable. Here are the relevant sections from the policy documents:

{context_text}

📧 For detailed clarification, please contact HR at hr@loandna.com"""
    
    def query_documents(self, vector_store_ids: List[str], query: str) -> dict:
        """Query multiple documents and generate answer"""
        all_contexts = []
        
        for vs_id in vector_store_ids:
            try:
                contexts = self.retrieve_context(vs_id, query, k=3)
                all_contexts.extend(contexts)
            except Exception as e:
                print(f"Error retrieving from {vs_id}: {e}")
        
        if not all_contexts:
            return {
                "answer": "❌ No relevant information found in the policy documents.\n\n📧 Please contact HR at hr@loandna.com for assistance.",
                "sources": [],
                "response_time": 0,
                "tokens_used": 0,
                "model_used": "none"
            }
        
        result = self.generate_answer(query, all_contexts)
        result["sources"] = all_contexts[:3]
        
        return result