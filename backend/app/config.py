from pydantic_settings import BaseSettings
from functools import lru_cache
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    # MongoDB
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "docqa_db"
    
    # Security - INCREASED TOKEN EXPIRY
    SECRET_KEY: str = "your-super-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # Increased from 30 to 1440 (24 hours)
    
    # Groq AI
    GROQ_API_KEY: str = ""
    
    # Vector Store
    VECTOR_STORE_PATH: str = "./vector_store"
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    
    # Embeddings
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # Groq Model - UPDATED to llama-3.1-8b-instant
    GROQ_MODEL: str = "llama-3.1-8b-instant"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"

@lru_cache()
def get_settings():
    return Settings()