# post.py
import logging
from sqlite3 import IntegrityError
from sqlalchemy import Text, JSON
from sqlalchemy.exc import IntegrityError
from __init__ import app, db
from model.user import User
from model.channel import Channel
class Post(db.Model):
    # creates the post in discussion channel
    """
    Post Model
    The Post class represents an individual contribution or discussion within a channel.
    Attributes:
        id (db.Column): The primary key, an integer representing the unique identifier for the post.
        _title (db.Column): A string representing the title of the post.
        _comment (db.Column): A string representing the comment of the post.
        _content (db.Column): A JSON blob representing the content of the post.
        _user_id (db.Column): An integer representing the user who created the post.
        _channel_id (db.Column): An integer representing the channel to which the post belongs.
    """
    # defines table name and columns
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    _title = db.Column(db.String(255), nullable=False)
    _comment = db.Column(db.String(255), nullable=False)
    _content = db.Column(JSON, nullable=False)
    _user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    _channel_id = db.Column(db.Integer, db.ForeignKey('channels.id'), nullable=False)
    def __init__(self, title, comment, user_id=None, channel_id=None, content={}, user_name=None, channel_name=None):
        """
        Constructor, 1st step in object creation.
        Args:
            title (str): The title of the post.
            comment (str): The comment of the post.
            user_id (int): The user who created the post.
            channel_id (int): The channel to which the post belongs.
            content (dict): The content of the post.
        """
        self._title = title
        self._comment = comment
        self._user_id = user_id
        self._channel_id = channel_id
        self._content = content
        # initializes a new post object
    def __repr__(self):
        """
        The __repr__ method is a special method used to represent the object in a string format.
        Called by the repr(post) built-in function, where post is an instance of the Post class.
        Returns:
            str: A text representation of how to create the object.
        """
        return f"Post(id={self.id}, title={self._title}, comment={self._comment}, content={self._content}, user_id={self._user_id}, channel_id={self._channel_id})"
    def create(self):
        """
        Creates a new post in the database.
        Returns:
            Post: The created post object, or None on error.
        """
        try:
            db.session.add(self)
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            logging.warning(f"IntegrityError: Could not create post with title '{self._title}' due to {str(e)}.")
            return None
        return self
    #  adds the post object to commit the transaction
    def read(self):
        """
        The read method retrieves the object data from the object's attributes and returns it as a dictionary.
        Uses:
            The Channel.query and User.query methods to retrieve the channel and user objects.
        Returns:
            dict: A dictionary containing the post data, including user and channel names.
        """
        user = User.query.get(self._user_id)
        channel = Channel.query.get(self._channel_id)
        data = {
            "id": self.id,
            "title": self._title,
            "comment": self._comment,
            "content": self._content,
            "user_name": user.name if user else None,
            "channel_name": channel.name if channel else None
        }
        return data
    def update(self, data):
        """
        Updates the post object with new data.
        Args:
            data (dict): A dictionary containing the new data for the post.
        Returns:
            Post: The updated post object, or None on error.
        """
        for key, value in data.items():
            setattr(self, key, value)
        db.session.commit()
        return self
    # update and delete commands
    def delete(self):
        """
        The delete method removes the object from the database and commits the transaction.
        Uses:
            The db ORM methods to delete and commit the transaction.
        Raises:
            Exception: An error occurred when deleting the object from the database.
        """
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e
    @staticmethod
    def restore(data):
        for post_data in data:
            _ = post_data.pop('id', None)  # Remove 'id' from post_data
            title = post_data.get("title", None)
            post = Post.query.filter_by(_title=title).first()
            if post:
                post.update(post_data)
            else:
                post = Post(**post_data)
                post.update(post_data)
                post.create()
                # restores posts from list of dictionaries
def initPosts():
    """
    The initPosts function creates the Post table and adds tester data to the table.
    Uses:
        The db ORM methods to create the table.
    Instantiates:
        Post objects with tester data.
    Raises:
        IntegrityError: An error occurred when adding the tester data to the table.
    """
    with app.app_context():
        """Create database and tables"""
        db.create_all()
        """Tester data for table"""
        posts = [
            Post(title='Added Group and Channel Select', comment='The Home Page has a Section, on this page we can select Group and Channel to allow blog filtering', content={'type': 'announcement'}, user_id=1, channel_id=1),
            Post(title='JSON content saving through content"field in database', comment='You could add other dialogs to a post that would allow custom data or even storing reference to uploaded images.', content={'type': 'announcement'}, user_id=1, channel_id=1),
            Post(title='Allows Post by different Users', comment='Different users seeing content is a key concept in social media.', content={'type': 'announcement'}, user_id=2, channel_id=1),
        ]
        for post in posts:
            try:
                post.create()
                print(f"Record created: {repr(post)}")
            except IntegrityError:
                '''fails with bad or duplicate data'''
                db.session.remove()
                print(f"Records exist, duplicate email, or error: {post._title}")










