from fastapi import APIRouter, Depends, Query, HTTPException
from typing import List, Optional
from datetime import datetime, timedelta
from bson import ObjectId
from app.database import get_qa_history_collection, get_documents_from_uploads
from app.models.conversation import QAHistoryResponse, ConversationStats
from app.routes.auth import get_current_user

router = APIRouter(prefix="/history", tags=["History"])

@router.get("/", response_model=List[QAHistoryResponse])
async def get_qa_history(
    limit: int = Query(50, ge=1, le=100),
    skip: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user)
):
    """Get user's Q&A history"""
    qa_history_collection = get_qa_history_collection()
    
    cursor = qa_history_collection.find(
        {"user_id": current_user["_id"]}
    ).sort("timestamp", -1).skip(skip).limit(limit)
    
    history = []
    async for record in cursor:
        record["_id"] = str(record["_id"])
        
        # Ensure timestamp field exists, if not set a default
        if "timestamp" not in record:
            record["timestamp"] = datetime.now()
        
        history.append(record)
    
    return history

@router.get("/stats", response_model=ConversationStats)
async def get_conversation_stats(current_user: dict = Depends(get_current_user)):
    """Get user's conversation statistics"""
    qa_history_collection = get_qa_history_collection()
    documents_collection = get_documents_from_uploads()
    
    # Total questions
    total_questions = await qa_history_collection.count_documents(
        {"user_id": current_user["_id"]}
    )
    
    # Total documents
    total_documents = await documents_collection.count_documents(
        {"owner_id": current_user["_id"]}
    )
    
    # Average response time
    pipeline = [
        {"$match": {"user_id": current_user["_id"]}},
        {"$group": {
            "_id": None,
            "avg_response_time": {"$avg": "$response_time"}
        }}
    ]
    
    avg_result = await qa_history_collection.aggregate(pipeline).to_list(1)
    avg_response_time = avg_result[0]["avg_response_time"] if avg_result else 0
    
    # Most queried documents
    pipeline = [
        {"$match": {"user_id": current_user["_id"]}},
        {"$unwind": "$document_names"},
        {"$group": {
            "_id": "$document_names",
            "count": {"$sum": 1}
        }},
        {"$sort": {"count": -1}},
        {"$limit": 5}
    ]
    
    most_queried = await qa_history_collection.aggregate(pipeline).to_list(5)
    most_queried_documents = [
        {"document": item["_id"], "query_count": item["count"]}
        for item in most_queried
    ]
    
    # Recent activity (last 10)
    cursor = qa_history_collection.find(
        {"user_id": current_user["_id"]}
    ).sort("timestamp", -1).limit(10)
    
    recent_activity = []
    async for record in cursor:
        record["_id"] = str(record["_id"])
        # Ensure timestamp exists
        if "timestamp" not in record:
            record["timestamp"] = datetime.now()
        recent_activity.append(record)
    
    return {
        "total_questions": total_questions,
        "total_documents": total_documents,
        "average_response_time": round(avg_response_time, 2),
        "most_queried_documents": most_queried_documents,
        "recent_activity": recent_activity
    }

@router.get("/search")
async def search_history(
    q: str = Query(..., min_length=1),
    current_user: dict = Depends(get_current_user)
):
    """Search in Q&A history"""
    qa_history_collection = get_qa_history_collection()
    
    cursor = qa_history_collection.find({
        "user_id": current_user["_id"],
        "$or": [
            {"question": {"$regex": q, "$options": "i"}},
            {"answer": {"$regex": q, "$options": "i"}}
        ]
    }).sort("timestamp", -1).limit(20)
    
    results = []
    async for record in cursor:
        record["_id"] = str(record["_id"])
        # Ensure timestamp exists
        if "timestamp" not in record:
            record["timestamp"] = datetime.now()
        results.append(record)
    
    return results

@router.delete("/{history_id}")
async def delete_history_item(
    history_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a specific Q&A history item"""
    qa_history_collection = get_qa_history_collection()
    
    result = await qa_history_collection.delete_one({
        "_id": ObjectId(history_id),
        "user_id": current_user["_id"]
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="History item not found")
    
    return {"message": "History item deleted successfully"}

@router.delete("/")
async def clear_history(current_user: dict = Depends(get_current_user)):
    """Clear all Q&A history for current user"""
    qa_history_collection = get_qa_history_collection()
    
    result = await qa_history_collection.delete_many({
        "user_id": current_user["_id"]
    })
    
    return {
        "message": f"Deleted {result.deleted_count} history items"
    }