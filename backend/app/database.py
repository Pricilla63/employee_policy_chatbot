from motor.motor_asyncio import AsyncIOMotorClient
from app.config import get_settings
import os

settings = get_settings()

# Async MongoDB client for FastAPI
class MongoDB:
    client: AsyncIOMotorClient = None
    
mongodb = MongoDB()

async def connect_to_mongo():
    """Connect to MongoDB on startup"""
    mongodb.client = AsyncIOMotorClient(settings.MONGODB_URL)
    print("✅ Connected to MongoDB")
    
    # Ensure uploads folder exists
    uploads_dir = "./uploads"
    os.makedirs(uploads_dir, exist_ok=True)
    print(f"✅ Uploads folder ready: {uploads_dir}")

async def close_mongo_connection():
    """Close MongoDB connection on shutdown"""
    mongodb.client.close()
    print("❌ Closed MongoDB connection")

def get_database():
    """Get MongoDB database"""
    return mongodb.client[settings.DATABASE_NAME]

# Collections - ONLY FOR METADATA
def get_users_collection():
    db = get_database()
    return db.users

def get_qa_history_collection():
    db = get_database()
    return db.qa_history

def get_conversations_collection():
    db = get_database()
    return db.conversations

# NEW FUNCTION: Get documents directly from uploads folder
def get_documents_from_uploads():
    """Get all document files directly from uploads folder"""
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
        print(f"📁 Found {len(documents)} files in uploads folder")
    else:
        print(f"❌ Uploads folder not found: {uploads_dir}")
    
    return documents