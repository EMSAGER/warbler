#  def setUp(self):
#         """Create test client, add sample data."""
#         self.client = app.test_client()
#         self.app_context = app.app_context()
#         self.app_context.push()
#         db.create_all()

#         User.query.delete()
#         Message.query.delete()


#         self.u1 = User.signup(username="testuser",
#                                     email="test@test.com",
#                                     password="testuser",
#                                     image_url=None)
#         db.session.add(self.u1)
#         self.u2 = User.signup(username="testuser2",
#                                     email="test2@test.com",
#                                     password="testuser2",
#                                     image_url=None)
#         db.session.add(self.u2)
#         db.session.commit()
    
#     def tearDown(self):
#         """Clean up any fouled transaction."""
#         db.session.remove()
#         db.drop_all()

#     def login(self, username):
#         """Log in a user for testing"""
#         with self.client.session_transaction() as sess:
#             sess['CURR_USER_KEY'] = self.u1.id if username == 'testuser' else self.u2.id
#             sess.modified = True

#     def logout(self):
#         """Log out of the current user"""
#         with self.client.session_transaction() as sess:
#             del sess['CURR_USER_KEY']


# def test_follower_pages_logged_in(self):
#         """Test if a logged in user can see the 
#         follower/following pages from any user"""
#         with app.app_context():
#             with self.client as c:
                

                
#                 # self.assertIn('@testuser', html)

#                 # res = c.get(f'/users/{self.u1.id}/following')
#                 # self.assertEqual(res.status_code, 200)
#                 # self.assertIn('<p>@{{ followed_user.username }}</p>', html)
    
#     def test_is_following_pages_logged_in(self):
#         """Test if a logged in user can see the 
#         follower/following pages from any user"""
#         with app.app_context():
#             with self.client as c:
#                 u1 = User.query.get(self.u1.id)
#                 u2 = User.query.get(self.u2.id)

#                 u1.following.append(u2)
#                 db.session.commit()

#                 self.login('testuser')
#                 res = c.get(f'/users/{self.u1.id}/following')
#                 # self.assertIn('@testuser', html)

#                 # res = c.get(f'/users/{self.u1.id}/following')
#                 # self.assertEqual(res.status_code, 200)
#                 # self.assertIn('<p>@{{ followed_user.username }}</p>', html)