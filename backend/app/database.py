from motor.motor_asyncio import AsyncIOMotorClient
from app.config import get_settings

settings = get_settings()

# Async MongoDB client for FastAPI
class MongoDB:
    client: AsyncIOMotorClient = None
    
mongodb = MongoDB()

async def connect_to_mongo():
    """Connect to MongoDB on startup"""
    mongodb.client = AsyncIOMotorClient(settings.MONGODB_URL)
    print("✅ Connected to MongoDB")

async def close_mongo_connection():
    """Close MongoDB connection on shutdown"""
    mongodb.client.close()
    print("❌ Closed MongoDB connection")

def get_database():
    """Get MongoDB database"""
    return mongodb.client[settings.DATABASE_NAME]

# Collections
def get_users_collection():
    db = get_database()
    return db.users

def get_documents_collection():
    db = get_database()
    return db.documents

def get_qa_history_collection():
    db = get_database()
    return db.qa_history

def get_conversations_collection():
    db = get_database()
    return db.conversations