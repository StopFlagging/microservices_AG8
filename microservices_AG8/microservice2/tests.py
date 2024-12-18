import unittest
import json
from unittest.mock import patch
from app import app, db, Token  # Assuming app code is in app.py
import jwt

class JWTServiceTestCase(unittest.TestCase):
    def setUp(self):
        # Set up the test client and the database
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Use in-memory database for testing
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        # Clean up the database after each test
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    @patch('requests.get')
    def test_generate_jwt(self, mock_get):
        # Mock the response from the external service
        mock_get.return_value.json.return_value = [
            {'id': 1, 'name': 'testuser', 'password': 'password123', 'level_of_access': 1}
        ]

        response = self.client.post('/generate', json={
            'name': 'testuser',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 201)
        self.assertIn('token', json.loads(response.data))

        # Verify that the token is stored in the database
        with self.app.app_context():
            token_entry = Token.query.first()
            self.assertIsNotNone(token_entry)
            self.assertEqual(token_entry.token, json.loads(response.data)['token'])

    @patch('requests.get')
    def test_generate_jwt_invalid_credentials(self, mock_get):
        # Mock the response from the external service
        mock_get.return_value.json.return_value = [
            {'id': 1, 'name': 'testuser', 'password': 'password123', 'level_of_access': 1}
        ]

        response = self.client.post('/generate', json={
            'name': 'testuser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 401)
        self.assertIn(b'Invalid credentials', response.data)

    def test_verify_jwt(self):
        # Generate a token manually for testing
        token = jwt.encode({'id': 1, 'level_of_access': 1, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, 'secret', algorithm='HS256')

        response = self.client.post('/verify', json={'token': token})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Token is valid', response.data)

    def test_verify_jwt_expired(self):
        # Generate an expired token
        token = jwt.encode({'id': 1, 'level_of_access': 1, 'exp': datetime.datetime.utcnow() - datetime.timedelta(minutes=1)}, 'secret', algorithm='HS256')

        response = self.client.post('/verify', json={'token': token})
        self.assertEqual(response.status_code, 401)
        self.assertIn(b'Token has expired', response.data)

    def test_verify_jwt_invalid(self):
        response = self.client.post('/verify', json={'token': 'invalidtoken'})
        self.assertEqual(response.status_code, 401)
        self.assertIn(b'Invalid token', response.data)

    def test_hi(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'JWT service OK!', response.data)

if __name__ == '__main__':
    unittest.main()