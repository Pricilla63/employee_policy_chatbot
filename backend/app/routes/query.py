# from fastapi import APIRouter, Depends, HTTPException
# from typing import List, Optional
# from datetime import datetime
# from bson import ObjectId
# from app.database import get_documents_collection, get_qa_history_collection
# from app.models.conversation import QAHistoryCreate, QueryRequest, QueryResponse
# from app.services.rag_service import RAGService
# from app.services.conversation_service import ConversationService
# from app.routes.auth import get_current_user
# from pydantic import BaseModel
# from datetime import datetime, timezone

# router = APIRouter(prefix="/query", tags=["Query"])
# rag_service = RAGService()
# conversation_service = ConversationService()

# class QueryRequest(BaseModel):
#     question: str
#     document_ids: Optional[List[str]] = None
#     new_chat: bool = False  # Flag to start new conversation

# class QueryResponse(BaseModel):
#     answer: str
#     sources: List[str]
#     response_time: float
#     documents_queried: List[str]
#     conversation_id: Optional[str] = None
#     is_new_conversation: bool = False

# @router.post("/ask", response_model=QueryResponse)
# async def ask_question(
#     query: QueryRequest,
#     current_user: dict = Depends(get_current_user)
# ):
#     # Get collections INSIDE the async function
#     documents_collection = get_documents_collection()
#     qa_history_collection = get_qa_history_collection()
    
#     # Get documents - fetch SHARED documents OR user's own documents
#     if query.document_ids:
#         object_ids = [ObjectId(doc_id) for doc_id in query.document_ids]
#         cursor = documents_collection.find({
#             "_id": {"$in": object_ids},
#             "$or": [
#                 {"is_shared": True},
#                 {"owner_id": current_user["_id"]}
#             ]
#         })
#     else:
#         # Query ALL shared documents (ignore owner)
#         cursor = documents_collection.find({"is_shared": True})
    
#     documents = await cursor.to_list(length=100)
    
#     if not documents:
#         raise HTTPException(
#             status_code=404, 
#             detail="No shared documents found. Please contact administrator to upload company documents."
#         )
    
#     # Get vector store IDs and document names
#     vector_store_ids = [doc["vector_store_id"] for doc in documents]
#     document_names = [doc["filename"] for doc in documents]
#     document_ids = [str(doc["_id"]) for doc in documents]
    
#     # Conversation management
#     conversation_id = None
#     is_new_conversation = False
    
#     if query.new_chat:
#         # Start a new conversation
#         conversation_id = await conversation_service.start_new_conversation(
#             current_user["_id"],
#             query.question,
#             document_ids
#         )
#         is_new_conversation = True
#     else:
#         # Get active conversation or create one if none exists
#         active_conversation = await conversation_service.get_active_conversation(current_user["_id"])
#         if not active_conversation:
#             conversation_id = await conversation_service.start_new_conversation(
#                 current_user["_id"],
#                 query.question,
#                 document_ids
#             )
#             is_new_conversation = True
#         else:
#             conversation_id = active_conversation["_id"]
    
#     # Query documents
#     try:
#         result = rag_service.query_documents(vector_store_ids, query.question)
        
#         # Create message for conversation
#         message_data = {
#             "question": query.question,
#             "answer": result["answer"],
#             "document_ids": document_ids,
#             "document_names": document_names,
#             "sources": result["sources"],
#             "response_time": result["response_time"],
#             "tokens_used": result.get("tokens_used"),
#             "model_used": result["model_used"],
#             "timestamp": datetime.now(timezone.utc)
#         }
        
#         # Add message to conversation
#         await conversation_service.add_message_to_conversation(conversation_id, message_data)
        
#         # Update conversation title if it's the first message and title is generic
#         if is_new_conversation:
#             # Generate better title from the question
#             better_title = query.question[:30] + "..." if len(query.question) > 30 else query.question
#             await conversation_service.update_conversation_title(conversation_id, better_title)
        
#         # Also save to QA history for backward compatibility
#         qa_record = QAHistoryCreate(
#             user_id=current_user["_id"],
#             username=current_user["username"],
#             question=query.question,
#             answer=result["answer"],
#             document_ids=document_ids,
#             document_names=document_names,
#             sources=result["sources"],
#             response_time=result["response_time"],
#             tokens_used=result.get("tokens_used"),
#             model_used=result["model_used"],
#             conversation_id=conversation_id
#         )
        
