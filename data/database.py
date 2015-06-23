import os
import sys
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Float, String, DateTime, Table, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql.expression import ClauseElement

from kivy.uix.image import AsyncImage
from kivy.loader import Loader
from kivy.loader import Loader
from sqlalchemy.types import TypeDecorator, VARCHAR
import json
Base = declarative_base()


class JSONEncodedDict(TypeDecorator):
    """Represents an immutable structure as a json-encoded string.

    Usage::

        JSONEncodedDict(255)

    """

    impl = VARCHAR

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)

        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value

class UniqueMixin(object):
    @classmethod
    def unique_hash(cls, *arg, **kw):
        raise NotImplementedError()

    @classmethod
    def unique_filter(cls, query, *arg, **kw):
        raise NotImplementedError()

    @classmethod
    def as_unique(cls, session, *arg, **kw):
        return _unique(
                    session,
                    cls,
                    cls.unique_hash,
                    cls.unique_filter,
                    cls,
                    arg, kw
               )

class FavFolder(Base):
    __tablename__ = 'fav_folder'
    # Here we define columns for the table address.
    # Notice that each column is also a normal Python instance attribute.
    id = Column(Integer, primary_key=True)
    name = Column(String(250))



class FavCollection(UniqueMixin, Base):
    __tablename__ = 'fav_collection'
    # Here we define columns for the table address.
    # Notice that each column is also a normal Python instance attribute.
    id = Column(Integer, primary_key=True)
    name = Column(String(250))
    icon = Column(String(250),nullable=True)
    sort_by = Column(String(250),nullable=True)
    fav_folder = relationship(
        FavFolder,
        secondary='favcollection_folder_link'
    )
    fav_items = relationship(
        'FavItem',
        secondary='favitem_collection_link',
        backref='fav_collection'

    )
    @classmethod
    def unique_hash(cls, name):
        return name

    @classmethod
    def unique_filter(cls, query, name):
        return query.filter(FavCollection.name == name)


class FavItem(UniqueMixin, Base):
    __tablename__ = 'fav_item'
    # Here we define columns for the table person
    # Notice that each column is also a normal Python instance attribute.
    # id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=True)
    comic_id_number = Column(Integer, primary_key=True)
    icon = Column(String(250),nullable=True)
    comic_json = Column(JSONEncodedDict(255),nullable=False)
    fav_folder = relationship(
        FavFolder,
        secondary='favitem_folder_link'
    )

    # fav_collection = relationship(
    #     FavCollection,
    #     secondary='favitem_collection_link'
    #
    # )
    @classmethod
    def unique_hash(cls, comic_id_number):
        return comic_id_number

    @classmethod
    def unique_filter(cls, query, comic_id_number):
        return query.filter(FavItem.comic_id_number == comic_id_number)


class FavItemCollectioLink(Base):
    __tablename__ = 'favitem_collection_link'
    fav_item_id = Column(Integer,ForeignKey('fav_item.comic_id_number'), primary_key=True)
    fav_collection_id = Column(Integer, ForeignKey('fav_collection.id'), primary_key=True)

class FavItemFolderLink(Base):
    __tablename__ = 'favitem_folder_link'
    fav_item_id = Column(Integer, ForeignKey('fav_item.comic_id_number'), primary_key=True)
    fav_folder_id = Column(Integer, ForeignKey('fav_folder.id'), primary_key=True)

class FavCollectionFolderLink(Base):
    __tablename__ = 'favcollection_folder_link'
    fav_collection_id = Column(Integer, ForeignKey('fav_collection.id'), primary_key=True)
    fav_folder_id = Column(Integer, ForeignKey('fav_folder.id'), primary_key=True)


class DataManager():
    def __init__(self):
        self.dbfile =  "data/dcsfav.sqlite"
    def delete(self):
        if os.path.exists( self.dbfile ):
            os.unlink( self.dbfile )

    def create(self):

        self.engine = create_engine('sqlite:///'+ self.dbfile, echo=False)

        session_factory = sessionmaker(bind=self.engine)
        self.Session = scoped_session(session_factory)

        Base.metadata.create_all(self.engine)
        session = self.Session()
        results = session.query(FavCollection).first()
        if results is None:
            new_collection = FavCollection(name='Unsorted Comics',sort_by='Pub Date')
            session.add(new_collection)
            session.commit()

from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql.expression import ClauseElement


def get_or_create(session,model, defaults={}, **kwargs):

    query = session.query(model).filter_by(**kwargs)
    instance = query.first()
    if instance:
        return instance, False
    else:
        session.begin(nested=True) #savepoint
        try:
            params = dict((k, v) for k, v in kwargs.iteritems() if not isinstance(v, ClauseElement))
            params.update(defaults)
            instance = model(**params)
            session.add(instance)
            session.commit()
            return instance, True
        except IntegrityError:
            import traceback
            traceback.print_exc()
            session.rollback()
            instance = query.one()
            return instance, False


def get_one_or_create(session,
                      model,
                      create_method='',
                      create_method_kwargs=None,
                      **kwargs):
    try:
        return session.query(model).filter_by(**kwargs).one(), True
    except NoResultFound:
        kwargs.update(create_method_kwargs or {})
        created = getattr(model, create_method, model)(**kwargs)
        try:
            session.add(created)
            session.commit()
            return created, False
        except IntegrityError:
            session.rollback()
            return session.query(model).filter_by(**kwargs).one(), True




def _unique(session, cls, hashfunc, queryfunc, constructor, arg, kw):
    cache = getattr(session, '_unique_cache', None)
    if cache is None:
        session._unique_cache = cache = {}

    key = (cls, hashfunc(*arg, **kw))
    if key in cache:
        return cache[key]
    else:
        with session.no_autoflush:
            q = session.query(cls)
            q = queryfunc(q, *arg, **kw)
            obj = q.first()
            if not obj:
                obj = constructor(*arg, **kw)
                session.add(obj)
        cache[key] = obj
        return obj


