"""User view tests"""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_user_views.py

import os
from unittest import TestCase
from flask import session
from models import db, connect_db, Message, User, Likes
from sqlalchemy.exc import IntegrityError

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

class UserViewTestCase(TestCase):
    """Tests for user related routes"""
    def setUp(self):
        """Create test client, add sample data."""
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()

        User.query.delete()
        Message.query.delete()

        self.u1 = User.signup(username="testpotato",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)
       
        self.u2 = User.signup(username="testuser2",
                                    email="test2@test.com",
                                    password="testuser2",
                                    image_url=None)
        db.session.add_all([self.u1, self.u2])

        db.session.commit()

        self.msg = Message(text="A liked message", user_id=self.u2.id)
        db.session.add(self.msg)
        db.session.commit()

        like = Likes(user_id=self.u1.id, message_id=self.msg.id)
        db.session.add(like)
        db.session.commit()

    
    def tearDown(self):
        """Clean up any fouled transaction."""
        db.session.remove()
        db.drop_all()

    def test_signup(self):
        """Test the signup route"""
        with app.app_context():
            with self.client as c:
                res = c.post('/signup', data=dict(
                        username="newuser",
                        email="newuser@test.com",
                        password="newpassword",
                        image_url=""
                        ), follow_redirects=True)
            html = res.get_data(as_text=True)
            
            self.assertEqual(res.status_code, 200)
            self.assertIn('value="newuser@test.com"', html)

            user = User.query.filter_by(email="newuser@test.com").all()
            self.assertIsNotNone(user)
            
    def test_login(self):
        """Test the login route."""
        with self.client as c:
            res = c.post('/login', data=dict(
                    username="testpotato",
                    password="testuser"
                ), follow_redirects=True)
            user = User.query.first()
            with c.session_transaction() as sess:
                self.assertIn('curr_user', sess) 

            self.assertEqual(res.status_code, 200)
            self.assertIn('<p>@testpotato</p>', res.get_data(as_text=True))

    def test_logout(self):
        """Test the logout route."""
        with self.client as c:
            with c.session_transaction() as sess:
                sess['curr_user'] = self.u1.id
                res = c.get('/logout', follow_redirects=True)

                self.assertEqual(res.status_code, 200)
                self.assertIn(' <li><a href="/signup">Sign up</a></li>', res.get_data(as_text=True))

                with c.session_transaction() as sess:
                    self.assertNotIn('curr_user', sess)

    def test_list_users(self):
        """Tests the list_users route returns a list of users"""
        with app.app_context():
            with self.client as c:
                res = c.get('/users')
                html = res.get_data(as_text=True)

                self.assertEqual(res.status_code, 200)

                self.assertIn("testpotato",html)
                self.assertIn("testuser2",html)

    def test_show_users(self):
        """Tests the user profile page"""
        with app.app_context():
            with self.client as c:
                res = c.get(f"/users/{self.u1.id}")
                html = res.get_data(as_text=True)

                self.assertEqual(res.status_code, 200)

                self.assertIn("testpotato",html)
                self.assertIn('<h4 id="sidebar-username">@testpotato</h4>',html)
    
    def test_show_following_logged_in(self):
        """Ensure following page is 
        accessible when logged in."""
        with app.app_context():
            with self.client as c:
                with c.session_transaction() as sess:
                    sess[CURR_USER_KEY] = self.u1.id
                u1 = User.query.get(self.u1.id)
                u2 = User.query.get(self.u2.id)

                u1.following.append(u2)
                db.session.commit()

            res = c.get(f"/users/{self.u1.id}/following")
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('<p>@testuser2</p>', html)

    def test_show_following_logged_out(self):
        """tests following page is not 
        accessible when logged out."""
        with app.app_context():
            with self.client as c:
                res = self.client.get(f'/users/{self.u2.id}/following', follow_redirects=True)
                html = res.get_data(as_text=True)

                self.assertEqual(res.status_code, 200)
                self.assertIn("Access unauthorized", html)

    def test_follower_page_logged_in(self):
        """When logged in, can you see the follower pages for any user?"""
        with app.app_context():
            with self.client as c:
                res = self.client.get(f'/users/{self.u2.id}/followers', follow_redirects=True)

    def test_follower_page_logged_out(self):
        """When logged out, are you disallowed from 
        visiting a user’s followers pages?"""
        with app.app_context():
            with self.client as c:
                with c.session_transaction() as sess:
                    sess[CURR_USER_KEY] = self.u1.id
                u1 = User.query.get(self.u1.id)
                u2 = User.query.get(self.u2.id)
                u2.followers.append(u1)
                db.session.commit()

                res = c.get(f'/users/{self.u2.id}/followers', follow_redirects=True)
                html = res.get_data(as_text=True)

                self.assertEqual(res.status_code, 200)
                self.assertIn('@testpotato', html)
    
    def test_edit_profile(self):
        """Ensure the edit profile routes work"""
        with app.app_context():
            with self.client as c:
                with c.session_transaction() as sess:
                    sess[CURR_USER_KEY] = self.u1.id
                res = c.post('/users/profile', 
                               data={"username": "updatedpotatoking", 
                                     "email": "updated@test.com", 
                                     "password": "testuser"}, follow_redirects=True)
          
                html = res.get_data(as_text=True)

                self.assertEqual(res.status_code, 200)
                self.assertIn("User Updated!", html)

                user = User.query.filter_by(id=self.u1.id).first()
                self.assertEqual(user.username, 'updatedpotatoking')
                self.assertEqual(user.email, 'updated@test.com')

    def test_delete_user(self):
        """Tests the deleting a user permanently removes them"""
        with app.app_context():
            with self.client as c:
                with c.session_transaction() as sess:
                    sess[CURR_USER_KEY] = self.u1.id
                res = c.post("/users/delete", follow_redirects=True)
                html = res.get_data(as_text=True)

                self.assertEqual(res.status_code, 200)
                self.assertIn("Sign up", html)

                user = User.query.filter_by(id=self.u1.id).first()
                self.assertIsNone(user)