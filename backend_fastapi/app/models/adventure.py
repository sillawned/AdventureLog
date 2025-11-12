"""Adventure domain models - clean SQLAlchemy implementation."""
import uuid
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, Date, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from .base import Base


class Location(Base):
    """Location model - places a user has visited or wants to visit."""
    __tablename__ = "locations"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    rating = Column(Integer, nullable=True)
    tags = Column(ARRAY(String), nullable=True)
    is_public = Column(Boolean, default=False)
    link = Column(String(500), nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    collection_id = Column(PG_UUID(as_uuid=True), ForeignKey("collections.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    visits = relationship("Visit", back_populates="location", cascade="all, delete-orphan")
    category = relationship("Category", foreign_keys=[category_id])
    collection = relationship("Collection", foreign_keys=[collection_id])


class Visit(Base):
    """Visit model - represents a visit to a location."""
    __tablename__ = "visits"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    location_id = Column(PG_UUID(as_uuid=True), ForeignKey("locations.id", ondelete="CASCADE"), nullable=False)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    timezone = Column(String(50), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    location = relationship("Location", back_populates="visits")


class Collection(Base):
    """Collection model - grouping of locations."""
    __tablename__ = "collections"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    link = Column(String(500), nullable=True)
    is_archived = Column(Boolean, default=False)
    is_public = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Category(Base):
    """Category model - categorization of locations."""
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    icon = Column(String(50), nullable=True)
    color = Column(String(20), nullable=True)


class Transportation(Base):
    """Transportation model."""
    __tablename__ = "transportations"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    location_id = Column(PG_UUID(as_uuid=True), ForeignKey("locations.id", ondelete="CASCADE"), nullable=False)
    type = Column(String(100), nullable=True)
    from_location = Column(String(255), nullable=True)
    to_location = Column(String(255), nullable=True)
    depart_time = Column(DateTime(timezone=True), nullable=True)
    arrive_time = Column(DateTime(timezone=True), nullable=True)
    depart_timezone = Column(String(50), nullable=True)
    arrive_timezone = Column(String(50), nullable=True)
    depart_latitude = Column(Float, nullable=True)
    depart_longitude = Column(Float, nullable=True)
    arrive_latitude = Column(Float, nullable=True)
    arrive_longitude = Column(Float, nullable=True)
    link = Column(String(500), nullable=True)
    rating = Column(Integer, nullable=True)
    is_public = Column(Boolean, default=False)
    collection_id = Column(PG_UUID(as_uuid=True), ForeignKey("collections.id", ondelete="SET NULL"), nullable=True)


class Note(Base):
    """Note model - notes attached to locations."""
    __tablename__ = "notes"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    location_id = Column(PG_UUID(as_uuid=True), ForeignKey("locations.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    content = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Checklist(Base):
    """Checklist model."""
    __tablename__ = "checklists"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    location_id = Column(PG_UUID(as_uuid=True), ForeignKey("locations.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    
    items = relationship("ChecklistItem", back_populates="checklist", cascade="all, delete-orphan")


class ChecklistItem(Base):
    """Checklist item model."""
    __tablename__ = "checklist_items"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    checklist_id = Column(PG_UUID(as_uuid=True), ForeignKey("checklists.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    is_checked = Column(Boolean, default=False)
    
    checklist = relationship("Checklist", back_populates="items")


class Activity(Base):
    """Activity model."""
    __tablename__ = "activities"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    location_id = Column(PG_UUID(as_uuid=True), ForeignKey("locations.id", ondelete="CASCADE"), nullable=False)
    type = Column(String(100), nullable=True)
    date = Column(Date, nullable=True)


class Lodging(Base):
    """Lodging model."""
    __tablename__ = "lodgings"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    location_id = Column(PG_UUID(as_uuid=True), ForeignKey("locations.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)


class Trail(Base):
    """Trail model."""
    __tablename__ = "trails"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    location_id = Column(PG_UUID(as_uuid=True), ForeignKey("locations.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    difficulty = Column(String(50), nullable=True)
    length = Column(Float, nullable=True)
