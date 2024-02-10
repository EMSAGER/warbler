"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase
from flask import session
from models import db, connect_db, Message, User, Likes

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data



# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        db.drop_all()
        db.create_all()

        User.query.delete()
        Message.query.delete()


        self.u1 = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)
        
        db.session.add(self.u1)

        self.u2 = User.signup(username="testuser2",
                                    email="test2@test.com",
                                    password="testuser2",
                                    image_url=None)
        db.session.add(self.u2)
        db.session.commit()

        new_msg = Message(text="A test message", user_id=self.u2.id)
        db.session.add(new_msg)
        db.session.commit()
        self.message_id = new_msg.id 

    def tearDown(self):
        """Clean up any fouled transaction."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_add_message(self):
        """Can use add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with app.app_context():
            with self.client as c:
                with c.session_transaction() as sess:
                    sess[CURR_USER_KEY] = self.u1.id

                # Now, that session setting is saved, so we can have
                # the rest of ours test

                resp = c.post("/messages/new", data={"text": "Hello"})

                # Make sure it redirects
                self.assertEqual(resp.status_code, 302)

                msg = Message.query.filter_by(text="Hello").first()
                self.assertIsNotNone(msg)
                self.assertEqual(msg.text, "Hello")

    def test_add_message_count(self):
        """Counts the new messages"""
        with app.app_context():
            initial_count = Message.query.count()

            with self.client as c:
                with c.session_transaction() as sess:
                    sess[CURR_USER_KEY] = self.u1.id

                c.post("/messages/new", data={"text": "Hello"})
                new_count = Message.query.count()

                # Ensure a message was added
                self.assertEqual(new_count, initial_count + 1)
    
    def test_show_method(self):
        """Test the showing the message route"""
        with app.app_context():
            new_msg = Message(text="godzilla", user_id=self.u1.id)
            db.session.add(new_msg)
            db.session.commit()
            with self.client as c:
                with c.session_transaction() as sess:
                    sess[CURR_USER_KEY] = self.u1.id
                    
            res = c.get(f"/messages/{new_msg.id}")
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn("godzilla", html)

    def test_msg_destroy_by_owner(self):
        """Tests the message owner can delete a message"""
        with app.app_context():
            with self.client as c:
                with c.session_transaction() as sess:
                    sess[CURR_USER_KEY] = self.u1.id

                
                res = c.post(f"/messages/{self.message_id}/delete", follow_redirects=True)

                self.assertEqual(res.status_code, 200)

                message = Message.query.get(self.message_id)
                self.assertIsNone(message)
   
    def test_message_delete_unauthorized(self):
        """Test message deletion attempt by a user who is not the owner"""
        with app.app_context():
            other_user = User.signup(
                    username="unauthorizeduser",
                    email="uniqueemail@test.com",
                    password="password",
                    image_url=None
                )
            db.session.add(other_user)
            db.session.commit()
            with self.client as c:
                    ##  below simulates LOGIN
                with c.session_transaction() as sess:
                    sess[CURR_USER_KEY] = other_user.id

                    res = c.post(f"/messages/{self.message_id}/delete", follow_redirects=True)
                    self.assertEqual(res.status_code, 200)

                    message = Message.query.get(self.message_id)
                    self.assertIsNotNone(message)

    def test_like_message(self):
        """Test liking a message"""
        with app.app_context():
            with self.client as c:
                with c.session_transaction() as sess:
                    sess[CURR_USER_KEY] = self.u1.id 

            res = c.post(f'/users/add_like/{self.message_id}', follow_redirects=True)
            self.assertEqual(res.status_code, 200) 

            # Ensure the like was added for the correct user and message
            like = Likes.query.filter_by(user_id=self.u1.id, message_id=self.message_id).first()
            self.assertIsNotNone(like)


    def test_unlike_message(self):
        """Test unliking a message."""
        # First, add a like to set up the test
        with app.app_context():
            like = Likes(user_id=self.u1.id, message_id=self.message_id)
            db.session.add(like)
            db.session.commit()

            with self.client as c:
                with c.session_transaction() as sess:
                    sess[CURR_USER_KEY] = self.u1.id 

                res = c.post(f'/users/add_like/{self.message_id}')
                self.assertEqual(res.status_code, 302)

                like = Likes.query.filter_by(user_id=self.u1.id, message_id=self.message_id).first()
                self.assertIsNone(like)
    
    def test_like_message_unauthorized(self):
        """Test liking a message without being logged in."""
        with app.app_context():
            with self.client as c:
                res = c.get(f"/users/{self.u1.id}/likes", follow_redirects=True)
                html = res.get_data(as_text=True)
            self.assertEqual(res.status_code, 200)
            self.assertIn("Access unauthorized.",html)
            self.assertNotIn("A liked message",html)