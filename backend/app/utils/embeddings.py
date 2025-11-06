# from sentence_transformers import SentenceTransformer
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain_community.vectorstores import FAISS
# from langchain_core.embeddings import Embeddings
# from langchain.schema import Document
# from typing import List
# import numpy as np
# from app.config import get_settings

# settings = get_settings()

# class CustomEmbeddings(Embeddings):
#     def __init__(self, model_name: str):
#         try:
#             self.model = SentenceTransformer(model_name)
#             print(f"✅ Loaded embedding model: {model_name}")
#         except Exception as e:
#             print(f"❌ Failed to load embedding model: {e}")
#             raise
    
#     def embed_documents(self, texts: List[str]) -> List[List[float]]:
#         try:
#             if not texts:
#                 return []
#             embeddings = self.model.encode(texts, normalize_embeddings=True)
#             return embeddings.tolist()
#         except Exception as e:
#             print(f"❌ Error embedding documents: {e}")
#             return []
    
#     def embed_query(self, text: str) -> List[float]:
#         try:
#             if not text:
#                 return [0.0] * 384  # Default dimension for all-MiniLM-L6-v2
#             embedding = self.model.encode([text], normalize_embeddings=True)[0]
#             return embedding.tolist()
#         except Exception as e:
#             print(f"❌ Error embedding query: {e}")
#             return [0.0] * 384

# def get_embeddings():
#     """Get embeddings instance with error handling"""
#     try:
#         return CustomEmbeddings(settings.EMBEDDING_MODEL)
#     except Exception as e:
#         print(f"❌ Critical: Failed to initialize embeddings: {e}")
#         # Fallback to a simpler approach if needed
#         raise

# def chunk_text(text: str) -> List[str]:
#     """Split text into chunks with proper error handling"""
#     if not text or not text.strip():
#         return []
    
#     try:
#         text_splitter = RecursiveCharacterTextSplitter(
#             chunk_size=settings.CHUNK_SIZE,
#             chunk_overlap=settings.CHUNK_OVERLAP,
#             length_function=len,
#             separators=["\n\n", "\n", ". ", "! ", "? ", " ", ""]  # Added separators for better splitting
#         )
        
#         # For single texts, use split_text
#         chunks = text_splitter.split_text(text)
        
#         # Filter out empty chunks
#         chunks = [chunk.strip() for chunk in chunks if chunk.strip()]
        
#         print(f"📄 Created {len(chunks)} chunks from text (length: {len(text)})")
#         return chunks
        
#     except Exception as e:
#         print(f"❌ Error chunking text: {e}")
#         # Fallback: simple split by sentences
#         import re
#         sentences = re.split(r'[.!?]+', text)
#         return [s.strip() for s in sentences if s.strip() and len(s.strip()) > 50]

# def create_documents_from_chunks(chunks: List[str], metadata: dict = None) -> List[Document]:
#     """Create LangChain Document objects from text chunks"""
#     if metadata is None:
#         metadata = {}
    
#     return [
#         Document(page_content=chunk, metadata=metadata)
#         for chunk in chunks
#     ]


from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.embeddings import Embeddings
from langchain.schema import Document
from typing import List
import numpy as np
import re
from app.config import get_settings
import os

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
        raise

def load_faiss_vector_store(store_path: str, embeddings):
    """Load FAISS vector store with version compatibility"""
    try:
        # Try with newer API first
        try:
            return FAISS.load_local(
                store_path, 
                embeddings, 
                allow_dangerous_deserialization=True
            )
        except TypeError:
            # Fall back to older API without the parameter
            print("ℹ️ Using older FAISS API (no allow_dangerous_deserialization parameter)")
            return FAISS.load_local(store_path, embeddings)
        except Exception as e:
            print(f"❌ Error with standard FAISS loading: {e}")
            # Try alternative loading method
            try:
                return FAISS.load_local(store_path, embeddings, allow_dangerous_deserialization=False)
            except:
                return FAISS.load_local(store_path, embeddings)
    except Exception as e:
        print(f"❌ Error loading FAISS vector store from {store_path}: {e}")
        raise

