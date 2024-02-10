"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from models import db, User, Message, Follows, bcrypt
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash


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



class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client"""
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        hashed_pwd1 = bcrypt.generate_password_hash("password").decode('utf-8')
        hashed_pwd2 = bcrypt.generate_password_hash("password").decode('utf-8')

        self.u1 = User(
            email="test@test.com",
            username="testuser",
            password= hashed_pwd1
        )   

        self.u2 = User(
            email="test2@test.com",
            username="testuser2",
            password= hashed_pwd2
        )   
        db.session.add(self.u1)
        db.session.add(self.u2)
        db.session.commit()


    def tearDown(self):
        """Clean up any fouled transaction."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
                    
    def test_repr_method(self):
        """tests the repr method work"""
        with app.app_context():
            u1 = User.query.get(self.u1.id)
            self.assertEqual(repr(u1), f"<User #{u1.id}: {u1.username}, {u1.email}>")

    def test_is_following(self):
        """Does is_following successfully 
        detect when user1 is followed by user2?"""
        with app.app_context():
            u1 = User.query.get(self.u1.id)
            u2 = User.query.get(self.u2.id)

            u1.following.append(u2)
            db.session.commit()

            self.assertTrue(u1.is_following(u2))
            self.assertFalse(u2.is_following(u1))
    
    def test_is_followed_by(self):
        """Does is_followed_by successfully 
        detect when u1 is followed by u2?"""
        with app.app_context():
            u1 = User.query.get(self.u1.id)
            u2 = User.query.get(self.u2.id)

            u1.followers.append(u2)
            db.session.commit()

            self.assertTrue(u1.is_followed_by(u2))
            self.assertFalse(u2.is_followed_by(u1))

    def test_user_signup(self):
        """Tests if user.create will 
        create a new user"""
        with app.app_context():
            u_test = User.signup("testsignup", "testsignup@test.com", "password", None)
            uid = 99999
            u_test.id = uid
            db.session.commit()

            u_test = User.query.get(uid)
            self.assertIsNotNone(u_test)
            self.assertEqual(u_test.username, "testsignup")
            self.assertEqual(u_test.email, "testsignup@test.com")
                    ##since the password will be hashed and unknown, except for the first 4 digits.
            self.assertTrue(u_test.password.startswith("$2b$"))

    def test_invalid_user_signup(self):
         """Does User.create fail to create a new user 
         if any of the validations 
         (e.g. uniqueness, non-nullable fields) fail?"""
         with app.app_context():
            invalid = User.signup(None, "test3@test.com", "password", None)
            uid = 123456789
            invalid.id = uid
            with self.assertRaises(IntegrityError):
                db.session.commit()
    
    def test_valid_authentication(self):
        """Does User.authenticate successfully 
        return a user when given a valid username and password?"""
        with app.app_context():
            u = User.authenticate(self.u1.username, "password")
            self.assertIsNotNone(u)
            self.assertEqual(u.id, self.u1.id)

    
    def test_invalid_username(self):
        """Does User.authenticate fail to 
        return a user when the username is invalid?"""
        with app.app_context():
            self.assertFalse(User.authenticate("badusername", "password"))

    def test_wrong_password(self):
        """Does User.authenticate fail to 
        return a user when the password is invalid?"""
        with app.app_context():
            self.assertFalse(User.authenticate(self.u1.username, "badpassword"))