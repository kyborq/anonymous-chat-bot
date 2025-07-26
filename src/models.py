from sqlalchemy import Column, ForeignKey, Integer, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class AnonymousMessage(Base):
    __tablename__ = "anonymous_messages"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    message_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    admin_thread_id = Column(Integer)

class AdminReply(Base):
    __tablename__ = "admin_replies"
    
    id = Column(Integer, primary_key=True)
    message_id = Column(Integer, ForeignKey('anonymous_messages.id'))
    reply_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)