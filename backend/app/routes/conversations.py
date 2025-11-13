# from fastapi import APIRouter, Depends, HTTPException, Query
# from typing import List, Optional
# from bson import ObjectId
# from app.database import get_conversations_collection, get_qa_history_collection, get_documents_from_uploads
# from app.models.conversation import ConversationResponse, ConversationStats
# from app.services.conversation_service import ConversationService
# from app.routes.auth import get_current_user

# router = APIRouter(prefix="/conversations", tags=["Conversations"])
# conversation_service = ConversationService()

# @router.get("/", response_model=List[ConversationResponse])
# async def get_conversations(
#     limit: int = Query(20, ge=1, le=100),
#     skip: int = Query(0, ge=0),
#     current_user: dict = Depends(get_current_user)
# ):
#     """Get user's conversations"""
#     conversations = await conversation_service.get_user_conversations(
#         current_user["_id"], limit, skip
#     )
#     return conversations

# @router.get("/active", response_model=Optional[ConversationResponse])
# async def get_active_conversation(current_user: dict = Depends(get_current_user)):
#     """Get user's active conversation"""
#     conversation = await conversation_service.get_active_conversation(current_user["_id"])
#     return conversation

# @router.get("/{conversation_id}")
# async def get_conversation(
#     conversation_id: str,
#     current_user: dict = Depends(get_current_user)
# ):
#     """Get specific conversation with all messages"""
#     try:
#         conversation = await conversation_service.get_conversation(conversation_id, current_user["_id"])
#         if not conversation:
#             raise HTTPException(status_code=404, detail="Conversation not found")
        
#         # Make sure the response includes all necessary fields
#         return {
#             "_id": conversation["_id"],
#             "user_id": conversation["user_id"],
#             "title": conversation["title"],
#             "messages": conversation.get("messages", []),
#             "document_ids": conversation.get("document_ids", []),
#             "is_active": conversation.get("is_active", True),
#             "message_count": conversation.get("message_count", 0),
#             "created_at": conversation["created_at"],
#             "updated_at": conversation["updated_at"],
#             "last_activity": conversation["last_activity"]
#         }
#     except Exception as e:
#         print(f"Error getting conversation: {e}")
#         raise HTTPException(status_code=500, detail=f"Error retrieving conversation: {str(e)}")

# @router.post("/new")
# async def start_new_conversation(current_user: dict = Depends(get_current_user)):
#     """Explicitly start a new conversation (like clicking 'New Chat')"""
#     # This just deactivates all current conversations
#     # The next question will automatically create a new one
#     await conversation_service.deactivate_all_conversations(current_user["_id"])
#     return {"message": "Ready for new conversation"}

# @router.delete("/{conversation_id}")
# async def delete_conversation(
#     conversation_id: str,
#     current_user: dict = Depends(get_current_user)
# ):
#     """Delete a conversation"""
#     success = await conversation_service.delete_conversation(conversation_id, current_user["_id"])
#     if not success:
#         raise HTTPException(status_code=404, detail="Conversation not found")
#     return {"message": "Conversation deleted successfully"}

# @router.get("/stats/overview", response_model=ConversationStats)
# async def get_conversation_stats(current_user: dict = Depends(get_current_user)):
#     """Get conversation statistics"""
#     # Get collections INSIDE the async function
#     qa_history_collection = get_qa_history_collection()
#     documents_collection = get_documents_from_uploads()
    
#     # Get conversation stats
#     conv_stats = await conversation_service.get_conversation_stats(current_user["_id"])
    
#     # Total questions from QA history
#     total_questions = await qa_history_collection.count_documents(
#         {"user_id": current_user["_id"]}
#     )
    
#     # Total documents
#     total_documents = await documents_collection.count_documents(
#         {"owner_id": current_user["_id"]}
#     )
    
#     # Average response time
#     pipeline = [
#         {"$match": {"user_id": current_user["_id"]}},
#         {"$group": {
#             "_id": None,
#             "avg_response_time": {"$avg": "$response_time"}
#         }}
#     ]
    
#     avg_result = await qa_history_collection.aggregate(pipeline).to_list(1)
#     avg_response_time = avg_result[0]["avg_response_time"] if avg_result else 0
    
