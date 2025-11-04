from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.embeddings import Embeddings
from langchain.schema import Document
from typing import List
import numpy as np
from app.config import get_settings

settings = get_settings()

class CustomEmbeddings(Embeddings):
    def __init__(self, model_name: str):
        try:
            self.model = SentenceTransformer(model_name)
            print(f"✅ Loaded embedding model: {model_name}")
        except Exception as e:
            print(f"❌ Failed to load embedding model: {e}")
            raise
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        try:
            if not texts:
                return []
            embeddings = self.model.encode(texts, normalize_embeddings=True)
            return embeddings.tolist()
        except Exception as e:
            print(f"❌ Error embedding documents: {e}")
            return []
    
    def embed_query(self, text: str) -> List[float]:
        try:
            if not text:
                return [0.0] * 384  # Default dimension for all-MiniLM-L6-v2
            embedding = self.model.encode([text], normalize_embeddings=True)[0]
            return embedding.tolist()
        except Exception as e:
            print(f"❌ Error embedding query: {e}")
            return [0.0] * 384

def get_embeddings():
    """Get embeddings instance with error handling"""
    try:
        return CustomEmbeddings(settings.EMBEDDING_MODEL)
    except Exception as e:
        print(f"❌ Critical: Failed to initialize embeddings: {e}")
        # Fallback to a simpler approach if needed
        raise

def chunk_text(text: str) -> List[str]:
    """Split text into chunks with proper error handling"""
    if not text or not text.strip():
        return []
    
    try:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            length_function=len,
            separators=["\n\n", "\n", ". ", "! ", "? ", " ", ""]  # Added separators for better splitting
        )
        
        # For single texts, use split_text
        chunks = text_splitter.split_text(text)
        
        # Filter out empty chunks
        chunks = [chunk.strip() for chunk in chunks if chunk.strip()]
        
        print(f"📄 Created {len(chunks)} chunks from text (length: {len(text)})")
        return chunks
        
    except Exception as e:
        print(f"❌ Error chunking text: {e}")
        # Fallback: simple split by sentences
        import re
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip() and len(s.strip()) > 50]

def create_documents_from_chunks(chunks: List[str], metadata: dict = None) -> List[Document]:
    """Create LangChain Document objects from text chunks"""
    if metadata is None:
        metadata = {}
    
    return [
        Document(page_content=chunk, metadata=metadata)
        for chunk in chunks
    ]