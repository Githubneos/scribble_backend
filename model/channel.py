# channel.py
from sqlite3 import IntegrityError
from sqlalchemy import Text, JSON
from __init__ import app, db
from model.group import Group
class Channel(db.Model):
    """
    Channel Model
    The Channel class represents a channel within a group, with customizable attributes.
    Attributes:
        id (db.Column): The primary key, an integer representing the unique identifier for the channel.
        _name (db.Column): A string representing the name of the channel.
        _attributes (db.Column): A JSON blob representing customizable attributes for the channel.
        _group_id (db.Column): An integer representing the group to which the channel belongs.
    """
    __tablename__ = 'channels'
    id = db.Column(db.Integer, primary_key=True)
    _name = db.Column(db.String(255), nullable=False)
    _attributes = db.Column(JSON, nullable=True)
    _group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=False)
    posts = db.relationship('Post', backref='channel', lazy=True)
    def __init__(self, name, group_id, attributes=None):
        """
        Constructor, 1st step in object creation.
        Args:
            name (str): The name of the channel.
            group_id (int): The group to which the channel belongs.
            attributes (dict, optional): Customizable attributes for the channel. Defaults to None.
        """
        self._name = name
        self._group_id = group_id
        self._attributes = attributes or {}
    def __repr__(self):
        """
        The __repr__ method is a special method used to represent the object in a string format.
        Called by the repr() built-in function.
        Returns:
            str: A text representation of how to create the object.
        """
        return f"Channel(id={self.id}, name={self._name}, group_id={self._group_id}, attributes={self._attributes})"
    @property
    def name(self):
        """
        Gets the channel's name.
        Returns:
            str: The channel's name.
        """
        return self._name
    def create(self):
        """
        The create method adds the object to the database and commits the transaction.
        Uses:
            The db ORM methods to add and commit the transaction.
        Raises:
            Exception: An error occurred when adding the object to the database.
        """
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e
    def read(self):
        """
        The read method retrieves the object data from the object's attributes and returns it as a dictionary.
        Returns:
            dict: A dictionary containing the channel data.
        """
        return {
            'id': self.id,
            'name': self._name,
            'attributes': self._attributes,
            'group_id': self._group_id
        }
    def update(self, inputs):
        """
        Updates the channel object with new data.
        Args:
            inputs (dict): A dictionary containing the new data for the channel.
        Returns:
            Channel: The updated channel object, or None on error.
        """
        if not isinstance(inputs, dict):
            return self
        name = inputs.get("name", "")
        group_id = inputs.get("group_id", None)
        # Update table with new data
        if name:
            self._name = name
        if group_id:
            self._group_id = group_id
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return None
        return self
    @staticmethod
    def restore(data):
        channels = {}
        for channel_data in data:
            _ = channel_data.pop('id', None)  # Remove 'id' from channel_data
            name = channel_data.get("name", None)
            channel = Channel.query.filter_by(_name=name).first()
            if channel:
                channel.update(channel_data)
            else:
                channel = Channel(**channel_data)
                channel.create()
        return channels
def initChannels():
    """
    The initChannels function creates the Channel table and adds tester data to the table.
    Uses:
        The db ORM methods to create the table.
    Instantiates:
        Channel objects with tester data.
    Raises:
        IntegrityError: An error occurred when adding the tester data to the table.
    """
    with app.app_context():
        """Create database and tables"""
        db.create_all()
        """Tester data for table"""
        # Home Page Channels
        general = Group.query.filter_by(_name='General').first()
        support = Group.query.filter_by(_name='Support').first()
        home_page_channels = [
            Channel(name='Announcements', group_id=general.id),
            Channel(name='Events', group_id=general.id),
            Channel(name='FAQ', group_id=support.id),
            Channel(name='Help Desk', group_id=support.id)
        ]
        channels = home_page_channels
        for channel in channels:
            try:
                db.session.add(channel)
                db.session.commit()
                print(f"Record created: {repr(channel)}")
            except IntegrityError:
                db.session.rollback()
                print(f"Records exist, duplicate email, or error: {channel.name}")