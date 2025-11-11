from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from bson import ObjectId

# Fix for protected namespace warning
class BasePydanticConfig:
    model_config = ConfigDict(
        protected_namespaces=(),
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )

# Query models - put these FIRST to avoid import issues
class QueryRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    
    question: str
    document_ids: Optional[List[str]] = None
    new_chat: bool = False

class QueryResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    
    answer: str
    sources: List[str]
    response_time: float
    documents_queried: List[str]
    conversation_id: Optional[str] = None
    is_new_conversation: bool = False

# Message model
class MessageModel(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    
    question: str
    answer: str
    document_ids: List[str]
    document_names: List[str]
    sources: List[str] = []
    response_time: float
    tokens_used: Optional[int] = None
    model_used: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Conversation models
class ConversationModel(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
        protected_namespaces=()
    )
    
    id: Optional[str] = Field(default=None, alias="_id")
    user_id: str
    title: str
    messages: List[Dict[str, Any]] = []
    document_ids: List[str] = []
    is_active: bool = True
    message_count: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_activity: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ConversationCreate(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    
    user_id: str
    title: str
    document_ids: List[str] = []

class ConversationResponse(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        protected_namespaces=()
    )
    
    id: str = Field(alias="_id")
    title: str
    message_count: int
    document_ids: List[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    last_activity: datetime
    preview_message: Optional[str] = None

# QA History models (backward compatibility)
class QAHistoryModel(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        protected_namespaces=()
    )
    
    id: Optional[str] = Field(default=None, alias="_id")
    user_id: str
    username: str
    question: str
    answer: str
    document_ids: List[str]
    document_names: List[str]
    sources: List[str] = []
    response_time: float
    tokens_used: Optional[int] = None
    model_used: str
    conversation_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class QAHistoryCreate(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    
    user_id: str
    username: str
    question: str
    answer: str
    document_ids: List[str]
    document_names: List[str]
    sources: List[str] = []
    response_time: float
    tokens_used: Optional[int] = None
    model_used: str
    conversation_id: Optional[str] = None

class QAHistoryResponse(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        protected_namespaces=()
    )
    
    id: str = Field(alias="_id")
    question: str
    answer: str
    document_names: List[str]
    sources: List[str]
    response_time: float
    conversation_id: Optional[str] = None
    timestamp: datetime

class ConversationStats(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    
    total_conversations: int
    total_questions: int
    total_documents: int
    average_response_time: float
    most_queried_documents: List[dict]
    recent_conversations: List[ConversationResponse]