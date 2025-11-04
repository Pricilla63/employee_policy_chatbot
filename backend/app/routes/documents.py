from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from typing import List
from datetime import datetime, timezone
from bson import ObjectId
from app.database import get_documents_collection
from app.models.document import DocumentResponse, DocumentCreate
from app.services.document_service import DocumentService
from app.routes.auth import get_current_user

router = APIRouter(prefix="/documents", tags=["Documents"])
document_service = DocumentService()

@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """Upload a document (private to user)"""
    try:
        documents_collection = get_documents_collection()
        
        file_path, vector_store_id, file_size, chunk_count = await document_service.process_document(
            file, 
            current_user["_id"]
        )
        
        document_dict = {
            "filename": file.filename,
            "file_path": file_path,
            "file_type": file.filename.split('.')[-1].lower(),
            "file_size": file_size,
            "vector_store_id": vector_store_id,
            "owner_id": current_user["_id"],
            "is_shared": False,  # Private document
            "chunk_count": chunk_count,
            "uploaded_at": datetime.now(timezone.utc)
        }
        
        result = await documents_collection.insert_one(document_dict)
        document_dict["_id"] = str(result.inserted_id)
        
        return document_dict
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload-shared", response_model=DocumentResponse)
async def upload_shared_document(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """Upload a shared document (available to all users)"""
    # Optional: Add admin check
    # if current_user.get("role") != "admin":
    #     raise HTTPException(status_code=403, detail="Only admins can upload shared documents")
    
    try:
        documents_collection = get_documents_collection()
        
        file_path, vector_store_id, file_size, chunk_count = await document_service.process_document(
            file, 
            "shared"
        )
        
        document_dict = {
            "filename": file.filename,
            "file_path": file_path,
            "file_type": file.filename.split('.')[-1].lower(),
            "file_size": file_size,
            "vector_store_id": vector_store_id,
            "owner_id": current_user["_id"],
            "is_shared": True,  # Shared document
            "chunk_count": chunk_count,
            "uploaded_at": datetime.now(timezone.utc)
        }
        
        result = await documents_collection.insert_one(document_dict)
        document_dict["_id"] = str(result.inserted_id)
        
        return document_dict
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[DocumentResponse])
async def get_user_documents(current_user: dict = Depends(get_current_user)):
    """Get all documents accessible to the user (shared + own private documents)"""
    documents_collection = get_documents_collection()
    
    # Get shared documents OR user's own documents
    cursor = documents_collection.find({
        "$or": [
            {"is_shared": True},  # Shared documents available to all
            {"owner_id": current_user["_id"]}  # User's private documents
        ]
    })
    
    documents = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        documents.append(doc)
    
    return documents

@router.get("/shared", response_model=List[DocumentResponse])
async def get_shared_documents(current_user: dict = Depends(get_current_user)):
    """Get only shared documents"""
    documents_collection = get_documents_collection()
    
    cursor = documents_collection.find({"is_shared": True})
    
    documents = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        documents.append(doc)
    
    return documents

@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a document (only if user owns it)"""
    documents_collection = get_documents_collection()
    
    # Only allow deletion if user owns the document
    result = await documents_collection.delete_one({
        "_id": ObjectId(document_id),
        "owner_id": current_user["_id"]
    })
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=404, 
            detail="Document not found or you don't have permission to delete it"
        )
    
    return {"message": "Document deleted successfully"}

@router.get("/stats")
async def get_document_stats(current_user: dict = Depends(get_current_user)):
    """Get document statistics"""
    documents_collection = get_documents_collection()
    
    # Count shared documents
    shared_count = await documents_collection.count_documents({"is_shared": True})
    
    # Count user's private documents
    private_count = await documents_collection.count_documents({
        "owner_id": current_user["_id"],
        "is_shared": False
    })
    
    # Get total stats for accessible documents
    pipeline = [
        {
            "$match": {
                "$or": [
                    {"is_shared": True},
                    {"owner_id": current_user["_id"]}
                ]
            }
        },
        {
            "$group": {
                "_id": None,
                "total_documents": {"$sum": 1},
                "total_chunks": {"$sum": "$chunk_count"},
                "total_size": {"$sum": "$file_size"},
                "file_types": {"$push": "$file_type"}
            }
        }
    ]
    
    result = await documents_collection.aggregate(pipeline).to_list(1)
    
    if not result:
        return {
            "total_documents": 0,
            "shared_documents": 0,
            "private_documents": 0,
            "total_chunks": 0,
            "total_size": 0,
            "file_types": {}
        }
    
    stats = result[0]
    
    # Count file types
    file_type_count = {}
    for ft in stats["file_types"]:
        file_type_count[ft] = file_type_count.get(ft, 0) + 1
    
    return {
        "total_documents": stats["total_documents"],
        "shared_documents": shared_count,
        "private_documents": private_count,
        "total_chunks": stats["total_chunks"],
        "total_size": stats["total_size"],
        "file_types": file_type_count
    }