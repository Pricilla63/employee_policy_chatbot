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
