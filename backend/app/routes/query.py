# from fastapi import APIRouter, Depends, HTTPException
# from datetime import datetime, timezone
# from app.services.rag_service import RAGService
# from app.services.conversation_service import ConversationService
# from app.services.document_service import DocumentService
# from app.routes.auth import get_current_user
# from app.models import QueryRequest, QueryResponse

# router = APIRouter(prefix="/query", tags=["Query"])
# rag_service = RAGService()
# conversation_service = ConversationService()
# document_service = DocumentService()

# @router.post("/ask", response_model=QueryResponse)
# async def ask_question(query: QueryRequest, current_user: dict = Depends(get_current_user)):
#     print("📝 Checking /uploads for new files before answering...")
#     new_docs = await document_service.process_existing_documents()

#     if new_docs:
#         print(f"📦 New documents detected & processed: {new_docs}")
#     else:
#         print("✅ No new documents to process before query")

#     documents = await document_service.get_processed_documents()
#     print(f"📊 Total processed documents available: {len(documents)}")

#     if not documents:
#         raise HTTPException(status_code=404, detail="No processed documents found. Add documents to /uploads.")

#     # Filter for specific documents (if requested from UI)
#     if query.document_ids:
#         filtered = [d for d in documents if d["filename"] in query.document_ids]
#         if filtered:
#             documents = filtered
#             print(f"🎯 Using filtered docs: {query.document_ids}")
#         else:
#             raise HTTPException(status_code=404, detail="Requested documents not processed.")

#     print(f"🤖 Running version-aware RAG query: '{query.question}'")
#     result = rag_service.query_documents_with_versions(query.question, documents, document_service)

#     # ===== Conversation Management =====
#     if query.new_chat:
#         conversation_id = await conversation_service.start_new_conversation(
#             current_user["_id"], query.question, [doc["filename"] for doc in documents]
#         )
#         is_new = True
#     else:
#         convo = await conversation_service.get_active_conversation(current_user["_id"])
#         if convo:
#             conversation_id = convo["_id"]
#             is_new = False
#         else:
#             conversation_id = await conversation_service.start_new_conversation(
#                 current_user["_id"], query.question, [doc["filename"] for doc in documents]
#             )
#             is_new = True

#     await conversation_service.add_message_to_conversation(conversation_id, {
#         "question": query.question,
#         "answer": result["answer"],
#         "document_ids": [doc["filename"] for doc in documents],
#         "document_names": result["sources"],
#         "sources": result.get("sources", []),
#         "response_time": result.get("response_time"),
#         "model_used": result.get("model_used"),
#         "timestamp": datetime.now(timezone.utc)
#     })

#     print(f"✅ Query completed in {result.get('response_time')} seconds")

#     return {
#         "answer": result["answer"],
#         "sources": result["sources"],
#         "response_time": result.get("response_time"),
#         "conversation_id": conversation_id,
#         "is_new_conversation": is_new,
#         # ✅ add documents_queried for Pydantic model compatibility
#         "documents_queried": [doc["filename"] for doc in documents],
#         # ✅ provide safe defaults to satisfy older response models
#         "is_latest": result.get("is_latest", True),
#         "latest_document": result.get("latest_document")
#     }

# # ================= Debug Endpoints ==================

# @router.get("/debug/versions")
# async def debug_versions():
#     docs = await document_service.get_processed_documents()
#     versions = {}
#     for d in docs:
#         versions[d["filename"]] = {
#             "version": d.get("version"),
#             "modified": d.get("file_modified_at"),
#             "vector_id": d.get("vector_store_id"),
#         }
#     return {"count": len(docs), "versions": versions}

# @router.get("/debug/document-content/{filename}")
# async def debug_document_content(filename: str):
#     all_docs = document_service.get_available_documents()
#     doc = next((d for d in all_docs if d['filename'] == filename), None)
#     if not doc:
#         return {"error": "File not found in uploads"}

#     file_path = doc['file_path']
#     ext = filename.split('.')[-1].lower()

