import json
import logging
from typing import List, Dict, Optional, Tuple
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from conversation_models import Base, User, Conversation, Message, generate_conversation_id, generate_message_id
from datetime import datetime

logger = logging.getLogger(__name__)

class ConversationManager:
    def __init__(self, database_url: str = "sqlite:///conversations.db"):
        """Initialize the conversation manager with database connection"""
        self.engine = create_engine(database_url, echo=False)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self._create_tables()
    
    def _create_tables(self):
        """Create database tables if they don't exist"""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Conversation database tables created successfully")
        except Exception as e:
            logger.error(f"Error creating tables: {e}")
    
    def get_db_session(self) -> Session:
        """Get a database session"""
        return self.SessionLocal()
    
    def create_or_get_user(self, user_id: str, username: str = None, email: str = None) -> User:
        """Create a new user or get existing user"""
        session = self.get_db_session()
        try:
            user = session.query(User).filter(User.user_id == user_id).first()
            if not user:
                user = User(
                    user_id=user_id,
                    username=username,
                    email=email
                )
                session.add(user)
                session.commit()
                logger.info(f"Created new user: {user_id}")
            return user
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Error creating/getting user: {e}")
            raise
        finally:
            session.close()
    
    def create_conversation(self, user_id: str, title: str = None) -> Conversation:
        """Create a new conversation for a user"""
        session = self.get_db_session()
        try:
            # Ensure user exists
            self.create_or_get_user(user_id)
            
            conversation = Conversation(
                conversation_id=generate_conversation_id(),
                user_id=user_id,
                title=title or f"Conversation {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}"
            )
            session.add(conversation)
            session.commit()
            logger.info(f"Created new conversation: {conversation.conversation_id}")
            return conversation
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Error creating conversation: {e}")
            raise
        finally:
            session.close()
    
    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Get a conversation by ID"""
        session = self.get_db_session()
        try:
            conversation = session.query(Conversation).filter(
                Conversation.conversation_id == conversation_id
            ).first()
            return conversation
        except SQLAlchemyError as e:
            logger.error(f"Error getting conversation: {e}")
            return None
        finally:
            session.close()
    
    def get_user_conversations(self, user_id: str, limit: int = 10) -> List[Conversation]:
        """Get conversations for a user"""
        session = self.get_db_session()
        try:
            conversations = session.query(Conversation).filter(
                Conversation.user_id == user_id,
                Conversation.is_active == True
            ).order_by(Conversation.updated_at.desc()).limit(limit).all()
            return conversations
        except SQLAlchemyError as e:
            logger.error(f"Error getting user conversations: {e}")
            return []
        finally:
            session.close()
    
    def add_message(self, conversation_id: str, role: str, content: str, 
                   intent: str = None, confidence: float = None, 
                   entities: Dict = None) -> Message:
        """Add a message to a conversation"""
        session = self.get_db_session()
        try:
            message = Message(
                conversation_id=conversation_id,
                message_id=generate_message_id(),
                role=role,
                content=content,
                intent=intent,
                confidence=int(confidence * 100) if confidence else None,
                entities=json.dumps(entities) if entities else None
            )
            session.add(message)
            
            # Update conversation timestamp
            conversation = session.query(Conversation).filter(
                Conversation.conversation_id == conversation_id
            ).first()
            if conversation:
                conversation.updated_at = datetime.utcnow()
            
            session.commit()
            logger.info(f"Added message to conversation {conversation_id}")
            return message
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Error adding message: {e}")
            raise
        finally:
            session.close()
    
    def get_conversation_messages(self, conversation_id: str, limit: int = 50) -> List[Message]:
        """Get messages for a conversation"""
        session = self.get_db_session()
        try:
            messages = session.query(Message).filter(
                Message.conversation_id == conversation_id
            ).order_by(Message.created_at.desc()).limit(limit).all()
            return list(reversed(messages))  # Return in chronological order
        except SQLAlchemyError as e:
            logger.error(f"Error getting conversation messages: {e}")
            return []
        finally:
            session.close()
    
    def get_conversation_history(self, conversation_id: str, limit: int = 10) -> List[Dict]:
        """Get conversation history as a list of message dictionaries"""
        messages = self.get_conversation_messages(conversation_id, limit)
        history = []
        for message in messages:
            history.append({
                'role': message.role,
                'content': message.content,
                'timestamp': message.created_at.isoformat(),
                'intent': message.intent,
                'confidence': message.confidence / 100 if message.confidence else None,
                'entities': json.loads(message.entities) if message.entities else None
            })
        return history
    
    def close_conversation(self, conversation_id: str) -> bool:
        """Mark a conversation as inactive"""
        session = self.get_db_session()
        try:
            conversation = session.query(Conversation).filter(
                Conversation.conversation_id == conversation_id
            ).first()
            if conversation:
                conversation.is_active = False
                session.commit()
                logger.info(f"Closed conversation: {conversation_id}")
                return True
            return False
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Error closing conversation: {e}")
            return False
        finally:
            session.close()
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """Delete a conversation and all its messages"""
        session = self.get_db_session()
        try:
            conversation = session.query(Conversation).filter(
                Conversation.conversation_id == conversation_id
            ).first()
            if conversation:
                session.delete(conversation)
                session.commit()
                logger.info(f"Deleted conversation: {conversation_id}")
                return True
            return False
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Error deleting conversation: {e}")
            return False
        finally:
            session.close()
    
    def get_conversation_summary(self, conversation_id: str) -> Dict:
        """Get a summary of a conversation"""
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            return None
        
        messages = self.get_conversation_messages(conversation_id)
        
        return {
            'conversation_id': conversation.conversation_id,
            'title': conversation.title,
            'user_id': conversation.user_id,
            'created_at': conversation.created_at.isoformat(),
            'updated_at': conversation.updated_at.isoformat(),
            'is_active': conversation.is_active,
            'message_count': len(messages),
            'last_message': messages[-1].content if messages else None,
            'last_message_time': messages[-1].created_at.isoformat() if messages else None
        } 