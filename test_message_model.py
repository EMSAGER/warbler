"""Message model tests"""

#test run path:
#   FLASK_ENV=production python -m unittest test_message_model.py


import os
from unittest import TestCase
from models import db, User, Message
from sqlalchemy.exc import DataError

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

class MessageModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client"""
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()

        User.query.delete()
        Message.query.delete()

        self.user = User.signup("testuser", "test@test.com", "password", None)
        db.session.add(self.user)
        db.session.commit()

        self.message = Message(text="Test message", user_id=self.user.id)
        db.session.add(self.message)
        db.session.commit()

    def tearDown(self):
        """Clean up any fouled transaction."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_message_creation(self):
        """Test that a message can be successfully created and is associated with the correct user."""
        with app.app_context():
            self.assertEqual(self.message.text, "Test message")
            self.assertEqual(self.message.user_id, self.user.id)

            # Retrieve the user associated with the message
            user = User.query.get(self.message.user_id)
            self.assertEqual(user.username, self.user.username)
    
    def test_message_retrieval(self):
        """Test the messages can be retrieved from the database"""
        with app.app_context():
            message = Message.query.first()
            self.assertIsNotNone(message)
            self.assertEqual(message.text, "Test message")

    def test_message_deletion(self):
        """Test that a message can be deleted"""
        with app.app_context():
            message_id = self.message.id
            Message.query.filter_by(id=message_id).delete()
            db.session.commit()

            message = Message.query.get(message_id)
            self.assertIsNone(message)
    
    def test_message_text_length_validation(self):
        """Test that a message cannot exceed 140 characters."""
            # Create a string that is too long
        with app.app_context():
            long_text = "x" * 141  # Create a string that is too long
            message = Message(text=long_text, user_id=self.user.id)
            db.session.add(message)
            with self.assertRaises(DataError):  
                db.session.commit()

    def test_user_message_relationship(self):
        """Test that a user's messages are correctly associated."""
        with app.app_context():
            user = User.query.first()
            message = Message.query.first()

            self.assertIn(message, user.messages)
            self.assertEqual(message.user, user)

    def test_message_belongs_to_user(self):
        """Test that a message is associated with the correct user."""
        with app.app_context():
            message = Message.query.first()
            self.assertEqual(message.user_id, self.user.id)
            self.assertEqual(message.user.username, self.user.username)