#     if ext == 'pdf': text = document_service.extract_text_from_pdf(file_path)
#     elif ext in ['doc', 'docx']: text = document_service.extract_text_from_docx(file_path)
#     else: text = document_service.extract_text_from_txt(file_path)

#     lines = [l.strip() for l in text.split("\n") if l.strip()]

#     return {
#         "filename": filename,
#         "path": file_path,
#         "characters": len(text),
#         "non_empty_lines": len(lines),
#         "sample": lines[:10]
#     }


















# from fastapi import APIRouter, Depends, HTTPException
# from app.services.conversation_service import ConversationService
# from app.database import get_qa_history_collection, get_documents_from_uploads
# from app.routes.auth import get_current_user
# from app.models.conversation import QueryRequest, QueryResponse, QAHistoryCreate
# from datetime import datetime, timezone
# from typing import Optional, List
# import time

# router = APIRouter(prefix="/query", tags=["Query"])
# conversation_service = ConversationService()

# async def process_query_with_rag(
#     question: str, 
#     document_ids: Optional[List[str]] = None,
#     user_id: str = None
# ):
#     """
#     Replace this function with your actual RAG processing logic
#     This is just a placeholder that returns mock data
#     """
#     # Get documents to query
#     all_documents = get_documents_from_uploads()
#     documents_to_query = all_documents
    
#     if document_ids:
#         # Filter documents by provided IDs
#         documents_to_query = [doc for doc in all_documents if doc["filename"] in document_ids]
    
#     # Simulate RAG processing - REPLACE THIS WITH YOUR ACTUAL RAG CODE
#     answer = f"This is a simulated answer for: {question}. [Replace with your actual RAG system]"
#     sources = [f"Source from {doc['filename']}" for doc in documents_to_query[:3]]
#     tokens_used = len(question.split()) + len(answer.split())
#     model_used = "gpt-3.5-turbo"
    
#     return answer, sources, documents_to_query, tokens_used, model_used

# async def save_to_qa_history(
#     user_id: str,
#     username: str,
#     question: str,
#     answer: str,
#     document_ids: List[str],
#     document_names: List[str],
#     sources: List[str] = [],
#     response_time: float = 0.0,
#     tokens_used: Optional[int] = None,
#     model_used: str = "gpt-3.5-turbo",
#     conversation_id: Optional[str] = None
# ):
#     """Save query to QA history"""
#     qa_history_collection = get_qa_history_collection()
    
#     history_data = QAHistoryCreate(
#         user_id=user_id,
#         username=username,
#         question=question,
#         answer=answer,
#         document_ids=document_ids,
#         document_names=document_names,
#         sources=sources,
#         response_time=response_time,
#         tokens_used=tokens_used,
#         model_used=model_used,
#         conversation_id=conversation_id
#     )
    
#     await qa_history_collection.insert_one(history_data.dict())

# @router.post("/", response_model=QueryResponse)
# async def query_documents(
#     request: QueryRequest,
#     current_user: dict = Depends(get_current_user)
# ):
#     """Query documents with conversation support"""
#     start_time = time.time()
    
#     user_id = current_user["_id"]
#     username = current_user.get("username", "user")
    
#     print(f"🔍 DEBUG: Received query - new_chat: {request.new_chat}, question: {request.question[:50]}...")
    
#     # Handle conversation logic
#     conversation_id = None
#     is_new_conversation = False
    
#     if request.new_chat:
#         # Start a new conversation
#         print("🆕 DEBUG: Creating NEW conversation")
#         conversation_id = await conversation_service.start_new_conversation(
#             user_id, request.question, request.document_ids or []
#         )
#         is_new_conversation = True
#         print(f"✅ DEBUG: New conversation created with ID: {conversation_id}")
#     else:
#         # Get active conversation or create one if none exists
#         active_conv = await conversation_service.get_active_conversation(user_id)
#         if active_conv:
#             conversation_id = active_conv["_id"]
#             is_new_conversation = False
#             print(f"🔄 DEBUG: Continuing existing conversation: {conversation_id}")
#         else:
#             # No active conversation, create one
#             print("⚠️ DEBUG: No active conversation found, creating one")
#             conversation_id = await conversation_service.start_new_conversation(
#                 user_id, request.question, request.document_ids or []
#             )
#             is_new_conversation = True
#             print(f"✅ DEBUG: New conversation created with ID: {conversation_id}")
    
