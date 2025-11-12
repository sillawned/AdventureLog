"""User model for authentication and profile data."""

from sqlalchemy import Boolean, Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base


class User(Base):
    """User model for local authentication and profile data."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(150), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    
    # Profile fields
    first_name = Column(String(150), nullable=True)
    last_name = Column(String(150), nullable=True)
    
    # Status fields
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    # Relationships
    immich_integrations = relationship("ImmichIntegration", back_populates="user", cascade="all, delete-orphan")
    strava_tokens = relationship("StravaToken", back_populates="user", cascade="all, delete-orphan")
    wanderer_integrations = relationship("WandererIntegration", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"
