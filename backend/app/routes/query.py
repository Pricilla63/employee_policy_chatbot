# from fastapi import APIRouter, Depends, HTTPException
# from typing import List, Optional
# from datetime import datetime
# import os
# from pathlib import Path
# from app.services.rag_service import RAGService
# from app.services.conversation_service import ConversationService
# from app.services.document_service import DocumentService
# from app.routes.auth import get_current_user
# from datetime import datetime, timezone
# from app.models import QAHistoryCreate, QueryRequest, QueryResponse

# router = APIRouter(prefix="/query", tags=["Query"])
# rag_service = RAGService()
# conversation_service = ConversationService()
# document_service = DocumentService()

# @router.post("/ask", response_model=QueryResponse)
# async def ask_question(
#     query: QueryRequest,
#     current_user: dict = Depends(get_current_user)
# ):
#     # Get processed documents with version information
#     documents = await document_service.get_processed_documents()
    
#     print(f"🔍 Looking for processed documents with versions")
#     print(f"📄 Documents found: {len(documents)}")
#     for doc in documents:
#         print(f"   - {doc['filename']} v{doc.get('version', 1)} (modified: {doc.get('file_modified_at', 'unknown')})")
    
#     if not documents:
#         # Try to process documents automatically
#         print("🔄 No processed documents found, attempting to process existing files...")
#         try:
#             await document_service.process_existing_documents()
#             documents = await document_service.get_processed_documents()
            
#             if not documents:
#                 raise HTTPException(
#                     status_code=404, 
#                     detail="No documents available for querying. Please upload and process documents first."
#                 )
                
#         except Exception as e:
#             raise HTTPException(
#                 status_code=500, 
#                 detail=f"Failed to process documents: {str(e)}"
#             )
    
#     # Filter documents if specific ones are requested
#     if query.document_ids:
#         filtered_documents = [doc for doc in documents if doc["filename"] in query.document_ids]
#         if filtered_documents:
#             documents = filtered_documents
#             print(f"🎯 Filtered to {len(documents)} requested documents")
#         else:
#             raise HTTPException(
#                 status_code=404,
#                 detail="Requested documents not found or not processed."
#             )
    
#     # Use version-aware querying
#     try:
#         print(f"🤖 Sending version-aware query: '{query.question}'")
#         result = rag_service.query_documents_with_versions(query.question, documents, document_service)
        
#         # Conversation management
#         conversation_id = None
#         is_new_conversation = False
        
#         if query.new_chat:
#             conversation_id = await conversation_service.start_new_conversation(
#                 current_user["_id"],
#                 query.question,
#                 [doc["filename"] for doc in documents]
#             )
#             is_new_conversation = True
#         else:
#             active_conversation = await conversation_service.get_active_conversation(current_user["_id"])
#             if not active_conversation:
#                 conversation_id = await conversation_service.start_new_conversation(
#                     current_user["_id"],
#                     query.question,
#                     [doc["filename"] for doc in documents]
#                 )
#                 is_new_conversation = True
#             else:
#                 conversation_id = active_conversation["_id"]
        
#         # Add message to conversation
#         message_data = {
#             "question": query.question,
#             "answer": result["answer"],
#             "document_ids": [doc["filename"] for doc in documents],
#             "document_names": result["sources"],
#             "sources": result.get("sources", []),
#             "response_time": result["response_time"],
#             "tokens_used": result.get("tokens_used"),
#             "model_used": result["model_used"],
#             "is_latest": result.get("is_latest", True),
#             "latest_document": result.get("latest_document"),
#             "timestamp": datetime.now(timezone.utc)
#         }
        
#         await conversation_service.add_message_to_conversation(conversation_id, message_data)
        
#         if is_new_conversation:
#             better_title = query.question[:30] + "..." if len(query.question) > 30 else query.question
#             await conversation_service.update_conversation_title(conversation_id, better_title)
        
#         print(f"✅ Version-aware query completed in {result['response_time']:.2f}s")
        
#         return {
#             "answer": result["answer"],
#             "sources": result["sources"],
#             "response_time": result["response_time"],
#             "documents_queried": result["sources"],
#             "conversation_id": conversation_id,
#             "is_new_conversation": is_new_conversation,
#             "is_latest": result.get("is_latest", True),
#             "latest_document": result.get("latest_document")
#         }
        
#     except Exception as e:
#         print(f"❌ Error in version-aware ask_question: {e}")
#         raise HTTPException(status_code=500, detail=str(e))

# # Add version debugging endpoint
# @router.get("/debug/versions")
# async def debug_versions():
#     """Debug endpoint to check document versions"""
#     try:
#         documents = await document_service.get_processed_documents()
#         version_info = {}
        
#         for doc in documents:
#             versions = document_service.get_document_versions(doc["filename"])
#             version_info[doc["filename"]] = {
#                 "current_version": doc.get("version", 1),
#                 "total_versions": len(versions),
#                 "latest_modified": doc.get("file_modified_at"),
#                 "versions": versions
#             }
        