#     # Process the query using your RAG system
#     answer, sources, documents_queried, tokens_used, model_used = await process_query_with_rag(
#         request.question, 
#         request.document_ids,
#         user_id
#     )
    
#     response_time = time.time() - start_time
    
#     # Create message object
#     message_data = {
#         "question": request.question,
#         "answer": answer,
#         "document_ids": [doc["filename"] for doc in documents_queried],
#         "document_names": [doc["filename"] for doc in documents_queried],
#         "sources": sources,
#         "response_time": response_time,
#         "tokens_used": tokens_used,
#         "model_used": model_used,
#         "timestamp": datetime.now(timezone.utc)
#     }
    
#     # Add message to conversation
#     if conversation_id:
#         print(f"💾 DEBUG: Saving message to conversation: {conversation_id}")
#         success = await conversation_service.add_message_to_conversation(conversation_id, message_data)
#         print(f"📝 DEBUG: Message saved successfully: {success}")
    
#     # Save to QA history for backward compatibility
#     await save_to_qa_history(
#         user_id=user_id,
#         username=username,
#         question=request.question,
#         answer=answer,
#         document_ids=[doc["filename"] for doc in documents_queried],
#         document_names=[doc["filename"] for doc in documents_queried],
#         sources=sources,
#         response_time=response_time,
#         tokens_used=tokens_used,
#         model_used=model_used,
#         conversation_id=conversation_id
#     )
    
#     print(f"🎯 DEBUG: Returning response - conversation_id: {conversation_id}, is_new_conversation: {is_new_conversation}")
    
#     return QueryResponse(
#         answer=answer,
#         sources=sources,
#         response_time=response_time,
#         documents_queried=[doc["filename"] for doc in documents_queried],
#         conversation_id=conversation_id,
#         is_new_conversation=is_new_conversation
#     )

# # Add this endpoint to match your frontend's expected endpoint
# @router.post("/ask", response_model=QueryResponse)
# async def ask_question(
#     request: QueryRequest,
#     current_user: dict = Depends(get_current_user)
# ):
#     """Alias for query endpoint to match frontend expectations"""
#     print("🔍 DEBUG: /ask endpoint called")
#     return await query_documents(request, current_user)


from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timezone
from app.services.rag_service import RAGService
from app.services.conversation_service import ConversationService
from app.services.document_service import DocumentService
from app.routes.auth import get_current_user
from app.models.conversation import QueryRequest, QueryResponse
import time

router = APIRouter(prefix="/query", tags=["Query"])
rag_service = RAGService()
conversation_service = ConversationService()
document_service = DocumentService()

