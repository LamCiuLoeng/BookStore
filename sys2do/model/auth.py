# -*- coding: utf-8 -*-
import os
from datetime import datetime as dt
import sys
try:
    from hashlib import sha1
except ImportError:
    sys.exit('ImportError: No module named hashlib\n'
             'If you are on python2.4 this library is not part of python. '
             'Please install it. Example: easy_install hashlib')

from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Unicode, Integer, DateTime
from sqlalchemy.orm import relation, synonym

from sys2do.model import DeclarativeBase, metadata, DBSession

__all__ = ['User', 'Group', 'Permission', 'SysMixin']

def getUserID():
#    return request.identity["user"].user_id
    return None

class SysMixin(object):
    create_time = Column(DateTime, default = dt.now)
    create_by_id = Column(Integer, default = getUserID)
    update_time = Column(DateTime, default = dt.now, onupdate = dt.now)
    update_by_id = Column(Integer, default = getUserID, onupdate = getUserID)
    active = Column(Integer, default = 0) # 0 is active ,1 is inactive

    @property
    def create_by(self):
        return DBSession.query(User).get(self.create_by_id)

    @property
    def update_by(self):
        return DBSession.query(User).get(self.update_by_id)

    def populate(self):
        return {}

    @classmethod
    def save_new(clz, handler):
        pass


    @classmethod
    def save_update(clz, id, handler):
        pass


#{ Association tables


# This is the association table for the many-to-many relationship between
# groups and permissions. This is required by repoze.what.
group_permission_table = Table('group_permission', metadata,
    Column('group_id', Integer, ForeignKey('group.id',
        onupdate = "CASCADE", ondelete = "CASCADE"), primary_key = True),
    Column('permission_id', Integer, ForeignKey('permission.id',
        onupdate = "CASCADE", ondelete = "CASCADE"), primary_key = True)
)

# This is the association table for the many-to-many relationship between
# groups and members - this is, the memberships. It's required by repoze.what.
user_group_table = Table('user_group', metadata,
    Column('user_id', Integer, ForeignKey('user.id',
        onupdate = "CASCADE", ondelete = "CASCADE"), primary_key = True),
    Column('group_id', Integer, ForeignKey('group.id',
        onupdate = "CASCADE", ondelete = "CASCADE"), primary_key = True)
)


#{ The auth* model itself


class Group(DeclarativeBase, SysMixin):
    __tablename__ = 'group'

    id = Column(Integer, autoincrement = True, primary_key = True)
    group_name = Column(Unicode(100), unique = True, nullable = False)
    display_name = Column(Unicode(255))
    users = relation('User', secondary = user_group_table, backref = 'groups')

    def __repr__(self):
        return self.display_name or self.group_name

    def __unicode__(self):
        return self.display_name or self.group_name


# The 'info' argument we're passing to the email_address and password columns
# contain metadata that Rum (http://python-rum.org/) can use generate an
# admin interface for your models.
class User(DeclarativeBase, SysMixin):

    __tablename__ = 'user'

    id = Column(Integer, autoincrement = True, primary_key = True)
    user_name = Column(Unicode(100), unique = True, nullable = False)
    email_address = Column(Unicode(255), nullable = True)
    display_name = Column(Unicode(255))
    password = Column('password', Unicode(80))

    def __repr__(self):
        return '<User: email="%s", display name="%s">' % (
                self.email_address, self.display_name)

    def __unicode__(self):
        return self.display_name or self.user_name

    @property
    def permissions(self):
        """Return a set of strings for the permissions granted."""
        perms = set()
        for g in self.groups:
            perms = perms | set(g.permissions)
        return perms

    @classmethod
    def by_email_address(cls, email):
        """Return the user object whose email address is ``email``."""
        return DBSession.query(cls).filter(cls.email_address == email).first()

    @classmethod
    def by_user_name(cls, username):
        """Return the user object whose user name is ``username``."""
        return DBSession.query(cls).filter(cls.user_name == username).first()

    def validate_password(self, password):
        return self.password == password

    @classmethod
    def identify(cls, value):
        return DBSession.query(cls).filter(cls.user_name.match(value)).one()

    def populate(self):
        return {
                "id" : self.id,
                "user_name" : self.user_name,
                "email_address" : self.email_address,
                "display_name" : self.display_name,
                }

    @classmethod
    def save_new(clz, handler):
        params = {
                  "user_name" : handler.get_argument("user_name", None),
                  "email_address" : handler.get_argument("email_address", None),
                  "display_name" : handler.get_argument("display_name", None),
                  "password" : handler.get_argument("password", None),
                  }
        record = clz(**params)
        DBSession.add(record)
        return record

    @classmethod
    def save_update(clz, id, handler):
        record = DBSession.query(clz).get(id)
        for f in ["user_name", "email_address", "display_name", "password"]:
            setattr(record, f, handler.get_argument(f, None))
        return record


class Permission(DeclarativeBase, SysMixin):
    __tablename__ = 'permission'

    id = Column(Integer, autoincrement = True, primary_key = True)
    permission_name = Column(Unicode(16), unique = True, nullable = False)
    description = Column(Unicode(255))
    groups = relation(Group, secondary = group_permission_table, backref = 'permissions')

    def __repr__(self):
        return '<Permission: name=%s>' % self.permission_name

    def __unicode__(self):
        return self.permission_name