#         await qa_history_collection.insert_one(qa_record.model_dump())
        
#         return {
#             "answer": result["answer"],
#             "sources": result["sources"],
#             "response_time": result["response_time"],
#             "documents_queried": document_names,
#             "conversation_id": conversation_id,
#             "is_new_conversation": is_new_conversation
#         }
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))



from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from datetime import datetime
from bson import ObjectId
from app.database import get_documents_collection, get_qa_history_collection
from app.models.conversation import QAHistoryCreate, QueryRequest, QueryResponse
from app.services.rag_service import RAGService
from app.services.conversation_service import ConversationService
from app.routes.auth import get_current_user
from datetime import datetime, timezone
from app.config import get_settings

settings = get_settings()

router = APIRouter(prefix="/query", tags=["Query"])
rag_service = RAGService()
conversation_service = ConversationService()

@router.post("/ask", response_model=QueryResponse)
async def ask_question(
    query: QueryRequest,
    current_user: dict = Depends(get_current_user)
):
    # Get collections INSIDE the async function
    documents_collection = get_documents_collection()
    qa_history_collection = get_qa_history_collection()
    
    # Get documents - fetch SHARED documents OR user's own documents
    if query.document_ids:
        object_ids = [ObjectId(doc_id) for doc_id in query.document_ids]
        cursor = documents_collection.find({
            "_id": {"$in": object_ids},
            "$or": [
                {"is_shared": True},
                {"owner_id": current_user["_id"]}
            ]
        })
    else:
        # Query ALL shared documents (ignore owner)
        cursor = documents_collection.find({"is_shared": True})
    
    documents = await cursor.to_list(length=100)
    
    if not documents:
        raise HTTPException(
            status_code=404, 
            detail="No shared documents found. Please contact administrator to upload company documents."
        )
    
    # Get vector store IDs and document names
    vector_store_ids = [doc["vector_store_id"] for doc in documents]
    document_names = [doc["filename"] for doc in documents]
    document_ids = [str(doc["_id"]) for doc in documents]
    
    # Conversation management
    conversation_id = None
    is_new_conversation = False
    
    if query.new_chat:
        # Start a new conversation
        conversation_id = await conversation_service.start_new_conversation(
            current_user["_id"],
            query.question,
            document_ids
        )
        is_new_conversation = True
    else:
        # Get active conversation or create one if none exists
        active_conversation = await conversation_service.get_active_conversation(current_user["_id"])
        if not active_conversation:
            conversation_id = await conversation_service.start_new_conversation(
                current_user["_id"],
                query.question,
                document_ids
            )
            is_new_conversation = True
        else:
            conversation_id = active_conversation["_id"]
    
    # Query documents
    try:
        result = rag_service.query_documents(vector_store_ids, query.question)
        
        # Create message for conversation
        message_data = {
            "question": query.question,
            "answer": result["answer"],
            "document_ids": document_ids,
            "document_names": document_names,
            "sources": result["sources"],
            "response_time": result["response_time"],
            "tokens_used": result.get("tokens_used"),
            "model_used": result["model_used"],
            "timestamp": datetime.now(timezone.utc)
        }
        
        # Add message to conversation
        await conversation_service.add_message_to_conversation(conversation_id, message_data)
        
        # Update conversation title if it's the first message and title is generic
        if is_new_conversation:
            # Generate better title from the question
            better_title = query.question[:30] + "..." if len(query.question) > 30 else query.question
            await conversation_service.update_conversation_title(conversation_id, better_title)
        
        # Also save to QA history for backward compatibility
        qa_record = QAHistoryCreate(
            user_id=current_user["_id"],
            username=current_user["username"],
            question=query.question,
            answer=result["answer"],
            document_ids=document_ids,
            document_names=document_names,
            sources=result["sources"],
            response_time=result["response_time"],
            tokens_used=result.get("tokens_used"),
            model_used=result["model_used"],
            conversation_id=conversation_id
        )
        
        await qa_history_collection.insert_one(qa_record.model_dump())
        
        return {
            "answer": result["answer"],
            "sources": result["sources"],
            "response_time": result["response_time"],
            "documents_queried": document_names,
            "conversation_id": conversation_id,
            "is_new_conversation": is_new_conversation
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))