#         return {
#             "total_documents": len(documents),
#             "version_info": version_info
#         }
#     except Exception as e:
#         return {"error": str(e)}
    
# @router.get("/debug/vector-store/{vector_store_id}")
# async def debug_vector_store(vector_store_id: str):
#     """Debug endpoint to check what's in a vector store"""
#     try:
#         vector_store = rag_service.load_vector_store(vector_store_id)
        
#         # Get some sample content from the vector store
#         sample_docs = vector_store.similarity_search("", k=5)  # Empty query to get random samples
        
#         sample_content = []
#         for i, doc in enumerate(sample_docs):
#             sample_content.append({
#                 "chunk_id": i,
#                 "content_preview": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
#                 "content_length": len(doc.page_content),
#                 "metadata": doc.metadata
#             })
        
#         return {
#             "vector_store_id": vector_store_id,
#             "total_chunks": len(sample_docs),
#             "sample_content": sample_content
#         }
#     except Exception as e:
#         return {"error": str(e)}

# @router.get("/debug/document-content/{filename}")
# async def debug_document_content(filename: str):
#     """Debug what text was extracted from a document"""
#     try:
#         # Find the document
#         all_docs = document_service.get_available_documents()
#         target_doc = next((doc for doc in all_docs if doc['filename'] == filename), None)
        
#         if not target_doc:
#             return {"error": f"Document {filename} not found in uploads"}
        
#         # Extract text to see what's actually in the document
#         file_path = target_doc['file_path']
#         file_extension = filename.split('.')[-1].lower()
        
#         text = ""
#         if file_extension == 'pdf':
#             text = document_service.extract_text_from_pdf(file_path)
#         elif file_extension in ['docx', 'doc']:
#             text = document_service.extract_text_from_docx(file_path)
#         elif file_extension == 'txt':
#             text = document_service.extract_text_from_txt(file_path)
        
#         # Show samples
#         lines = text.split('\n')
#         non_empty_lines = [line.strip() for line in lines if line.strip()]
        
#         return {
#             "filename": filename,
#             "file_path": file_path,
#             "total_length": len(text),
#             "non_empty_lines_count": len(non_empty_lines),
#             "sample_lines": non_empty_lines[:10],  # First 10 non-empty lines
#             "has_leave_keyword": "leave" in text.lower(),
#             "has_policy_keyword": "policy" in text.lower(),
#             "has_content": bool(text.strip())
#         }
        
#     except Exception as e:
#         return {"error": str(e)}


# ✅ FINAL UPDATED query.py (auto detect new docs before answering + latest version-aware RAG)

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
#         "is_new_conversation": is_new
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


# ✅ FINAL UPDATED query.py (auto detect new docs before answering + latest version-aware RAG)

from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timezone
from app.services.rag_service import RAGService
from app.services.conversation_service import ConversationService
from app.services.document_service import DocumentService
from app.routes.auth import get_current_user
from app.models import QueryRequest, QueryResponse

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
    if query.new_chat:
        conversation_id = await conversation_service.start_new_conversation(
            current_user["_id"], query.question, [doc["filename"] for doc in documents]
        )
        is_new = True
    else:
        convo = await conversation_service.get_active_conversation(current_user["_id"])
        if convo:
            conversation_id = convo["_id"]
            is_new = False
        else:
            conversation_id = await conversation_service.start_new_conversation(
                current_user["_id"], query.question, [doc["filename"] for doc in documents]
            )
            is_new = True

    await conversation_service.add_message_to_conversation(conversation_id, {
        "question": query.question,
        "answer": result["answer"],
        "document_ids": [doc["filename"] for doc in documents],
        "document_names": result["sources"],
        "sources": result.get("sources", []),
        "response_time": result.get("response_time"),
        "model_used": result.get("model_used"),
        "timestamp": datetime.now(timezone.utc)
    })

    print(f"✅ Query completed in {result.get('response_time')} seconds")

    return {
        "answer": result["answer"],
        "sources": result["sources"],
        "response_time": result.get("response_time"),
        "conversation_id": conversation_id,
        "is_new_conversation": is_new,
        # ✅ add documents_queried for Pydantic model compatibility
        "documents_queried": [doc["filename"] for doc in documents],
        # ✅ provide safe defaults to satisfy older response models
        "is_latest": result.get("is_latest", True),
        "latest_document": result.get("latest_document")
    }

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

    if ext == 'pdf': text = document_service.extract_text_from_pdf(file_path)
    elif ext in ['doc', 'docx']: text = document_service.extract_text_from_docx(file_path)
    else: text = document_service.extract_text_from_txt(file_path)

    lines = [l.strip() for l in text.split("\n") if l.strip()]

    return {
        "filename": filename,
        "path": file_path,
        "characters": len(text),
        "non_empty_lines": len(lines),
        "sample": lines[:10]
    }
