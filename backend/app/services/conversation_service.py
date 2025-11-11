from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from bson import ObjectId
from app.database import get_conversations_collection

class ConversationService:
    def __init__(self):
        # Don't initialize collection in __init__ - get it when needed
        self._collection = None
    
    @property
    def collection(self):
        """Lazy loading of collection"""
        if self._collection is None:
            self._collection = get_conversations_collection()
        return self._collection
    
    async def create_conversation(self, user_id: str, title: str, document_ids: List[str] = None) -> str:
        """Create a new conversation"""
        if document_ids is None:
            document_ids = []
            
        conversation_dict = {
            "user_id": user_id,
            "title": title,
            "messages": [],
            "document_ids": document_ids,
            "is_active": True,
            "message_count": 0,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "last_activity": datetime.now(timezone.utc)
        }
        
        result = await self.collection.insert_one(conversation_dict)
        return str(result.inserted_id)
    
    async def get_user_conversations(self, user_id: str, limit: int = 50, skip: int = 0) -> List[Dict]:
        """Get all conversations for a user"""
        cursor = self.collection.find(
            {"user_id": user_id}
        ).sort("last_activity", -1).skip(skip).limit(limit)
        
        conversations = []
        async for conv in cursor:
            conv["_id"] = str(conv["_id"])
            # Add preview message (last message if exists)
            if conv["messages"]:
                last_msg = conv["messages"][-1]
                conv["preview_message"] = last_msg.get("question", "No messages yet")
            else:
                conv["preview_message"] = "No messages yet"
            conversations.append(conv)
        
        return conversations
    
    async def get_active_conversation(self, user_id: str) -> Optional[Dict]:
        """Get user's active conversation"""
        conversation = await self.collection.find_one({
            "user_id": user_id,
            "is_active": True
        })
        
        if conversation:
            conversation["_id"] = str(conversation["_id"])
            return conversation
        
        return None
    
    async def get_conversation(self, conversation_id: str, user_id: str) -> Optional[Dict]:
        """Get specific conversation"""
        conversation = await self.collection.find_one({
            "_id": ObjectId(conversation_id),
            "user_id": user_id
        })
        
        if conversation:
            conversation["_id"] = str(conversation["_id"])
            return conversation
        
        return None
    
    async def add_message_to_conversation(self, conversation_id: str, message: Dict) -> bool:
        """Add a message to conversation and update activity"""
        result = await self.collection.update_one(
            {"_id": ObjectId(conversation_id)},
            {
                "$push": {"messages": message},
                "$inc": {"message_count": 1},
                "$set": {
                    "updated_at": datetime.now(timezone.utc),
                    "last_activity": datetime.now(timezone.utc)
                }
            }
        )
        
        return result.modified_count > 0
    
    async def update_conversation_title(self, conversation_id: str, title: str) -> bool:
        """Update conversation title"""
        result = await self.collection.update_one(
            {"_id": ObjectId(conversation_id)},
            {
                "$set": {
                    "title": title,
                    "updated_at": datetime.now(timezone.utc)
                }
            }
        )
        
        return result.modified_count > 0
    
    async def deactivate_all_conversations(self, user_id: str) -> bool:
        """Deactivate all user conversations (when starting new chat)"""
        result = await self.collection.update_many(
            {"user_id": user_id, "is_active": True},
            {"$set": {"is_active": False}}
        )
        
        return result.modified_count > 0
    
    async def start_new_conversation(self, user_id: str, first_question: str, document_ids: List[str] = None) -> str:
        """Start a new conversation and deactivate old ones"""
        if document_ids is None:
            document_ids = []
        
        # Deactivate all current conversations
        await self.deactivate_all_conversations(user_id)
        
        # Generate title from first question
        title = first_question[:50] + "..." if len(first_question) > 50 else first_question
        
        # Create new conversation
        return await self.create_conversation(user_id, title, document_ids)
    
    async def delete_conversation(self, conversation_id: str, user_id: str) -> bool:
        """Delete a conversation"""
        result = await self.collection.delete_one({
            "_id": ObjectId(conversation_id),
            "user_id": user_id
        })
        
        return result.deleted_count > 0
    
    async def get_conversation_stats(self, user_id: str) -> Dict:
        """Get conversation statistics for user"""
        pipeline = [
            {"$match": {"user_id": user_id}},
            {"$group": {
                "_id": None,
                "total_conversations": {"$sum": 1},
                "total_messages": {"$sum": "$message_count"}
            }}
        ]
        
        result = await self.collection.aggregate(pipeline).to_list(1)
        
        if result:
            return {
                "total_conversations": result[0]["total_conversations"],
                "total_messages": result[0]["total_messages"]
            }
        
        return {"total_conversations": 0, "total_messages": 0}