from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime, timezone

class DocumentModel(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True
    )
    
    id: Optional[str] = Field(default=None, alias="_id")
    filename: str
    file_path: str
    file_type: str
    file_size: int
    vector_store_id: str
    owner_id: str
    is_shared: bool = True
    chunk_count: int = 0
    uploaded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))  # ← Fixed

class DocumentCreate(BaseModel):
    filename: str
    file_path: str
    file_type: str
    file_size: int
    vector_store_id: str
    owner_id: str
    is_shared: bool = True
    chunk_count: int = 0

class DocumentResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    id: str = Field(alias="_id")
    filename: str
    file_type: str
    file_size: int
    chunk_count: int
    is_shared: bool = True
    uploaded_at: datetime