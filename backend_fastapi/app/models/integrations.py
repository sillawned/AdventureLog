"""Integration models for external services."""

import uuid
from sqlalchemy import Column, Integer, String, Boolean, BigInteger, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from .base import Base


class ImmichIntegration(Base):
    """Immich photo service integration."""
    
    __tablename__ = "immich_integrations"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    server_url = Column(String(255), nullable=False)
    api_key = Column(String(255), nullable=False)
    copy_locally = Column(
        Boolean, 
        default=True, 
        nullable=False,
        comment="Copy image to local storage instead of just linking"
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    user = relationship("User", back_populates="immich_integrations")


class StravaToken(Base):
    """Strava OAuth tokens."""
    
    __tablename__ = "strava_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    access_token = Column(String(255), nullable=False)
    refresh_token = Column(String(255), nullable=False)
    expires_at = Column(BigInteger, nullable=False)  # Unix timestamp
    athlete_id = Column(BigInteger, nullable=True)
    scope = Column(String(255), nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    user = relationship("User", back_populates="strava_tokens")


class WandererIntegration(Base):
    """Wanderer hiking app integration."""
    
    __tablename__ = "wanderer_integrations"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    server_url = Column(String(255), nullable=False)
    username = Column(String(255), nullable=False)
    token = Column(String(512), nullable=True)
    token_expiry = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    user = relationship("User", back_populates="wanderer_integrations")
