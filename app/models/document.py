# app/models/document.py
from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
import datetime
from app.db.base import Base

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(Text)
    file_path = Column(String)
    summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="documents")