def chunk_text(text: str) -> List[str]:
    """Split text into chunks with better preservation of context for policy documents"""
    if not text or not text.strip():
        return []
    
    try:
        # Use more conservative chunking for policy documents
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,  # Smaller chunks for better precision
            chunk_overlap=100,  # More overlap to preserve context
            length_function=len,
            separators=["\n\n", "\n", ". ", "! ", "? ", " ", ""]
        )
        
        chunks = text_splitter.split_text(text)
        
        # Filter and clean chunks
        cleaned_chunks = []
        for chunk in chunks:
            chunk = chunk.strip()
            if chunk and len(chunk) > 50:  # Remove very short chunks
                # Further clean the chunk
                chunk = re.sub(r'\s+', ' ', chunk)  # Normalize whitespace
                cleaned_chunks.append(chunk)
        
        print(f"📄 Created {len(cleaned_chunks)} cleaned chunks from text (length: {len(text)})")
        return cleaned_chunks
        
    except Exception as e:
        print(f"❌ Error chunking text: {e}")
        # Fallback: split by paragraphs and sentences
        paragraphs = text.split('\n\n')
        meaningful_chunks = []
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if paragraph and len(paragraph) > 100:
                # If paragraph is too long, split by sentences
                if len(paragraph) > 800:
                    sentences = re.split(r'[.!?]+', paragraph)
                    current_chunk = ""
                    for sentence in sentences:
                        sentence = sentence.strip()
                        if sentence:
                            if len(current_chunk) + len(sentence) < 600:
                                if current_chunk:
                                    current_chunk += ". " + sentence
                                else:
                                    current_chunk = sentence
                            else:
                                if current_chunk:
                                    meaningful_chunks.append(current_chunk)
                                current_chunk = sentence
                    if current_chunk:
                        meaningful_chunks.append(current_chunk)
                else:
                    meaningful_chunks.append(paragraph)
        
        print(f"📄 Created {len(meaningful_chunks)} fallback chunks from text")
        return meaningful_chunks

def create_documents_from_chunks(chunks: List[str], metadata: dict = None) -> List[Document]:
    """Create LangChain Document objects from text chunks with enhanced metadata"""
    if metadata is None:
        metadata = {}
    
    documents = []
    for i, chunk in enumerate(chunks):
        # Enhance metadata with chunk information
        chunk_metadata = metadata.copy()
        chunk_metadata.update({
            "chunk_id": i,
            "chunk_count": len(chunks),
            "content_preview": chunk[:100] + "..." if len(chunk) > 100 else chunk
        })
        documents.append(Document(page_content=chunk, metadata=chunk_metadata))
    
    return documents

def create_faiss_index(documents: List[Document], embeddings, index_path: str):
    """Create and save FAISS index with error handling"""
    try:
        # Create FAISS index from documents
        vector_store = FAISS.from_documents(documents, embeddings)
        
        # Save the index
        vector_store.save_local(index_path)
        print(f"✅ FAISS index saved to: {index_path}")
        return vector_store
        
    except Exception as e:
        print(f"❌ Error creating FAISS index: {e}")
        raise

def semantic_search(query: str, vector_store, k: int = 5, score_threshold: float = 0.7):
    """Perform semantic search with score filtering"""
    try:
        # Get documents with similarity scores
        docs_with_scores = vector_store.similarity_search_with_score(query, k=k*2)
        
        # Filter by score threshold
        filtered_docs = []
        for doc, score in docs_with_scores:
            if score <= score_threshold:
                filtered_docs.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "score": score
                })
        
        # Sort by score (lower is better)
        filtered_docs.sort(key=lambda x: x["score"])
        
        return filtered_docs[:k]
        
    except Exception as e:
        print(f"❌ Error in semantic search: {e}")
        return []

# Utility function to check if FAISS index exists
def faiss_index_exists(index_path: str) -> bool:
    """Check if FAISS index files exist"""
    required_files = [
        os.path.join(index_path, "index.faiss"),
        os.path.join(index_path, "index.pkl")
    ]
    return all(os.path.exists(f) for f in required_files)