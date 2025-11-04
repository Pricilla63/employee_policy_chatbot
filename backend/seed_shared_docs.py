import asyncio
import os
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from app.services.document_service import DocumentService
from app.utils.security import get_password_hash
from app.config import get_settings
from datetime import datetime, timezone


settings = get_settings()

async def seed_shared_documents():
    """Seed shared documents for all users"""
    
    print("=" * 70)
    print("🌍 Seeding SHARED Documents (Available to ALL Users)")
    print("=" * 70)
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.DATABASE_NAME]
    users_collection = db.users
    documents_collection = db.documents
    
    # Create or get system user for shared documents
    system_user = await users_collection.find_one({"username": "system"})
    
    if not system_user:
        print("\n📝 Creating system user for shared documents...")
        system_user_dict = {
            "email": "system@docuchat.ai",
            "username": "system",
            "hashed_password": get_password_hash("system_password_do_not_share"),
            "is_active": True,
            "created_at": datetime.now(timezone.utc)

        }
        result = await users_collection.insert_one(system_user_dict)
        system_user_id = str(result.inserted_id)
        print(f"✅ System user created")
    else:
        system_user_id = str(system_user["_id"])
        print(f"✅ Using existing system user")
    
    # Path to uploads folder
    uploads_folder = "./uploads"
    
    if not os.path.exists(uploads_folder):
        print(f"\n❌ Uploads folder not found: {uploads_folder}")
        client.close()
        return
    
    # Get all documents in folder
    supported_extensions = ('.pdf', '.docx', '.txt', '.doc')
    files = [f for f in os.listdir(uploads_folder) 
             if f.lower().endswith(supported_extensions)]
    
    if not files:
        print(f"\n⚠️  No documents found in {uploads_folder}")
        print(f"   Supported formats: {', '.join(supported_extensions)}")
        client.close()
        return
    
    print(f"\n📄 Found {len(files)} document(s) in uploads/:")
    for f in files:
        file_size = os.path.getsize(os.path.join(uploads_folder, f))
        print(f"   📎 {f} ({file_size / 1024:.1f} KB)")
    
    # Initialize document service
    doc_service = DocumentService()
    
    print("\n🔄 Processing shared documents...\n")
    
    processed = 0
    skipped = 0
    failed = 0
    
    for filename in files:
        file_path = os.path.join(uploads_folder, filename)
        
        # Check if already processed (check by filename and is_shared=True)
        existing = await documents_collection.find_one({
            "filename": filename,
            "is_shared": True
        })
        
        if existing:
            print(f"⏭️  {filename:<45} Already shared")
            skipped += 1
            continue
        
        try:
            print(f"🔄 {filename:<45} Processing...", end='', flush=True)
            
            # Extract text based on file type
            file_extension = filename.split('.')[-1].lower()
            
            if file_extension == 'pdf':
                text = doc_service.extract_text_from_pdf(file_path)
            elif file_extension in ['docx', 'doc']:
                text = doc_service.extract_text_from_docx(file_path)
            elif file_extension == 'txt':
                text = doc_service.extract_text_from_txt(file_path)
            else:
                print(f"\r❌ {filename:<45} Unsupported format")
                failed += 1
                continue
            
            # Get file size
            file_size = os.path.getsize(file_path)
            
            # Create vector store
            vector_store_id, chunk_count = doc_service.rag_service.create_vector_store(
                text, 
                "shared"  # Document ID for shared docs
            )
            
            # Save to database as SHARED document
            document_dict = {
                "filename": filename,
                "file_path": file_path,
                "file_type": file_extension,
                "file_size": file_size,
                "vector_store_id": vector_store_id,
                "owner_id": system_user_id,  # Owned by system
                "is_shared": True,  # ← SHARED FOR ALL USERS
                "chunk_count": chunk_count,
                "uploaded_at": datetime.now(timezone.utc)

            }
            
            await documents_collection.insert_one(document_dict)
            
            print(f"\r✅ {filename:<45} {chunk_count} chunks | 🌍 SHARED")
            processed += 1
            
        except Exception as e:
            print(f"\r❌ {filename:<45} Error: {str(e)[:30]}")
            failed += 1
    
    print("\n" + "=" * 70)
    print("📊 Summary:")
    print(f"   ✅ Processed: {processed}")
    print(f"   ⏭️  Skipped:   {skipped}")
    print(f"   ❌ Failed:    {failed}")
    print("=" * 70)
    
    if processed > 0:
        print("\n🎉 Shared documents successfully registered!")
        print("🌍 ALL users can now query these documents!")
        print(f"💬 Users can ask questions at http://localhost:3000")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(seed_shared_documents())