import unittest
import json
from unittest.mock import patch
from app import app, db, Test  # Assuming app code is in app.py

class TestServiceTestCase(unittest.TestCase):
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

    @patch('requests.post')
    def test_create_test(self, mock_post):
        # Mock the token verification response
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {'data': {'level_of_access': 3}}

        response = self.client.post('/create', json={'data': 'Test data'}, headers={'Authorization': 'Bearer validtoken'})
        self.assertEqual(response.status_code, 201)
        self.assertIn(b'Test created', response.data)

        # Verify that the test is stored in the database
        with self.app.app_context():
            test_entry = Test.query.first()
            self.assertIsNotNone(test_entry)
            self.assertEqual(test_entry.data, 'Test data')

    @patch('requests.post')
    def test_create_test_access_denied(self, mock_post):
        # Mock the token verification response
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {'data': {'level_of_access': 2}}

        response = self.client.post('/create', json={'data': 'Test data'}, headers={'Authorization': 'Bearer validtoken'})
        self.assertEqual(response.status_code, 403)
        self.assertIn(b'Access denied', response.data)

    @patch('requests.post')
    def test_read_all_tests(self, mock_post):
        # Mock the token verification response
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {'data': {'level_of_access': 3}}

        # Create a test entry
        with self.app.app_context():
            test_entry = Test(data='Test data')
            db.session.add(test_entry)
            db.session.commit()

        response = self.client.get('/readAll', headers={'Authorization': 'Bearer validtoken'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(json.loads(response.data)), 1)

    @patch('requests.post')
    def test_read_one_test(self, mock_post):
        # Mock the token verification response
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {'data': {'level_of_access': 3}}

        # Create a test entry
        with self.app.app_context():
            test_entry = Test(data='Test data')
            db.session.add(test_entry)
            db.session.commit()

        response = self.client.get('/readOne/1', headers={'Authorization': 'Bearer validtoken'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test data', response.data)

    @patch('requests.post')
    def test_update_test(self, mock_post):
        # Mock the token verification response
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {'data': {'level_of_access': 3}}

        # Create a test entry
        with self.app.app_context():
            test_entry = Test(data='Test data')
            db.session.add(test_entry)
            db.session.commit()

        response = self.client.put('/update/1', json={'data': 'Updated test data'}, headers={'Authorization': 'Bearer validtoken'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test updated', response.data)

        # Verify the update
        response = self.client.get('/readOne/1', headers={'Authorization': 'Bearer validtoken'})
        self.assertIn(b'Updated test data', response.data)

    @patch('requests.post')
    def test_update_test_access_denied(self, mock_post):
        # Mock the token verification response
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {'data': {'level_of_access': 2}}

        # Create a test entry
        with self.app.app_context():
            test_entry = Test(data='Test data')
            db.session.add(test_entry)
            db.session.commit()

        response = self.client.put('/update/1', json={'data': 'Updated test data'}, headers={'Authorization': 'Bearer validtoken'})
        self.assertEqual(response.status_code, 403)
        self.assertIn(b'Access denied', response.data)

    @patch('requests.post')
    def test_delete_test(self, mock_post):
        # Mock the token verification response
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {'data': {'level_of_access': 3}}

        # Create a test entry
        with self.app.app_context():
            test_entry = Test(data='Test data')
            db.session.add(test_entry)
            db.session.commit()

        response = self.client.delete('/delete/1', headers={'Authorization': 'Bearer validtoken'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test deleted', response.data)

        # Verify the deletion
        response = self.client.get('/readOne/1', headers={'Authorization': 'Bearer validtoken'})
        self.assertEqual(response.status_code, 404)

    @patch('requests.post')
    def test_delete_test_access_denied(self, mock_post):
        # Mock the token verification response
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {'data': {'level_of_access': 2}}

        # Create a test entry
        with self.app.app_context():
            test_entry = Test(data='Test data')
            db.session.add(test_entry)
            db.session.commit()

        response = self.client.delete('/delete/1', headers={'Authorization': 'Bearer validtoken'})
        self.assertEqual(response.status_code, 403)
        self.assertIn(b'Access denied', response.data)

    def test_hi(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test service OK!', response.data)

if __name__ == '__main__':
    unittest.main()s