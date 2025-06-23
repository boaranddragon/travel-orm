"""
SQLAlchemy models for the Travel Itinerary database
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Date, Integer, ForeignKey, Text, ARRAY, text
from sqlalchemy.dialects.postgresql import UUID, ENUM
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from .connection import DatabaseConnection

# Create the base model class
Base = declarative_base()

# Define enum types
item_type_enum = ENUM('info', 'food', 'hotel', 'activity', 'transport', 
                      name='item_type', create_type=False)
data_source_type_enum = ENUM('email', 'file', 'api', 'manual', 
                             name='data_source_type', create_type=False)

# Base model class
class Model:
    """
    Base model class with CRUD operations
    """
    @classmethod
    def create(cls, **kwargs):
        """
        Create a new record
        
        Args:
            **kwargs: Model attributes
            
        Returns:
            Model: Created record
        """
        with DatabaseConnection.session_scope() as session:
            instance = cls(**kwargs)
            session.add(instance)
            session.flush()  # Flush to get the ID
            session.refresh(instance)
            # Create a copy of the instance to return after the session is closed
            instance_copy = cls(**{
                k: getattr(instance, k) 
                for k in kwargs.keys() if hasattr(instance, k)
            })
            # Copy the ID
            setattr(instance_copy, 'id', getattr(instance, 'id'))
            return instance_copy
    
    @classmethod
    def get_by_id(cls, id):
        """
        Get a record by ID
        
        Args:
            id: Primary key value
            
        Returns:
            Model: Record or None if not found
        """
        with DatabaseConnection.session_scope() as session:
            instance = session.query(cls).get(id)
            if instance:
                # Create a copy of the instance to return after the session is closed
                instance_copy = cls()
                for column in instance.__table__.columns:
                    setattr(instance_copy, column.name, getattr(instance, column.name))
                return instance_copy
            return None
    
    @classmethod
    def list_all(cls, limit=None):
        """
        List all records
        
        Args:
            limit (int, optional): Maximum number of records to return
            
        Returns:
            list: List of records
        """
        with DatabaseConnection.session_scope() as session:
            query = session.query(cls)
            if limit is not None:
                query = query.limit(limit)
            
            results = query.all()
            
            # Create copies of the instances to return after the session is closed
            copies = []
            for instance in results:
                instance_copy = cls()
                for column in instance.__table__.columns:
                    setattr(instance_copy, column.name, getattr(instance, column.name))
                copies.append(instance_copy)
                
            return copies
    
    def update(self, **kwargs):
        """
        Update record attributes
        
        Args:
            **kwargs: Attributes to update
            
        Returns:
            Model: Updated record
        """
        with DatabaseConnection.session_scope() as session:
            # Get a fresh instance from the database
            instance = session.query(self.__class__).get(self.id)
            if not instance:
                raise ValueError(f"Instance with id {self.id} not found")
                
            # Update attributes
            for key, value in kwargs.items():
                setattr(instance, key, value)
                
            # Also update the current instance
            for key, value in kwargs.items():
                setattr(self, key, value)
                
            session.flush()
            session.refresh(instance)
            return self
    
    def delete(self):
        """
        Delete the record
        
        Args:
            self: Model instance
            
        Returns:
            bool: True if deleted
        """
        with DatabaseConnection.session_scope() as session:
            # Get a fresh instance from the database
            instance = session.query(self.__class__).get(self.id)
            if instance:
                session.delete(instance)
                return True
            return False
    
    @classmethod
    def execute_query(cls, query_func):
        """
        Execute a custom query function
        
        Args:
            query_func: Function that takes a session and returns a query result
            
        Returns:
            Any: Query result
        """
        with DatabaseConnection.session_scope() as session:
            result = query_func(session)
            
            # If the result is a list of model instances, create copies
            if isinstance(result, list) and len(result) > 0 and hasattr(result[0], '__table__'):
                copies = []
                for instance in result:
                    instance_copy = instance.__class__()
                    for column in instance.__table__.columns:
                        setattr(instance_copy, column.name, getattr(instance, column.name))
                    copies.append(instance_copy)
                return copies
            
            return result


class TravelAdvisor(Base, Model):
    """SQLAlchemy model for travel_advisors table"""
    __tablename__ = 'travel_advisors'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    phone_number = Column(String(50))
    website = Column(String(255))
    profile_image = Column(String(255))
    company_name = Column(String(255))
    company_logo = Column(String(255))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    itineraries = relationship("Itinerary", back_populates="travel_advisor")
    
    def __repr__(self):
        return f"<TravelAdvisor(id='{self.id}', name='{self.name}', company='{self.company_name}')>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': str(self.id),
            'name': self.name,
            'phone_number': self.phone_number,
            'website': self.website,
            'profile_image': self.profile_image,
            'company_name': self.company_name,
            'company_logo': self.company_logo,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Itinerary(Base, Model):
    """SQLAlchemy model for itineraries table"""
    __tablename__ = 'itineraries'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    travel_advisor_id = Column(UUID(as_uuid=True), ForeignKey('travel_advisors.id'), nullable=False)
    start_date = Column(Date, nullable=False)
    duration = Column(Integer, nullable=False)
    destination = Column(String(255), nullable=False)
    cover_image = Column(String(255))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    travel_advisor = relationship("TravelAdvisor", back_populates="itineraries", foreign_keys=[travel_advisor_id])
    days = relationship("Day", back_populates="itinerary", cascade="all, delete-orphan")
    information_documents = relationship("InformationDocument", back_populates="itinerary", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Itinerary(id='{self.id}', destination='{self.destination}', start_date='{self.start_date}')>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': str(self.id),
            'travel_advisor_id': str(self.travel_advisor_id),
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'duration': self.duration,
            'destination': self.destination,
            'cover_image': self.cover_image,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class DataSource(Base, Model):
    """SQLAlchemy model for data_sources table"""
    __tablename__ = 'data_sources'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    received_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    processed_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    type = Column(data_source_type_enum, nullable=False)
    url = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    information_documents = relationship("InformationDocument", back_populates="data_source")
    itinerary_items = relationship("ItineraryItem", back_populates="data_source")
    
    def __repr__(self):
        return f"<DataSource(id='{self.id}', type='{self.type}')>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': str(self.id),
            'received_at': self.received_at.isoformat() if self.received_at else None,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None,
            'type': self.type,
            'url': self.url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class InformationDocument(Base, Model):
    """SQLAlchemy model for information_documents table"""
    __tablename__ = 'information_documents'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    itinerary_id = Column(UUID(as_uuid=True), ForeignKey('itineraries.id'), nullable=False)
    data_source_id = Column(UUID(as_uuid=True), ForeignKey('data_sources.id'))
    index = Column(Integer, nullable=False)
    title = Column(String(255), nullable=False)
    text = Column(Text)
    formatted_text = Column(Text)
    photos = Column(ARRAY(String))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    itinerary = relationship("Itinerary", back_populates="information_documents")
    data_source = relationship("DataSource", back_populates="information_documents")
    
    def __repr__(self):
        return f"<InformationDocument(id='{self.id}', title='{self.title}')>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': str(self.id),
            'itinerary_id': str(self.itinerary_id),
            'data_source_id': str(self.data_source_id) if self.data_source_id else None,
            'index': self.index,
            'title': self.title,
            'text': self.text,
            'formatted_text': self.formatted_text,
            'photos': self.photos,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Day(Base, Model):
    """SQLAlchemy model for days table"""
    __tablename__ = 'days'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    itinerary_id = Column(UUID(as_uuid=True), ForeignKey('itineraries.id'), nullable=False)
    indices = Column(ARRAY(Integer), nullable=False)
    title = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    itinerary = relationship("Itinerary", back_populates="days")
    itinerary_items = relationship("ItineraryItem", back_populates="day", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Day(id='{self.id}', itinerary_id='{self.itinerary_id}', index={self.index})>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': str(self.id),
            'itinerary_id': str(self.itinerary_id),
            'index': self.index,
            'title': self.title,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class ItineraryItem(Base, Model):
    """SQLAlchemy model for itinerary_items table"""
    __tablename__ = 'itinerary_items'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    day_id = Column(UUID(as_uuid=True), ForeignKey('days.id'), nullable=True)  # Allow NULL per Phase B requirements
    data_source_id = Column(UUID(as_uuid=True), ForeignKey('data_sources.id'))  # Updated FK reference
    index = Column(Integer, nullable=False)
    title = Column(String(255), nullable=False)
    type = Column(item_type_enum, nullable=False)
    detail_text = Column(Text)
    photos = Column(ARRAY(String))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    day = relationship("Day", back_populates="itinerary_items")
    data_source = relationship("DataSource", back_populates="itinerary_items")
    
    def __repr__(self):
        return f"<ItineraryItem(id='{self.id}', day_id='{self.day_id}', type='{self.type}', title='{self.title}')>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': str(self.id),
            'day_id': str(self.day_id),
            'data_source_id': str(self.data_source_id) if self.data_source_id else None,
            'index': self.index,
            'title': self.title,
            'type': self.type,
            'detail_text': self.detail_text,
            'photos': self.photos,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