#     # Most queried documents
#     pipeline = [
#         {"$match": {"user_id": current_user["_id"]}},
#         {"$unwind": "$document_names"},
#         {"$group": {
#             "_id": "$document_names",
#             "count": {"$sum": 1}
#         }},
#         {"$sort": {"count": -1}},
#         {"$limit": 5}
#     ]
    
#     most_queried = await qa_history_collection.aggregate(pipeline).to_list(5)
#     most_queried_documents = [
#         {"document": item["_id"], "query_count": item["count"]}
#         for item in most_queried
#     ]
    
#     # Recent conversations
#     recent_conversations = await conversation_service.get_user_conversations(
#         current_user["_id"], limit=5
#     )
    
#     return {
#         "total_conversations": conv_stats["total_conversations"],
#         "total_questions": total_questions,
#         "total_documents": total_documents,
#         "average_response_time": round(avg_response_time, 2),
#         "most_queried_documents": most_queried_documents,
#         "recent_conversations": recent_conversations
#     }






from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from bson import ObjectId
from app.database import get_conversations_collection, get_qa_history_collection, get_documents_from_uploads
from app.models.conversation import ConversationResponse, ConversationStats
from app.services.conversation_service import ConversationService
from app.routes.auth import get_current_user

router = APIRouter(prefix="/conversations", tags=["Conversations"])
conversation_service = ConversationService()

@router.get("", response_model=List[ConversationResponse])  # Removed trailing slash
async def get_conversations(
    limit: int = Query(20, ge=1, le=100),
    skip: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user)
):
    """Get user's conversations"""
    conversations = await conversation_service.get_user_conversations(
        current_user["_id"], limit, skip
    )
    return conversations

@router.get("/active", response_model=Optional[ConversationResponse])
async def get_active_conversation(current_user: dict = Depends(get_current_user)):
    """Get user's active conversation"""
    conversation = await conversation_service.get_active_conversation(current_user["_id"])
    return conversation

@router.get("/{conversation_id}")
async def get_conversation(
    conversation_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get specific conversation with all messages"""
    try:
        conversation = await conversation_service.get_conversation(conversation_id, current_user["_id"])
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        # Make sure the response includes all necessary fields
        return {
            "_id": conversation["_id"],
            "user_id": conversation["user_id"],
            "title": conversation["title"],
            "messages": conversation.get("messages", []),
            "document_ids": conversation.get("document_ids", []),
            "is_active": conversation.get("is_active", True),
            "message_count": conversation.get("message_count", 0),
            "created_at": conversation["created_at"],
            "updated_at": conversation["updated_at"],
            "last_activity": conversation["last_activity"]
        }
    except Exception as e:
        print(f"Error getting conversation: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving conversation: {str(e)}")

@router.post("/new")
async def start_new_conversation(current_user: dict = Depends(get_current_user)):
    """Explicitly start a new conversation (like clicking 'New Chat')"""
    # This just deactivates all current conversations
    # The next question will automatically create a new one
    await conversation_service.deactivate_all_conversations(current_user["_id"])
    return {"message": "Ready for new conversation"}

@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a conversation"""
    success = await conversation_service.delete_conversation(conversation_id, current_user["_id"])
    if not success:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"message": "Conversation deleted successfully"}

@router.get("/stats/overview", response_model=ConversationStats)
async def get_conversation_stats(current_user: dict = Depends(get_current_user)):
    """Get conversation statistics"""
    # Get collections INSIDE the async function
    qa_history_collection = get_qa_history_collection()
    documents_collection = get_documents_from_uploads()
    
    # Get conversation stats
    conv_stats = await conversation_service.get_conversation_stats(current_user["_id"])
    
    # Total questions from QA history
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
    
    # Recent conversations
    recent_conversations = await conversation_service.get_user_conversations(
        current_user["_id"], limit=5
    )
    
    return {
        "total_conversations": conv_stats["total_conversations"],
        "total_questions": total_questions,
        "total_documents": total_documents,
        "average_response_time": round(avg_response_time, 2),
        "most_queried_documents": most_queried_documents,
        "recent_conversations": recent_conversations
    }