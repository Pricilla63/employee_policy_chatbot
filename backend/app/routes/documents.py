from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query
from typing import List
from datetime import datetime, timezone
from bson import ObjectId
import os
import shutil
from app.database import get_documents_from_uploads
from app.models import DocumentResponse
from app.services.document_service import DocumentService
from app.routes.auth import get_current_user

router = APIRouter(prefix="/documents", tags=["Documents"])
document_service = DocumentService()

@router.get("/from-folder")
async def get_documents_from_folder():
    """Get all documents directly from uploads folder (for testing)"""
    try:
        documents = get_documents_from_uploads()
        return {
            "folder_path": "./uploads",
            "document_count": len(documents),
            "documents": documents
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """Upload a document to uploads folder"""
    try:
        documents_collection = get_documents_from_uploads()
        
        # 1. Save the actual file to uploads folder
        file_path = await document_service.save_uploaded_file(file)
        
        # 2. Extract file metadata from ACTUAL file
        file_metadata = document_service.get_file_metadata(file_path)
        
        # 3. Handle versioning based on ACTUAL file timestamps and content
        previous_version_id, new_version, is_new_version = await document_service.handle_document_versioning(
            filename=file.filename,
            content_hash=file_metadata["content_hash"],
            file_modified_at=file_metadata["file_modified_at"]
        )
        
        # 4. Process document if it's a new version
        if is_new_version:
            vector_store_id, chunk_count, _ = await document_service.process_document(file_path)
        else:
            # For existing version, we still need to create metadata entry
            vector_store_id = f"existing_{file_metadata['content_hash'][:16]}"
            chunk_count = 0
        
        # 5. Create metadata entry in database
        document_dict = {
            "filename": f"{file.filename} (v{new_version})" if is_new_version else file.filename,
            "original_filename": file.filename,
            "file_path": file_path,
            "file_type": file_metadata["file_extension"],
            "file_size": file_metadata["file_size"],
            "vector_store_id": vector_store_id,
            "owner_id": "system",  # All documents owned by system
            "is_shared": True,     # All documents are shared for all users
            "chunk_count": chunk_count,
            "uploaded_at": datetime.now(timezone.utc),
            "file_modified_at": file_metadata["file_modified_at"],
            "file_created_at": file_metadata["file_created_at"],
            "version": new_version,
            "is_latest": True,
            "is_active": True,
            "previous_version_id": previous_version_id,
            "content_hash": file_metadata["content_hash"],
            "metadata": {
                "uploaded_by": current_user["username"],
                "upload_method": "api_upload"
            }
        }
        
        result = await documents_collection.insert_one(document_dict)
        document_dict["_id"] = str(result.inserted_id)
        
        print(f"✅ Uploaded document: {file.filename} v{new_version}")
        return document_dict
        
    except HTTPException:
        raise
    except Exception as e:
        # Clean up file if there was an error
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[DocumentResponse])
async def get_all_documents(current_user: dict = Depends(get_current_user)):
    """Get ALL documents from database metadata"""
    documents_collection = get_documents_from_uploads()
    
    # Get only LATEST versions of active documents
    cursor = documents_collection.find({
        "is_latest": True,
        "is_active": True
    }).sort("file_modified_at", -1)
    
    documents = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        
        # Verify file actually exists in uploads folder
        if os.path.exists(doc["file_path"]):
            documents.append(doc)
        else:
            print(f"⚠️ Document in DB but missing in uploads: {doc['filename']}")
    
    return documents

@router.post("/sync-existing")
async def sync_existing_files(current_user: dict = Depends(get_current_user)):
    """Sync existing files from uploads folder to database"""
    try:
        synced_files = await document_service.scan_existing_files()
        return {
            "message": f"Synced {len(synced_files)} files from uploads folder",
            "synced_files": synced_files
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/file/{document_id}")
async def get_document_file(
    document_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get the actual file content"""
    documents_collection = get_documents_from_uploads()
    
    document = await documents_collection.find_one({
        "_id": ObjectId(document_id),
        "is_active": True
    })
    
    if not document or not os.path.exists(document["file_path"]):
        raise HTTPException(status_code=404, detail="File not found")
    
    # Return file content
    from fastapi.responses import FileResponse
    return FileResponse(
        document["file_path"],
        filename=document["original_filename"],
        media_type='application/octet-stream'
    )

@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a document (soft delete)"""
    documents_collection = get_documents_from_uploads()
    
    # Soft delete - mark as inactive
    result = await documents_collection.update_one(
        {
            "_id": ObjectId(document_id)
        },
        {
            "$set": {
                "is_active": False,
                "is_latest": False,
                "modified_at": datetime.now(timezone.utc)
            }
        }
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return {"message": "Document deleted successfully"}

@router.get("/{document_id}/versions")
async def get_document_versions(
    document_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get version history of a document"""
    documents_collection = get_documents_from_uploads()
    
    # Get the current document
    current_doc = await documents_collection.find_one({
        "_id": ObjectId(document_id),
        "is_active": True
    })
    
    if not current_doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Find all versions of this document
    cursor = documents_collection.find({
        "original_filename": current_doc["original_filename"],
        "is_active": True
    }).sort("version", -1)
    
    versions = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        versions.append(doc)
    
    return versions

@router.get("/stats")
async def get_document_stats(current_user: dict = Depends(get_current_user)):
    """Get document statistics"""
    documents_collection = get_documents_from_uploads()
    
    # Get total stats for latest active documents
    pipeline = [
        {
            "$match": {
                "is_latest": True,
                "is_active": True
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
        "total_chunks": stats["total_chunks"],
        "total_size": stats["total_size"],
        "file_types": file_type_count
    }

@router.post("/process-all")
async def process_all_documents(current_user: dict = Depends(get_current_user)):
    """Process all documents in uploads folder to create vector stores"""
    try:
        processed_docs = await document_service.process_existing_documents()
        return {
            "message": f"Processed {len(processed_docs)} documents",
            "processed_documents": processed_docs
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/processed")
async def get_processed_documents(current_user: dict = Depends(get_current_user)):
    """Get all processed documents with vector stores"""
    try:
        processed_docs = await document_service.get_processed_documents()
        return {
            "processed_count": len(processed_docs),
            "documents": processed_docs
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))