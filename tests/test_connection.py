"""
Tests for the database connection module
"""

import os
import unittest
from unittest.mock import patch, MagicMock

from travel_orm.connection import DatabaseConnection, test_connection


class TestDatabaseConnection(unittest.TestCase):
    """Test cases for DatabaseConnection class"""
    
    @patch('travel_orm.connection.boto3.client')
    def test_get_db_credentials_with_arn(self, mock_boto3_client):
        """Test getting DB credentials with ARN"""
        # Setup mock
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client
        mock_client.get_secret_value.return_value = {
            'SecretString': '{"username": "test_user", "password": "test_pass", "host": "test_host", "port": 5432}'
        }
        
        # Test with ARN
        with patch.dict(os.environ, {'DB_SECRET_ARN': 'test_arn'}):
            creds = DatabaseConnection._get_db_credentials()
            
            # Verify
            mock_boto3_client.assert_called_once_with('secretsmanager')
            mock_client.get_secret_value.assert_called_once_with(SecretId='test_arn')
            self.assertEqual(creds['username'], 'test_user')
            self.assertEqual(creds['password'], 'test_pass')
            self.assertEqual(creds['host'], 'test_host')
            self.assertEqual(creds['port'], 5432)
    
    @patch('travel_orm.connection.boto3.client')
    def test_get_db_credentials_with_name(self, mock_boto3_client):
        """Test getting DB credentials with name"""
        # Setup mock
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client
        mock_client.get_secret_value.return_value = {
            'SecretString': '{"username": "test_user", "password": "test_pass", "host": "test_host", "port": 5432}'
        }
        
        # Test with name
        with patch.dict(os.environ, {'DB_SECRET_NAME': 'test_name'}):
            creds = DatabaseConnection._get_db_credentials()
            
            # Verify
            mock_boto3_client.assert_called_once_with('secretsmanager')
            mock_client.get_secret_value.assert_called_once_with(SecretId='test_name')
            self.assertEqual(creds['username'], 'test_user')
    
    @patch('travel_orm.connection.DatabaseConnection._get_db_credentials')
    @patch('travel_orm.connection.create_engine')
    @patch('travel_orm.connection.sessionmaker')
    @patch('travel_orm.connection.scoped_session')
    def test_initialize(self, mock_scoped_session, mock_sessionmaker, mock_create_engine, mock_get_creds):
        """Test database initialization"""
        # Setup mocks
        mock_get_creds.return_value = {
            'username': 'test_user',
            'password': 'test_pass',
            'host': 'test_host',
            'port': 5432
        }
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine
        mock_session_factory = MagicMock()
        mock_sessionmaker.return_value = mock_session_factory
        mock_scoped_session.return_value = mock_session_factory
        
        # Test initialization
        with patch.dict(os.environ, {'DB_NAME': 'test_db'}):
            DatabaseConnection._initialize()
            
            # Verify
            mock_get_creds.assert_called_once()
            mock_create_engine.assert_called_once_with('postgresql://test_user:test_pass@test_host:5432/test_db')
            mock_sessionmaker.assert_called_once_with(bind=mock_engine)
            mock_scoped_session.assert_called_once_with(mock_session_factory)
            self.assertEqual(DatabaseConnection._engine, mock_engine)
            self.assertEqual(DatabaseConnection._session_factory, mock_session_factory)
    
    @patch('travel_orm.connection.DatabaseConnection.get_session_factory')
    def test_session_scope(self, mock_get_session_factory):
        """Test session scope context manager"""
        # Setup mock
        mock_session = MagicMock()
        mock_session_factory = MagicMock()
        mock_session_factory.return_value = mock_session
        mock_get_session_factory.return_value = mock_session_factory
        
        # Test successful transaction
        with DatabaseConnection.session_scope() as session:
            self.assertEqual(session, mock_session)
        
        # Verify
        mock_session.commit.assert_called_once()
        mock_session.close.assert_called_once()
        mock_session.rollback.assert_not_called()
        
        # Reset mocks
        mock_session.reset_mock()
        
        # Test transaction with exception
        try:
            with DatabaseConnection.session_scope() as session:
                raise ValueError("Test exception")
        except ValueError:
            pass
        
        # Verify
        mock_session.rollback.assert_called_once()
        mock_session.close.assert_called_once()
        mock_session.commit.assert_not_called()
    
    @patch('travel_orm.connection.DatabaseConnection.session_scope')
    def test_test_connection(self, mock_session_scope):
        """Test the test_connection function"""
        # Setup mock
        mock_session = MagicMock()
        mock_result = MagicMock()
        mock_result.fetchone.return_value = ["PostgreSQL 15.3"]
        mock_session.execute.return_value = mock_result
        
        # Mock context manager
        mock_context = MagicMock()
        mock_context.__enter__.return_value = mock_session
        mock_session_scope.return_value = mock_context
        
        # Test successful connection
        result = test_connection()
        
        # Verify
        self.assertIn("Successfully connected to PostgreSQL", result)
        self.assertIn("15.3", result)
        mock_session.execute.assert_called_once()
        
        # Test connection failure
        mock_session.execute.side_effect = Exception("Connection failed")
        result = test_connection()
        
        # Verify
        self.assertIn("Failed to connect to database", result)
        self.assertIn("Connection failed", result)


if __name__ == '__main__':
    unittest.main()
