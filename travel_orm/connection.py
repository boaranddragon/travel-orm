"""
Database connection management for TravelORM
"""

import json
import logging
import os
import boto3
from contextlib import contextmanager
from botocore.exceptions import ClientError
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, scoped_session

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class DatabaseConnection:
    """
    Singleton class for managing database connections
    """
    _instance = None
    _engine = None
    _session_factory = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
        return cls._instance
    
    @classmethod
    def get_engine(cls):
        """
        Get the SQLAlchemy engine, initializing if necessary
        
        Returns:
            Engine: SQLAlchemy engine
        """
        if cls._engine is None:
            cls._initialize()
        return cls._engine
    
    @classmethod
    def get_session_factory(cls):
        """
        Get the SQLAlchemy session factory, initializing if necessary
        
        Returns:
            scoped_session: Session factory
        """
        if cls._session_factory is None:
            cls._initialize()
        return cls._session_factory
    
    @classmethod
    def _get_db_credentials(cls, secret_arn=None):
        """
        Get database credentials from AWS Secrets Manager
        
        Args:
            secret_arn (str): ARN of the secret containing database credentials
            
        Returns:
            dict: Database credentials
        """
        # For testing purposes, use hardcoded credentials if environment variables are not set
        if os.environ.get('USE_HARDCODED_CREDENTIALS', 'false').lower() == 'true':
            logger.info("Using hardcoded credentials for testing")
            return {
                'username': os.environ.get('DB_USERNAME', 'postgres'),
                'password': os.environ.get('DB_PASSWORD', ''),
                'host': os.environ.get('DB_HOST', ''),
                'port': int(os.environ.get('DB_PORT', '5432'))
            }
            
        secret_arn = secret_arn or os.environ.get('DB_SECRET_ARN')
        secret_name = os.environ.get('DB_SECRET_NAME', 'travel-itinerary-db-credentials')
        
        if not secret_arn and not secret_name:
            raise ValueError("Either DB_SECRET_ARN or DB_SECRET_NAME environment variable must be set")
            
        client = boto3.client('secretsmanager')
        try:
            if secret_arn:
                response = client.get_secret_value(SecretId=secret_arn)
            else:
                response = client.get_secret_value(SecretId=secret_name)
                
            return json.loads(response['SecretString'])
        except ClientError as e:
            logger.error(f"Error retrieving database credentials: {str(e)}")
            raise
    
    @classmethod
    def _initialize(cls, secret_arn=None, db_name=None):
        """
        Initialize the database connection using SQLAlchemy
        
        Args:
            secret_arn (str): ARN of the secret containing database credentials
            db_name (str): Name of the database to connect to
        """
        try:
            # Get credentials from Secrets Manager
            creds = cls._get_db_credentials(secret_arn)
            db_name = db_name or os.environ.get('DB_NAME', 'travel_itinerary')
            
            # Create connection string using pg8000 instead of psycopg2
            conn_string = f"postgresql+pg8000://{creds['username']}:{creds['password']}@{creds['host']}:{creds.get('port', 5432)}/{db_name}"
            
            # Create engine
            cls._engine = create_engine(conn_string)
            
            # Create session factory
            cls._session_factory = scoped_session(sessionmaker(bind=cls._engine))
            
            logger.info("SQLAlchemy engine and session initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing database connection: {str(e)}")
            raise
    
    @classmethod
    @contextmanager
    def session_scope(cls):
        """
        Provide a transactional scope around a series of operations.
        
        Yields:
            Session: SQLAlchemy session
        """
        session = cls.get_session_factory()()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Error in database transaction: {str(e)}")
            raise
        finally:
            session.close()


def test_connection():
    """
    Test the database connection using SQLAlchemy
    
    Returns:
        str: Success message with database version or error message
    """
    try:
        with DatabaseConnection.session_scope() as session:
            result = session.execute(text("SELECT version()")).fetchone()
        return f"Successfully connected to PostgreSQL via SQLAlchemy. Version: {result[0]}"
    except Exception as e:
        return f"Failed to connect to database via SQLAlchemy: {str(e)}"
