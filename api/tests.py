import unittest
from unittest.mock import patch, MagicMock
import json
from app import app
import bcrypt

class TestAuthAPI(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    @patch('bcrypt.hashpw')
    @patch('bcrypt.gensalt')
    @patch('psycopg2.connect')
    def test_register_user_success(self, mock_connect, mock_gensalt, mock_hashpw):
        # Mock bcrypt
        mock_gensalt.return_value = b'fake_salt'
        mock_hashpw.return_value = b'hashed_password'
        
        # Mock database connection
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.__enter__.return_value = mock_cursor
        
        # Mock database responses
        mock_cursor.fetchone.side_effect = [
            None,  # No existing email
            (1,),  # User type ID
            (1,),  # New user ID
        ]

        test_data = {
            "user_name": "Test User",
            "user_email": "test@example.com",
            "user_password": "password123",
            "user_address": "123 Test St",
            "user_type": "customer"
        }

        response = self.app.post('/api/register',
                               data=json.dumps(test_data),
                               content_type='application/json')
        
        self.assertEqual(response.status_code, 201)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['user_id'], 1)
        self.assertEqual(response_data['user_type'], 1)

    @patch('psycopg2.connect')
    def test_register_user_email_exists(self, mock_connect):
        # Mock database connection
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.__enter__.return_value = mock_cursor
        
        # Mock existing email
        mock_cursor.fetchone.return_value = [(1, "existing@example.com")]

        test_data = {
            "user_name": "Test User",
            "user_email": "existing@example.com",
            "user_password": "password123",
            "user_address": "123 Test St",
            "user_type": "customer"
        }

        response = self.app.post('/api/register',
                               data=json.dumps(test_data),
                               content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.data)
        self.assertIn('error', response_data)
        self.assertIn('Email already exists', response_data['error'])

    @patch('bcrypt.checkpw')
    @patch('psycopg2.connect')
    def test_login_user_success(self, mock_connect, mock_checkpw):
        # Mock database connection
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.__enter__.return_value = mock_cursor
        
        # Mock user found and correct password
        mock_cursor.fetchone.return_value = (1, "Test User", "test@example.com", "hashed_password", "123 Test St", 1)
        mock_checkpw.return_value = True

        test_data = {
            "user_email": "test@example.com",
            "user_password": "password123"
        }

        response = self.app.post('/api/login',
                               data=json.dumps(test_data),
                               content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['user_id'], 1)
        self.assertEqual(response_data['user_type'], 1)

    @patch('psycopg2.connect')
    def test_login_user_not_found(self, mock_connect):
        # Mock database connection
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.__enter__.return_value = mock_cursor
        
        # Mock user not found
        mock_cursor.fetchone.return_value = None

        test_data = {
            "user_email": "nonexistent@example.com",
            "user_password": "password123"
        }

        response = self.app.post('/api/login',
                               data=json.dumps(test_data),
                               content_type='application/json')
        
        self.assertEqual(response.status_code, 404)
        response_data = json.loads(response.data)
        self.assertIn('error', response_data)
        self.assertEqual(response_data['error'], 'User not found')

    @patch('psycopg2.connect')
    def test_get_user_info_success(self, mock_connect):
        # Mock database connection
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.__enter__.return_value = mock_cursor
        
        # Mock user data
        mock_cursor.fetchone.return_value = (1, "Test User", "test@example.com", "hashed_password", "123 Test St", 1)

        response = self.app.get('/api/getUserInfo?user_id=1')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['user_name'], "Test User")
        self.assertEqual(response_data['user_email'], "test@example.com")
        self.assertEqual(response_data['adress'], "123 Test St")
        self.assertEqual(response_data['user_type'], 1)

    @patch('psycopg2.connect')
    def test_get_user_info_not_found(self, mock_connect):
        # Mock database connection
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.__enter__.return_value = mock_cursor
        
        # Mock user not found
        mock_cursor.fetchone.return_value = None

        response = self.app.get('/api/getUserInfo?user_id=999')
        
        self.assertEqual(response.status_code, 404)
        response_data = json.loads(response.data)
        self.assertIn('error', response_data)
        self.assertEqual(response_data['error'], 'User not found')

if __name__ == '__main__':
    unittest.main()