@router.post("/ask", response_model=QueryResponse)
async def ask_question(query: QueryRequest, current_user: dict = Depends(get_current_user)):
    print("📝 Checking /uploads for new files before answering...")
    new_docs = await document_service.process_existing_documents()

    if new_docs:
        print(f"📦 New documents detected & processed: {new_docs}")
    else:
        print("✅ No new documents to process before query")

    documents = await document_service.get_processed_documents()
    print(f"📊 Total processed documents available: {len(documents)}")

    if not documents:
        raise HTTPException(status_code=404, detail="No processed documents found. Add documents to /uploads.")

    # Filter for specific documents (if requested from UI)
    if query.document_ids:
        filtered = [d for d in documents if d["filename"] in query.document_ids]
        if filtered:
            documents = filtered
            print(f"🎯 Using filtered docs: {query.document_ids}")
        else:
            raise HTTPException(status_code=404, detail="Requested documents not processed.")

    print(f"🤖 Running version-aware RAG query: '{query.question}'")
    result = rag_service.query_documents_with_versions(query.question, documents, document_service)

    # ===== Conversation Management =====
    start_time = time.time()
    user_id = current_user["_id"]
    username = current_user.get("username", "user")
    
    print(f"🔍 DEBUG: Received query - new_chat: {query.new_chat}, question: {query.question[:50]}...")
    
    # Handle conversation logic
    conversation_id = None
    is_new_conversation = False
    
    if query.new_chat:
        # Start a new conversation
        print("🆕 DEBUG: Creating NEW conversation")
        conversation_id = await conversation_service.start_new_conversation(
            user_id, query.question, [doc["filename"] for doc in documents]
        )
        is_new_conversation = True
        print(f"✅ DEBUG: New conversation created with ID: {conversation_id}")
    else:
        # Get active conversation or create one if none exists
        active_conv = await conversation_service.get_active_conversation(user_id)
        if active_conv:
            conversation_id = active_conv["_id"]
            is_new_conversation = False
            print(f"🔄 DEBUG: Continuing existing conversation: {conversation_id}")
        else:
            # No active conversation, create one
            print("⚠️ DEBUG: No active conversation found, creating one")
            conversation_id = await conversation_service.start_new_conversation(
                user_id, query.question, [doc["filename"] for doc in documents]
            )
            is_new_conversation = True
            print(f"✅ DEBUG: New conversation created with ID: {conversation_id}")
    
    response_time = time.time() - start_time

    # Create message object
    message_data = {
        "question": query.question,
        "answer": result["answer"],
        "document_ids": [doc["filename"] for doc in documents],
        "document_names": [doc["filename"] for doc in documents],
        "sources": result.get("sources", []),
        "response_time": response_time,
        "tokens_used": result.get("tokens_used"),
        "model_used": result.get("model_used", "unknown"),
        "timestamp": datetime.now(timezone.utc)
    }
    
    # Add message to conversation
    if conversation_id:
        print(f"💾 DEBUG: Saving message to conversation: {conversation_id}")
        success = await conversation_service.add_message_to_conversation(conversation_id, message_data)
        print(f"📝 DEBUG: Message saved successfully: {success}")
    
    print(f"🎯 DEBUG: Returning response - conversation_id: {conversation_id}, is_new_conversation: {is_new_conversation}")
    print(f"✅ Query completed in {response_time} seconds")

    return QueryResponse(
        answer=result["answer"],
        sources=result.get("sources", []),
        response_time=response_time,
        documents_queried=[doc["filename"] for doc in documents],
        conversation_id=conversation_id,
        is_new_conversation=is_new_conversation
    )

# Add this endpoint for backward compatibility
@router.post("/", response_model=QueryResponse)
async def query_documents(
    request: QueryRequest,
    current_user: dict = Depends(get_current_user)
):
    """Alias for /ask endpoint"""
    print("🔍 DEBUG: / endpoint called, redirecting to /ask")
    return await ask_question(request, current_user)

# ================= Debug Endpoints ==================

@router.get("/debug/versions")
async def debug_versions():
    docs = await document_service.get_processed_documents()
    versions = {}
    for d in docs:
        versions[d["filename"]] = {
            "version": d.get("version"),
            "modified": d.get("file_modified_at"),
            "vector_id": d.get("vector_store_id"),
        }
    return {"count": len(docs), "versions": versions}

@router.get("/debug/document-content/{filename}")
async def debug_document_content(filename: str):
    all_docs = document_service.get_available_documents()
    doc = next((d for d in all_docs if d['filename'] == filename), None)
    if not doc:
        return {"error": "File not found in uploads"}

    file_path = doc['file_path']
    ext = filename.split('.')[-1].lower()

    if ext == 'pdf': 
        text = document_service.extract_text_from_pdf(file_path)
    elif ext in ['doc', 'docx']: 
        text = document_service.extract_text_from_docx(file_path)
    else: 
        text = document_service.extract_text_from_txt(file_path)

    lines = [l.strip() for l in text.split("\n") if l.strip()]

    return {
        "filename": filename,
        "path": file_path,
        "characters": len(text),
        "non_empty_lines": len(lines),
        "sample": lines[:10]
    }