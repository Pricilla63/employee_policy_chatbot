# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from contextlib import asynccontextmanager
# from datetime import datetime, timezone
# from app.database import connect_to_mongo, close_mongo_connection
# from app.routes.auth import router as auth_router
# from app.routes.documents import router as documents_router
# from app.routes.query import router as query_router
# from app.routes.history import router as history_router
# from app.routes.conversations import router as conversations_router
# from app.services.document_service import DocumentService

# doc_service = DocumentService()

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     # Startup
#     await connect_to_mongo()
#     print("🚀 Server started — scanning /uploads for new documents...")
#     try:
#         new_docs = await doc_service.process_existing_documents()
#         if new_docs:
#             print(f"📦 Processed new documents at startup: {new_docs}")
#         else:
#             print("✅ No new documents detected at startup")
#     except Exception as e:
#         print(f"❌ Error processing docs on startup: {e}")
#     yield

#     # Shutdown
#     await close_mongo_connection()
#     print("🔌 MongoDB connection closed")

# app = FastAPI(
#     title="Document Q&A RAG Application with MongoDB",
#     description="AI-powered document Q&A system with version control and intelligent retrieval",
#     version="2.1.0",
#     lifespan=lifespan,
# )

# # ✅ CORS config (React support)
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=[
#         "http://localhost:3000",
#         "http://localhost:3001",
#         "http://127.0.0.1:3000",
#         "http://127.0.0.1:3001",
#         "http://localhost:5173",
#     ],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # ✅ API Routers
# app.include_router(auth_router)
# app.include_router(documents_router)
# app.include_router(query_router)
# app.include_router(history_router)
# app.include_router(conversations_router)

# @app.get("/")
# async def root():
#     return {
#         "message": "Document Q&A RAG API running ✅",
#         "version": "2.1.0",
#         "services": ["Auth", "Documents", "RAG Query", "Conversation History"],
#         "timestamp": datetime.now(timezone.utc),
#     }

# @app.get("/health")
# async def health_check():
#     return {"status": "UP", "time": datetime.now(timezone.utc)}

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(
#         "main:app",
#         host="0.0.0.0",
#         port=8000,
#         reload=True,
#         log_level="info",
#     )






from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import connect_to_mongo, close_mongo_connection
from app.routes import conversations, auth, query

app = FastAPI(title="Document Chat API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(query.router)
app.include_router(conversations.router)
app.include_router(auth.router)

# Database events
@app.on_event("startup")
async def startup_event():
    await connect_to_mongo()

@app.on_event("shutdown")
async def shutdown_event():
    await close_mongo_connection()

@app.get("/")
async def root():
    return {"message": "Document Chat API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "document-chat-api"}