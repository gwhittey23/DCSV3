import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String,PickleType
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from kivy.uix.image import AsyncImage
from kivy.loader import Loader
from kivy.loader import Loader

Base = declarative_base()

class FavItem(Base):
    __tablename__ = 'fav_item'
    # Here we define columns for the table person
    # Notice that each column is also a normal Python instance attribute.
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    comic_id = Column(Integer,nullable=True)

    cover_image = Column(PickleType)

class FavCollection(Base):
    __tablename__ = 'address'
    # Here we define columns for the table address.
    # Notice that each column is also a normal Python instance attribute.
    id = Column(Integer, primary_key=True)
    name = Column(String(250))
    s_type = Column(String(250),nullable=True)

def _image_loaded(self, proxyImage):
    if proxyImage.image.texture:
        self.image.texture = proxyImage.image.texture

# Create an engine that stores data in the local directory's
# sqlalchemy_example.db file.
engine = create_engine('sqlite:///dcsfav.db')

# Create all tables in the engine. This is equivalent to "Create Table"
# statements in raw SQL.
Base.metadata.create_all(engine)





