import unittest
import json
from app import app, db, User  # Assuming app code is in app.py

class UserServiceTestCase(unittest.TestCase):
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

    def test_create_user(self):
        response = self.client.post('/create', json={
            'name': 'testuser',
            'password': 'password123',
            'level_of_access': 1
        })
        self.assertEqual(response.status_code, 201)
        self.assertIn(b'User   created', response.data)

    def test_read_all_users(self):
        self.client.post('/create', json={
            'name': 'testuser',
            'password': 'password123',
            'level_of_access': 1
        })
        response = self.client.get('/readAll')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(json.loads(response.data)), 1)

    def test_read_one_user(self):
        self.client.post('/create', json={
            'name': 'testuser',
            'password': 'password123',
            'level_of_access': 1
        })
        response = self.client.get('/readOne/1')
        self.assertEqual(response.status_code, 200)
        user_data = json.loads(response.data)
        self.assertEqual(user_data['name'], 'testuser')

    def test_update_user(self):
        self.client.post('/create', json={
            'name': 'testuser',
            'password': 'password123',
            'level_of_access': 1
        })
        response = self.client.put('/update/1', json={
            'name': 'updateduser',
            'password': 'newpassword',
            'level_of_access': 2
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'User   updated', response.data)

        # Verify the update
        response = self.client.get('/readOne/1')
        user_data = json.loads(response.data)
        self.assertEqual(user_data['name'], 'updateduser')

    def test_delete_user(self):
        self.client.post('/create', json={
            'name': 'testuser',
            'password': 'password123',
            'level_of_access': 1
        })
        response = self.client.delete('/delete/1')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'User   deleted', response.data)

        # Verify the user is deleted
        response = self.client.get('/readAll')
        self.assertEqual(len(json.loads(response.data)), 0)

    def test_hi(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'User  service OK!', response.data)

if __name__ == '__main__':
    unittest.main()