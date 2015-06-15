import os
import sys
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Float, String, DateTime, Table, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from kivy.uix.image import AsyncImage
from kivy.loader import Loader
from kivy.loader import Loader

Base = declarative_base()


class FavFolder(Base):
    __tablename__ = 'fav_folder'
    # Here we define columns for the table address.
    # Notice that each column is also a normal Python instance attribute.
    id = Column(Integer, primary_key=True)
    name = Column(String(250))



class FavCollection(Base):
    __tablename__ = 'fav_collection'
    # Here we define columns for the table address.
    # Notice that each column is also a normal Python instance attribute.
    id = Column(Integer, primary_key=True)
    name = Column(String(250))
    icon = Column(String(250),nullable=True)
    fav_folder = relationship(
        FavFolder,
        secondary='favcollection_folder_link'
    )

class FavItem(Base):
    __tablename__ = 'fav_item'
    # Here we define columns for the table person
    # Notice that each column is also a normal Python instance attribute.
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    comic_id_number = Column(Integer,nullable=True)
    icon = Column(String(250),nullable=True)
    fav_folder = relationship(
        FavFolder,
        secondary='favitem_folder_link'
    )

class FavItemFolderLink(Base):
    __tablename__ = 'favitem_folder_link'
    fav_item_id = Column(Integer, ForeignKey('fav_item.id'), primary_key=True)
    fav_folder_id = Column(Integer, ForeignKey('fav_folder.id'), primary_key=True)

class FavCollectionFolderLink(Base):
    __tablename__ = 'favcollection_folder_link'
    fav_collection_id = Column(Integer, ForeignKey('fav_collection.id'), primary_key=True)
    fav_folder_id = Column(Integer, ForeignKey('fav_folder.id'), primary_key=True)


class DataManager():
    def __init__(self):
        self.dbfile =  "data/dcsfav.db"
        print self.dbfile
    def delete(self):
        if os.path.exists( self.dbfile ):
            os.unlink( self.dbfile )

    def create(self):

        self.engine = create_engine('sqlite:///'+ self.dbfile, echo=False)

        session_factory = sessionmaker(bind=self.engine)
        self.Session = scoped_session(session_factory)

        Base.metadata.create_all(self.engine)









