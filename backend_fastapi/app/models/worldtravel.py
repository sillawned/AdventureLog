"""WorldTravel models - countries, regions, cities, and visited tracking."""
from sqlalchemy import Column, Integer, String, ForeignKey, Numeric, UniqueConstraint
from sqlalchemy.orm import relationship
from .base import Base


class Country(Base):
    """Country model - read-only reference data."""
    __tablename__ = "countries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    country_code = Column(String(2), unique=True, nullable=False, index=True)  # ISO2
    subregion = Column(String(100), nullable=True)
    capital = Column(String(100), nullable=True)
    latitude = Column(Numeric(9, 6), nullable=True)
    longitude = Column(Numeric(9, 6), nullable=True)
    
    regions = relationship("Region", back_populates="country")


class Region(Base):
    """Region/State model - read-only reference data."""
    __tablename__ = "regions"

    id = Column(String(50), primary_key=True)  # string ID from source data
    name = Column(String(100), nullable=False)
    country_id = Column(Integer, ForeignKey("countries.id", ondelete="CASCADE"), nullable=False, index=True)
    latitude = Column(Numeric(9, 6), nullable=True)
    longitude = Column(Numeric(9, 6), nullable=True)
    
    country = relationship("Country", back_populates="regions")
    cities = relationship("City", back_populates="region")


class City(Base):
    """City model - read-only reference data."""
    __tablename__ = "cities"

    id = Column(String(50), primary_key=True)  # string ID from source data
    name = Column(String(100), nullable=False)
    region_id = Column(String(50), ForeignKey("regions.id", ondelete="CASCADE"), nullable=False, index=True)
    latitude = Column(Numeric(9, 6), nullable=True)
    longitude = Column(Numeric(9, 6), nullable=True)
    
    region = relationship("Region", back_populates="cities")


class VisitedRegion(Base):
    """User's visited regions tracking."""
    __tablename__ = "visited_regions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    region_id = Column(String(50), ForeignKey("regions.id", ondelete="CASCADE"), nullable=False, index=True)
    
    __table_args__ = (
        UniqueConstraint('user_id', 'region_id', name='unique_user_region'),
    )


class VisitedCity(Base):
    """User's visited cities tracking."""
    __tablename__ = "visited_cities"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    city_id = Column(String(50), ForeignKey("cities.id", ondelete="CASCADE"), nullable=False, index=True)
    
    __table_args__ = (
        UniqueConstraint('user_id', 'city_id', name='unique_user_city'),
    )
