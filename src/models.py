from sqlalchemy import Column, ForeignKey, Integer, Text, DateTime, String
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class AnonymousMessage(Base):
    __tablename__ = "anonymous_messages"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    message_text = Column(Text, nullable=True)
    media_type = Column(String(20), nullable=True)  # 'photo', 'video', None
    media_file_id = Column(Text, nullable=True)  # Telegram file_id
    caption = Column(Text, nullable=True)  # Подпись к медиа
    created_at = Column(DateTime, default=datetime.utcnow)
    admin_thread_id = Column(Integer)

class AdminReply(Base):
    __tablename__ = "admin_replies"
    
    id = Column(Integer, primary_key=True)
    message_id = Column(Integer, ForeignKey('anonymous_messages.id'))
    reply_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)